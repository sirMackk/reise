reise

For now, this is just a non-working exploration of making a DNS tunneler in Python 2.7.

My main structure is a proxy client running on localhost, accepting local http requests over TCP and forwarding them through UDP (DNS form in the future) to a remote proxy server. The proxy server recieves the packets and forwards them to the target over TCP, gets a reply and then returns the reply over UDP to the proxy client. Still experimenting with using sockets correctly at this stage.