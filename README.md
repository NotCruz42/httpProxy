# httpProxy
Topic 2 - httpProxy
This topic focuses on developing an http proxy that passes requests and data between web clients and web servers. Normally your web client, e.g., your web browser, communicates directly with a remote web server. 
However, in some circumstances it may be useful to introduce an intermediate entity called a proxy. Conceptually, the proxy sits between the client and the server. 
In the simplest case, instead of sending requests directly to a server, the client sends all of its requests to the proxy. The proxy then opens a connection to the server, and passes on the client's request. 
The proxy receives the reply from the server, and then sends that reply back to the client. Notice that the proxy is essentially acting like both an HTTP client (to the remote server) and an HTTP server (to the initial client). 
Your task is to build an http proxy capable of accepting HTTP requests, forwarding requests to remote (origin) servers, and returning response data to a client.
