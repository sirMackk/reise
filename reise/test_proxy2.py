#threading proxy using Queue

import threading
import socket
import Queue

tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp.bind(('localhost', 8080))
tcp.listen(10)

class ClientThread(threading.Thread):
    # def __init__(self, queue):
        # self.msg = msg
        # self.addr = addr
        # super(ClientThread, self).__init__()

    def run(self):
        while 1:
            
            print '[starting thread]'
            try:
                item = clientPool.get(True, 10)
            except Queue.Empty:
                print 'EMPTY EMPTY'
                break
            print '[got item]'
            if item == None:
                print '[NONE]'
                break
            #print item
            msg, addr = item
            print msg, addr
            
            buffer = msg.recv(8192)   
            print 'Buffer length: %d' % len(buffer)
            out = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            print 'outbound socket acquired, connecting...'
            out.connect((self.getIP(buffer), 80))
            print 'sending buffer to target'
            out.sendall(buffer)
            print 'receiving...'
            reply = out.recv(65536)
            out.close()
            print 'got reply, closing socket, sending back to localhost'
            msg.sendall(reply)

    def getIP(self, buffer):
        end = buffer.find('/n')
        host = buffer[:end].split()[1]
        
        end = host[7:].find('/')
        host_ip = socket.gethostbyname(host[7:(end+7)])
        print host + ' ' + host_ip

        return host_ip

clientPool = Queue.Queue()
for i in range(3):
    ClientThread().start()

for i in xrange(5):
    clientPool.put(tcp.accept())

tcp.close()