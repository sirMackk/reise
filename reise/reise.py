#threading proxy using Queue
#early stage

import threading
import socket
import Queue
import time
from sys import argv, exit
import argparse


#TODO:
#- PRIORITY - figure out correct timeouts for receiving data, it's
#             a huge bottleneck bandwidth wise and it makes TCP RSTs.
#- finish CLI arguments - think about this later on
#- refactor a few functions according to execution time
#- complete main __init__ functions - bundle this with testing
#- add udpProxy based on tcpProxy
#- add docstrings to functions
#- add tests for functions - bundle this with refactoring
#- add SSH tunneling between proxies


class reise(object):


    class tcpProxy(object):

        def __init__(self, local='127.0.0.1:8088', target=None, threads=6, l4='http'):
            self._threads = threads
            self._l4 = l4
            self._tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

            ##double check this section later
            self._tcp.bind(self.verify_target_input(local))

            self._target = self.verify_target_input(target)


        def verify_target_input(self, target):
            '''
            This function verifies the user input for the target IP.
            It makes sure that the address is an IPv4 decimal dotted
            notation address with a port.
            '''
            if target is None:
                return None

            outbound = target.split(':')
            try:
                outbound_ip = [int(i) for i in outbound[0].split('.')]
            except ValueError:
                raise ValueError ('Bad IP address')
            try:
                 if int(outbound[1]) > 0 and int(outbound[1]) < 65535:
                    port = int(outbound[1])
            except ValueError:
                raise ValueError('Bad port')
            if len(outbound_ip) == 4:
                for i in outbound_ip:
                    if i < 0 or i >= 255:
                        raise ValueError('IP too large or too small: %d' %i)
            else:
                raise IndexError('IP too short or too long')

            return ('.'.join(str(i) for i in outbound_ip), port)

            
        #Doesn't work, just a place-holder
        def start(self):
            self._tcp.listen(10)
            clientPool = Queue.Queue()
            for i in xrange(self._threads):
                reise.ClientThread(self._l4, self._target, clientPool).start()
            while 1:
                clientPool.put(self._tcp.accept())

            self._tcp.close()

    #ClientThread class subclasses threading.Thread class
    class ClientThread(threading.Thread):
        #this class is the actual receiving and sending interface to work with.
        def __init__(self, l4, target, clientPool):
            #size temporary
            self.SIZE = 506
            self.TIMEOUT = 2
            self.target = target
            self.l4 = l4

            ##THIS VARIABLE MUST BE USER SET IN THE FUTURE.
            self.recv = 'raw'
            self.pool = clientPool
            threading.Thread.__init__(self)

        def run(self):
            connection = {'tcp': self.connect_tcp, 'udp': self.connect_udp, 'http': self.connect_http,
                            'raw': self.connect_raw}
            receive = {'raw': self.recv_raw, 'tcp': self.recv_data, 'udp': self.recv_udp, 'http': self.recv_raw}

            while 1:
                #refactor the next 9 lines of code later
                print '[starting thread]'
                try:
                    item = self.pool.get()
                    #item = clientPool.get(True, 10)
                except Queue.Empty:
                    print 'EMPTY EMPTY'
                    break
                if item is None:
                    print 'NONE'
                    break
                msg, addr = item
                buffer = receive[self.recv](msg)  
                print 'Buffer length: %d' % len(buffer)
                soket, what = connection[self.l4](buffer, self.target)   
                data = receive[what](soket)  
                soket.close()  
                print 'Recieve length: %d' % len(data)    
                print 'got reply, closing socket, sending back to localhost'
                # print data
                # msg.sendall(data)
                soket, what = connection[self.recv](data, None, msg)
                print 'sent'
                soket.close()

        def getIP(self, buffer):
            ##have to do good unit testin and refactoring on this function
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
            '''
            This function is responsible for receiving all the data through
            a TCP connection. The timeout values are in seconds.
            The function also sorts the packets and removes the 6 byte header from
            them.
            '''
            out.setblocking(0)

            data = []
            recv = ''

            start = time.time()
            while 1:
                if data and time.time() - start > self.TIMEOUT:
                    break
                elif time.time() - start > self.TIMEOUT*2:
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
            data.sort()
            #returns a string compromised of fragments with the headers removed
            return ''.join([i[6:] for i in data])

        def recv_raw(self, out):
            out.setblocking(0)
            data = []
            recv = ''

            start = time.time()
            while 1:
                if data and time.time() - start > self.TIMEOUT*2:
                    break
                elif time.time() - start > self.TIMEOUT*4:
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
            udp.setblocking(0)
            data = []
            recv = ''
            start = time.time()

            while 1:
                if data and time.time() - start > self.TIMEOUT:
                    break
                elif time.time() - start > self.TIMEOUT*2:
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
            data.sort()

            #returns a string compromised of fragments with the headers removed
            return ''.join([i[6:] for i in data])


        def connect_raw(self, data, ip_port, s = None):
            if s is None:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect(ip_port)
            s.sendall(data)
            return s, 'raw'


        def connect_tcp(self, data, ip_port, s = None):
            if s is None:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect(ip_port)
            #USES FRAGMENTING FUNCTION, DOUBLE CHECK THIS LATER / SAME FOR CONNECT_UDP
            for i in self.fragment_and_sequence(data):
                s.sendall(i)

            return s, 'tcp'

        def connect_udp(self, data, ip_port):
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            #make port mutable
            #this is the part that decides which spoofing protocol to use
            #or to send raw data. The protocol should also be able to
            #fragment and sequence packets just in case size differs.
            for i in fragment_and_sequence(data):
                s.sendto(i, ip_port)
            return self.recv_udp(s)

        def connect_http(self, data, ip_port=None):
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((self.getIP(data), 80))
            s.sendall(data)
            # data = self.recv_http(s)
            # s.close()
            return s, 'http'

        def fragment_and_sequence(self, pack):
            '''
            This function is responsible for fragmentation and sequencing of data.
            It uses self._SIZE for maximum packet size and it adds 6 bytes for sequencing.
            Maximum number of sequenced packets is 999 for now. 
            It adds a 6 byte long string with in the format of frag_num|num_of_frags|fragment.
            '''
            ##think about the second number, maybe packets dont need the extra info about
            ##x out of y for their size, it's not used in sorting it anyway, as you previously
            ##though would be needed. That's 3 bytes saved per packet.
            max = len(pack)/self.SIZE+1
            return ['%03d%03d%s' % ((i/self.SIZE)+1, max, pack[(0+i):(self.SIZE+i)]) for i in [j*self.SIZE for j in xrange(0, max)]]


#scaffolding
if __name__ == '__main__':

    #working on CLI arguments and finally and final structure of program 
    parser = argparse.ArgumentParser()
    parser.add_argument('-l', '--local', help = 'The local [ip:port] on which to listen to,\
                                     blank is 127.0.0.1  AUTO is set by socket.getfqdn()',
                                    default = '127.0.0.0:8088')
    parser.add_argument('-t', '--target', help = 'The target host [ip:port], blank on tcp defaults to \
                                         global, blank on udp defaults to localhost', )
    parser.add_argument('-p', '--protocol', help = 'Outbound protocl to use. Default tcp or udp for \
                                         udp', default = 'tcp')
    parser.add_argument('-n', '--nthreads', help = 'The number of connection/receive threads to \
                                            run, blank is 6', default = 6)
    parser.add_argument('-r', '--proxy', help = 'Type of proxy to run on the local machine',
                                         default = 'tcp')
    args = parser.parse_args()

    print args

    print args.local
    print args.protocol

    #placeholder code for now
    proxy = tcpProxy(target, port, threads, protocol)
    proxy.run()