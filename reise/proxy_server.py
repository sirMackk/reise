import socket
from sys import exit

udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp.bind((socket.gethostbyname(socket.getfqdn()), 9081))

out = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print 'setup complete'

for i in xrange(3):
    #recieving request from client
    data, addr = udp.recvfrom(2048)
    print 'got request from host'
    print 'getting target ip address'
    print data
    print data.split('\n')[0].split()[1].split('/')[2]
    try:
        remote_ip = socket.gethostbyname(data.split('\n')[0].split()[1].split('/')[2])
    except:
        udp.close
        print 'Errno 11004 or index range error'
        exit()
    #forwarding request to target

    #I assume there is an error in my model here. Maybe some tcp answers
    #require more than 1 2048 packet or buffer
    out.connect((remote_ip, 80))
    out.sendall(data)
    #getting data back
    reply = out.recv(2048)
    print reply
    out.close()
    #sending data back to client
    print 'replying to ', addr[0]
    udp.sendto(reply, (addr[0], 9080))
    print 'sent'

print 'shutting down'
udp.close()