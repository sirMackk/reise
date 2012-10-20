#threading proxy using Queue
#early stage

import threading
import socket
import Queue
import time
from sys import argv

tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp.bind(('127.0.0.1', 8080))
tcp.listen(10)
#included: client.py
#first experiment with a tcp localhost proxy coupled with a send/recv udp interface
#simple initial test work
#must work on client to make it into an internet facing proxy
#must also work out issues with threads


#TODO 
#- make this whole program a class, allowing for easy implementation 
#in other projects, including the project that's the purpose of this experiment.
#- initial testing shows that this script uses about 30% of the CPU, so it would
#be nice to think about optimizing it later. Maybe Cython?




#ClientThread class subclasses threading.Thread class
class ClientThread(threading.Thread):
    def run(self):
        while 1:
            
            print '[starting thread]'
            try:
                item = clientPool.get()
                #item = clientPool.get(True, 10)
            except Queue.Empty:
                print 'EMPTY EMPTY'
                break
            if item == None:
                print 'NONE'
                break
            msg, addr = item
            buffer = msg.recv(8192)   
            print 'Buffer length: %d' % len(buffer)
            out = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            #out.bind((socket.gethostbyname(socket.getfqdn()), 53))
            print 'outbound socket acquired, connecting...'
            print 'sending buffer to target'
            out.sendto(buffer, (target.split(':')[0], int(target.split(':')[1]))) 
            print 'receiving...'
            data = self.recv_udp(out)
            print 'got reply, closing socket, sending back to localhost'
            print data
            msg.sendall(data)
            msg.close()

    def getIP(self, buffer):
        end = buffer.find('/n')
        try:
            host = buffer[:end].split()[1]      
        except IndexError:
            print buffer
            print end
            exit()
        end = host[7:].find('/')
        host_ip = socket.gethostbyname(host[7:(end+7)])
        print host + ' ' + host_ip
        return host_ip

#This function is responsible for recieving ALL the data packets.
#I had a big issues with this earlier because I assumed that recv
#recieves all the tcp packets on a connection. This is not true, recv
#works similiarly to send. This function is to recv what sendall is to send.
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

    def recv_udp(self, udp):
        print 'engaging recv_udp function'
        udp.setblocking(0)
        data = []
        recv = ''
        start = time.time()

        while 1:
            if data and time.time() - start > 2:
                break
            elif time.time() - start > 4:
                break
            try:
                recv, addr = udp.recvfrom(2048)
                if recv:
                    print recv
                    data.append(recv)
                    start = time.time()
                else:
                    time.sleep(0.1)
            except:
                pass
        
        return ''.join(data)

script, target = argv

clientPool = Queue.Queue()
for i in range(1):
    ClientThread().start()
while 1:
    clientPool.put(tcp.accept())


tcp.close()
