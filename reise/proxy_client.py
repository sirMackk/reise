import socket
from sys import argv

script, ip = argv

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp.bind((socket.gethostbyname(socket.getfqdn()), 9080))
s.bind(('localhost', 8080))
print 'bind complete'
s.listen(2)
for i in xrange(3):
    print 'listening'
    #for i in xrange(5):
    #accepts connection from localhost
    conn, addr = s.accept()
    print 'accepting connection'
    #gets the data from it, http stuffs
    data = conn.recv(2048)
    print 'recieved data: %d' % len(data)
    #sends http stuffs using udp to remote host ip port 9081
    print 'sending by udp'
    udp.sendto(data, (ip, 9081))
    #obtains reply with http stuffs
    print 'waiting for udp reply'
    data, addr = udp.recvfrom(2048)
    #sends http stuff back to localhost
    print 'sending back on tcp localhost'
    conn.sendall(data)
    
conn.close()
s.close()
udp.close()