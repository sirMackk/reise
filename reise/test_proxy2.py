#threading proxy using Queue

import threading
import socket
import Queue

import datetime
import time

tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp.bind(('127.0.0.1', 8080))
tcp.listen(10)

f = open('debug.txt', 'w')
now = datetime.datetime.now()
f.write('******************************************************')
f.write(now.strftime('%Y-%m-%d %H:%M'))
f.write('******************************************************')

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
            f.write('\n\n=====================================================\n')    
            buffer = msg.recv(8192)   
            f.write(buffer)
            print 'Buffer length: %d' % len(buffer)
            out = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            print 'outbound socket acquired, connecting...'
            out.connect((self.getIP(buffer), 80))
            print 'sending buffer to target'
            out.sendall(buffer)
            print 'receiving...'
            data = self.recv_data(out)
            f.write('++++++++++++++++++++++++++++++++++++++++++++++++++++++\n')
            f.write(data)
            out.close()
            print 'got reply, closing socket, sending back to localhost'
            msg.sendall(data)
            msg.close()

    def getIP(self, buffer):
        end = buffer.find('/n')
        host = buffer[:end].split()[1]
        
        end = host[7:].find('/')
        f.write('IPIPIPIPIPIP')
        f.write(host[7:(end+7)])
        f.write('IPIPIPIPIPIP')
        host_ip = socket.gethostbyname(host[7:(end+7)])
        print host + ' ' + host_ip

        return host_ip

    def recv_data(self, out):
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

clientPool = Queue.Queue()
for i in range(3):
    ClientThread().start()

for i in xrange(25):
    clientPool.put(tcp.accept())

tcp.close()
f.close()