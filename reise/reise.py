#threading proxy using Queue
#early stage

import threading
import socket
import Queue
import time
from sys import argv


#TODO:
#- finish CLI arguments - think about this later on
#- packets fragmentation and sequencing - ALMOST COMPLETE
#- refactor a few functions according to execution time
#- complete main __init__ functions - bundle this with testing
#- add udpProxy based on tcpProxy
#- add docstrings to functions
#- add tests for functions - bundle this with refactoring
#- add SSH tunneling between proxies

class reise(object):


    class tcpProxy(object):

        def __init__(self, local='127.0.0.1:8088', target=None, threads=6, l4='tcp'):
            try:
                verify_target_input(target)
            except ValueError:
                exit()
            except IndexError:
                exit()
            self._l4 = l4
            self._tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            #gets local IP by getfqdn, might be buggy though, giving IP of wrong interface
            self._tcp.bind((socket.gethostbyname(socket.getfqdn()), port))
            self._tcp.listen(10)

        def _verify_target_input(self, target):
            '''
            This function verifies the user input for the target IP.
            It makes sure that the address is an IPv4 decimal dotted
            notation address with a port.
            '''

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

            return '.'.join(str(i) for i in outbound_ip), port





            
        #Doesn't work, just a place-holder
            def start(self):
                clientPool = Queue.Queue()
                for i in range(5):
                    ClientThread().start(l4, target)
                while 1:
                    clientPool.put(tcp.accept())

                tcp.close()

    #ClientThread class subclasses threading.Thread class
    class ClientThread(threading.Thread):
        #this class is the actual receiving and sending interface to work with.
        def run(self, l4, target, size=505):
            self.SIZE = size;
            connection = {'tcp': connect_tcp, 'udp': connect_udp}
            while 1:
                #refactor the next 9 lines of code later
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
                #recieving should also use a defined spoofed protocol
                #filter as well as sequencing and defragmenting. Default would
                #be raw
                buffer = msg.recv(8192)   
                print 'Buffer length: %d' % len(buffer)
                connection[l4](buffer, target)            
                print 'got reply, closing socket, sending back to localhost'
                print data
                msg.sendall(data)
                msg.close()

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

        def connect_tcp(self, data, ip):
            if ip is None:
                ip = self.getIP(data)
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            #make port mutable
            s.connect((ip, 80))
            #USES FRAGMENTING FUNCTION, DOUBLE CHECK THIS LATER / SAME FOR CONNECT_UDP
            for i in fragment_and_sequence(data):
                s.sendall(data)
            data = recv_data(s)
            s.close()
            return data

        def connect_udp(self, data, ip):
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            #make port mutable
            #this is the part that decides which spoofing protocol to use
            #or to send raw data. The protocol should also be able to
            #fragment and sequence packets just in case size differs.
            for i in fragment_and_sequence(data):
                s.sendto(data, (ip, 53))
            return recv_udp(s)

        def fragment_and_sequence(self, pack):
            '''
            This generator is responsible for fragmentation and sequencing of data.
            It uses self._SIZE for maximum packet size and it adds 7 bytes for sequencing.
            Maximum number of sequenced packets is 999 for now. 
            It adds a 7 byte long string with in the format of frag_num#num_of_frags#fragment.
            '''
            #might need delimiter at the end of fragment maybe?
            max = len(pack)/self.SIZE+1
            frags = ['%s#%s#%s' % (str((i/self.SIZE)+1), str(max), pack[(0+i):(self.SIZE+i)]) for i in [j*self.SIZE for j in xrange(0, max)]]
            for i in frags:
                yield i


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