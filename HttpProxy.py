import socket
import threading
import sys
import errno
import os
import signal
import sem

DEFAULT_METHOD = "GET"
DEFAULT_PORT = "80"
DEFUALT_VERSION = "HTTP/1.0"
CONNECTION_CLOSE = "Connection: close"
INTERNAL_ERROR = "500 INTERNAL ERROR\n"
BACKLOG = 30
BUFFER_LENGTH = 2048
MAX_MESSAGE = 200000
MAX_CONCURRENT_USERS = 30

maxConcurrent = sem.Semaphore()

class ThreadArgs:
    def __init__(self, client_sock):
        self.clientSock = client_sock

def send_chunk(client_sock, buffer, buffer_length):
    bytes_sent = 0
    while bytes_sent < buffer_length:
        try:
            bytes_just_sent = client_sock.send(buffer[bytes_sent:])
            if bytes_just_sent == 0:
                raise RuntimeError("Socket connection broken")
            bytes_sent += bytes_just_sent
        except socket.error as e:
            if e.errno == errno.EPIPE:
                raise RuntimeError("Socket connection broken")
            else:
                raise
    return 0

def producer_consumer(client_sock, http_server_sock):
    while True:
        try:
            buffer = http_server_sock.recv(BUFFER_LENGTH)
            if not buffer:
                break
            send_chunk(client_sock, buffer, len(buffer))
        except socket.error as e:
            if e.errno == errno.EPIPE:
                break
            else:
                raise

def process_thread(args):
    telnet_sock = args.clientSock
    command = ""
    url = ""
    bytes_left = MAX_MESSAGE
    buffer = bytearray(bytes_left)
    while "\r\n\r\n" not in command and bytes_left:
        try:
            bytes_recv = telnet_sock.recv_into(buffer, bytes_left)
            if bytes_recv == 0:
                raise RuntimeError("Socket connection broken")
            bytes_left -= bytes_recv
            command += buffer.decode("utf-8")
        except socket.error as e:
            if e.errno == errno.EPIPE:
                raise RuntimeError("Socket connection broken")
            else:
                raise

    command = command.replace("\n", "")
    tokens = command.split()
    
    if len(tokens) < 3 or tokens[0] != "GET" or tokens[2] != "HTTP/1.0":
        send_chunk(telnet_sock, INTERNAL_ERROR.encode("utf-8"), len(INTERNAL_ERROR))
        telnet_sock.close()
        sem.post(maxConcurrent)
        return
    else:
        url = tokens[1]
        parts = url.split(":")
        host = parts[0]
        port = "80" if len(parts) == 1 else parts[1]
        path = "/" + "/".join(parts[1:]).split("/", 1)[1] if len(parts) > 1 else "/"
        
        try:
            web_server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            web_server_sock.connect((host, int(port)))
        except socket.error as e:
            send_chunk(telnet_sock, INTERNAL_ERROR.encode("utf-8"), len(INTERNAL_ERROR))
            telnet_sock.close()
            sem.post(maxConcurrent)
            return
        
        header = f"GET {path} HTTP/1.0\r\nHost: {host}\r\nConnection: close\r\n\r\n"
        try:
            web_server_sock.sendall(header.encode("utf-8"))
            producer_consumer(telnet_sock, web_server_sock)
            web_server_sock.close()
        except socket.error as e:
            send_chunk(telnet_sock, INTERNAL_ERROR.encode("utf-8"), len(INTERNAL_ERROR))
            telnet_sock.close()
        sem.post(maxConcurrent)
        telnet_sock.close()

def main(argv):
    if len(argv) != 2:
        sys.stderr.write("Usage: python script.py <port>\n")
        sys.exit(1)

    local_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serv_addr = ('', int(argv[1]))

    try:
        local_sock.bind(serv_addr)
        local_sock.listen(BACKLOG)
    except socket.error as e:
        sys.stderr.write("Socket error: {}\n".format(e))
        sys.exit(1)

    sem.init(maxConcurrent, 0, MAX_CONCURRENT_USERS)

    while True:
        sem.wait(maxConcurrent)
        try:
            client_sock, client_addr = local_sock.accept()
            thread_args = ThreadArgs(client_sock)
            thread = threading.Thread(target=process_thread, args=(thread_args,))
            thread.start()
        except socket.error as e:
            sys.stderr.write("Socket error: {}\n".format(e))
            sys.exit(1)

    sem.close(maxConcurrent)

if __name__ == "__main__":
    main(sys.argv)
