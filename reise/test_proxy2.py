#threading proxy using Queue
#early stage

import threading
import socket
import Queue
import time

tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp.bind(('127.0.0.1', 8080))
tcp.listen(10)

#TODO 
#- make this whole program a class, allowing for easy implementation 
#in other projects, including the project that's the purpose of this experiment.
#- initial testing shows that this script uses about 30% of the CPU, so it would
#be nice to think about optimizing it later. Maybe Cython?




#ClientThread class subclasses threading.Thread class
class ClientThread(threading.Thread):
#run function called by .start()
    def run(self):
#infinite loop, means loop will try to .get items from queue until it breaks
#during the try..except or if item == None. Gotta experiment more with this part
        while 1:
            
            print '[starting thread]'
#try to get item from queue, if no - break loop and hopefully kill the thread
            try:
                item = clientPool.get()
                #item = clientPool.get(True, 10)
            except Queue.Empty:
                print 'EMPTY EMPTY'
                break
            if item == None:
                print 'NONE'
                break
#connection established
            msg, addr = item
#obtained, large 8192 byte buffer, might also use the recv_data method here
#to ensure all packets are recieved from hosts, although
#in a simple http session, it seems that the browser
#mostly produces fairly short GETs
            buffer = msg.recv(8192)   
            print 'Buffer length: %d' % len(buffer)
#create internet-facing tcp socket
            out = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            print 'outbound socket acquired, connecting...'
#connect with target host
            out.connect((self.getIP(buffer), 80))
            print 'sending buffer to target'
#send out the whole buffer obtained from host
            out.sendall(buffer)
            print 'receiving...'
#recieve all data packets from internet, see more later
            data = self.recv_data(out)
#close internet facing socket
            out.close()
            print 'got reply, closing socket, sending back to localhost'
#send the whole reply back using the local socket generated by .accept()
            msg.sendall(data)
#close that socket aswell
            msg.close()
#this function responsible for getting the IP of target host by parsing an HTTP request
    def getIP(self, buffer):
#finds the first newline character, as HTTP keeps the domain name on the first line
        end = buffer.find('/n')
        try:
#try to slice the first line out of the buffer, than split it and return the middle string
            host = buffer[:end].split()[1]   
#might not succeed, gotta take a close look at this     
        except IndexError:
            print buffer
            print end
            exit()
#next obtain the exact domain name for correct resolution, 
#ommitting the http:// part and omitting anything after eg. .com
        end = host[7:].find('/')
#finally resolve target IP
        host_ip = socket.gethostbyname(host[7:(end+7)])
        print host + ' ' + host_ip
#return the value
        return host_ip

#This function is responsible for recieving ALL the data packets.
#I had a big issues with this earlier because I assumed that recv
#recieves all the tcp packets on a connection. This is not true, recv
#works similiarly to send. This function is to recv what sendall is to send.
    def recv_data(self, out):
#make the internet facing socket non-blocking, ensuring that the socket doesn't
#wait for data all the time (gotta go deeper into this)
        out.setblocking(0)

#create a list to hold the incoming data
        data = []
#empty string to recv data, later gets appened to data
        recv = ''

#timeout timer
        start = time.time()
#infinite loop will receive tcp segments as long as server is sending them  
        while 1:
#however, if it got some data but has been running for over 2 seconds
#it will break and return only the data it got. Could tweak this.
            if data and time.time() - start > 2:
                break
#Also, if it got no data and it's been 4 seconds, also quit.
            elif time.time() - start > 4:
                break
#try to recieve anything from recv, if not then wait, allowing loop to start again
            try:
                recv = out.recv(8192)
                if recv:
#append reply to data, restart timouttimer
                    data.append(recv)
                    start = time.time()
                else:
                    time.sleep(0.1)
#if no connection from recv, pass, restart loop
            except:
                pass
#return the joined data
        return ''.join(data)


#create Queue object
clientPool = Queue.Queue()
#start 5 threads
for i in range(5):
    ClientThread().start()
#put tcp.accepts into queue for as long as they come
while 1:
    clientPool.put(tcp.accept())


tcp.close()
