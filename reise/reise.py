import threading
import socket
import time
from sys import argv, exit
import argparse


#TODO:
#- performance tweaks - tcpProxy fetches test page in about 7 seconds, udpProxy - 35 seconds
#- finish CLI arguments - think about this later on
#- add docstrings to functions
#- add tests for functions - bundle this with refactoring
#- packet size must be user settable


class reise(object):


    class tcpProxy(object):

        def __init__(self, local='127.0.0.1:8088', target=None, l4='http'):
            self._l4 = l4
            #creates receiving socket on local machine
            self._tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
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

        def start(self):
            self._tcp.listen(10)

            while 1:
                reise.ClientThread(self._l4, self._target, self._tcp.accept()).start()

            #DETERMINE WHERE _TCP MUST BE CLOSED?
            # self._tcp.close()




    class udpProxy(tcpProxy):

        def __init__(self, local='127.0.0.1:8089', target=None, l4='http'):
            self._l4 = l4
            self._udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self._udp.bind(self.verify_target_input(local))
            self._target = self.verify_target_input(target)

        def start(self):
            buffer = []
            while 1:
               buffer.append(self._udp.recvfrom(4096))
               packet = self.check(buffer)
               if packet is not None:
                    reise.udpThread(self._l4, self._target, (''.join([i[0][6:] for i in packet]), packet[0][1]), self._udp).start()

        def check(self, buffer):
            for i in buffer:
                packet = filter(lambda x: x[1] == i[1], buffer)
                if len(packet) == int(i[0][3:6]):
                    buffer[:] = (i for i in buffer if i not in packet)
                    return packet


    class ClientThread(threading.Thread):
        def __init__(self, l4, target, sokit, loc=None):
            #size temporary
            self.SIZE = 506
            self.TIMEOUT = 2
            self.target = target
            self.l4 = l4
            self.sokit = sokit  
            self.loc = loc         
            threading.Thread.__init__(self)


        def run(self):
            connection = {'tcp': self.connect_tcp, 'udp': self.connect_udp, 'http': self.connect_http}
            receive = {'tcp': self.recv_tcp, 'http': self.recv_tcp, 'udp': self.recv_udp}

            print '[starting thread]' 
            msg, addr = self.sokit
            buffer = msg.recv(4096)
            print 'Buffer length: %d' % len(buffer)
            soket = connection[self.l4](buffer, self.target)  
            recv = receive[self.l4](soket, self.TIMEOUT-1, msg)  
            msg.close()               
            print 'got reply, closing socket, sending back to localhost'
            print 'sent,\n CLOSING THREAD'
            soket.close()
            print '[closing thread]'      

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

        def recv_tcp(self, out, t, local):
            '''
            This is a revised recv_data function that sends back data as soon as it gets it.
            '''
            out.setblocking(0)
            start = time.time()
            data = False
            while 1:
                if data and time.time() - start > t * 2:
                    break
                elif time.time() - start > t * 3:
                    break
                try:
                    recv = out.recv(8192)
                    if recv:

                        local.sendall(recv)
                        start = time.time()
                        data = True
                    else:
                        time.sleep(0.1)
                except:
                    pass
            local.close()
            return None

        def recv_udp(self, udp, t, local=None):

            data = False
            start = time.time()
            #timeout on the socket bypasses the non-blocking problem
            udp.settimeout(t*5)
            while 1:
                if data and time.time() - start > t:
                    break
                elif time.time() - start > t * 2:
                    break
                try:
                    recv, addr = udp.recvfrom(2048)
                    if recv:
                        local.sendall(recv[6:])
                        data = True
                        start = time.time()
                    else:
                        time.sleep(0.1)
                        print 'sleeping'
                except:
                    #refactor this and other exceptions to provide 
                    #meaningful debugging information.
                    pass
            udp.close()
            return None

        def connect_tcp(self, data, ip_port, s = None):
            if s is None:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect(ip_port)
            s.sendall(data)

            return s

        def connect_udp(self, data, ip_port):
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            #not all udp traffic should be segmented
            for i in self.fragment_and_sequence(data):
                s.sendto(i, ip_port)
            
            return s

        def connect_http(self, data, ip_port=None):
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((self.getIP(data), 80))
            s.sendall(data)
            # data = self.recv_http(s)
            # s.close()
            return s

        def fragment_and_sequence(self, pack):
            '''
            This function is responsible for fragmentation and sequencing of data.
            It uses self._SIZE for maximum packet size and it adds 6 bytes for sequencing.
            Maximum number of sequenced packets is 999 for now. 
            It adds a 6 byte long string with in the format of frag_num|num_of_frags|fragment.
            '''
            max = len(pack)/self.SIZE+1
            return ['%03d%03d%s' % ((i/self.SIZE)+1, max, pack[(0+i):(self.SIZE+i)]) for i in [j*self.SIZE for j in xrange(0, max)]]
   
    class udpThread(ClientThread):

        def __init__(self, l4, target, packet, loc=None):
            #size temporary
            self.SIZE = 506
            self.TIMEOUT = 2
            self.target = target
            self.l4 = l4
            self.recved = packet  
            self.loc = loc         
            threading.Thread.__init__(self)
        
        def run(self):
            connection = {'tcp': self.connect_tcp, 'udp': self.connect_udp, 'http': self.connect_http}
            receive = {'tcp': self.recv_tcp, 'http': self.recv_tcp, 'udp': self.recv_udp}
            print '[starting thread]'

            #following statement is a place-holder
            buffer, addr = self.recved
            print 'Buffer length: %d' % len(buffer)
            print 'BUFFER: %s' % buffer
            soket = connection[self.l4](buffer, self.target)  

            #receive reply and pass it back to previous node
            recv = receive[self.l4](soket, self.TIMEOUT-1, addr)
            print recv
            # connection[self.l4](recv, addr)
            #self.recv_tcp(soket, 1, msg)     
            print 'got reply, closing socket, sending back to localhost'
            print 'sent,\n CLOSING THREAD'
            soket.close()
            print '[closing thread]'

        def recv_tcp(self, out, t, addr):
            '''
            This is a revised recv_data function that sends back data as soon as it gets it.
            '''
            out.setblocking(0)
            start = time.time()
            data = []
            while 1:
                if data and time.time() - start > t * 2:
                    break
                elif time.time() - start > t * 3:
                    break
                try:
                    recv = out.recv(4096)
                    if recv:
                        #gets all the tcp data
                        #s.sendto(recv, addr)
                        print recv
                        data.append(recv)
                        start = time.time()
                 
                    else:
                        time.sleep(0.1)
                except:
                    pass
            print addr
            print len(data)
            #performance can be gained here by sending out udp chunks
            #without waiting, just quick fragmentation.
            for i in self.fragment_and_sequence(''.join(data)):
                self.loc.sendto(i, addr)

            out.close()
            

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