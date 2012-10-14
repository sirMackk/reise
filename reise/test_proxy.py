#proxy testing

import socket
import time

def recv_data(out):
        out.setblocking(0)

        data = []
        recv = ''
        start = time.time()
    
        while 1:
            if data and time.time() - start > 2:
                break

            elif time.time() - start > 4:
                break

            try:
                recv = out.recv(8192)
                if recv:
                    data.append(recv)
                    start = time.time()
                else:
                    time.sleep(0.1)
            except:
                pass

        return ''.join(data)

def getIP(buffer):
    end = buffer.find('/n')
    host = buffer[:end].split()[1]
    
    end = host[7:].find('/')
    host_ip = socket.gethostbyname(host[7:(end+7)])
    print host + ' ' + host_ip

    return host_ip

local = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
local.bind(('localhost', 8080))
local.listen(5)
profile = time.time()

for i in xrange(20):
    print time.time() - profile
    print '=====%d=====\n' % i
    out = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    data, addr = local.accept()
    print 'Connection accepted'
    buffer = data.recv(4096)
    print 'data recieved'
    
  
    print 'sending buffer to remote host'
    out.connect((getIP(buffer), 80))
    out.sendall(buffer)
    print 'recieving data from remote host'
    reply = recv_data(out)
    out.close()
    print 'data recieved from remote host'

    data.sendall(reply)
    print 'data sent'

#Leaving this as a warning and small lesson.
#Using a quick and dirty time.time() profiling method, a single-thread solution
#to a proxy is simply really slow. A multithread solution is almost twice as fast.


local.close()    
print 'END'
    