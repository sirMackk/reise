#proxy testing

import socket

local = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

f = open('test.txt', 'a')
local.bind(('localhost', 8080))
local.listen(5)
for i in xrange(20):
    print '=====%d=====\n' % i
    out = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    data, addr = local.accept()
    print 'Connection accepted'
    buffer = data.recv(4096)
    print 'data recieved'
    f.write('=============================================================\n')
    f.write(buffer)
    end = buffer.find('\n')
    print len(buffer)
    #print buffer, end
    #print buffer[:end]
    try:
        host = buffer[:end].split()[1]
    except IndexError:
        print "BUFFER IS PROBABLY EMPTY"
    
    end = host[7:].find('/')

    print host[7:(end+7)]
    host_ip = socket.gethostbyname(host[7:(end+7)])
    #print 'remote host: ' + host + ' IP: ' + host_ip
    print 'sending buffer to remote host'
    out.connect((host_ip, 80))
    out.sendall(buffer)
    print 'recieving data from remote host'
    reply = out.recv(65536)
    out.close()
    print 'data recieved from remote host'
    f.write('+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++\n')
    f.write(reply)
    f.write('\n\n\n')
    print 'sending data back to local host'
    data.sendall(reply)
    print 'data sent'
local.close()
out.close()    
f.close()
    