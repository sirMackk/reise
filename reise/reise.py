import threading
import socket
import time
from sys import argv, exit
import argparse

#TODO:
#- performance tweaks - tcpProxy fetches test page in about 7 seconds, udpProxy - 22 seconds
#- add docstrings to functions
#- add tests for functions - bundle this with refactoring


class reise(object):

    class tcpProxy(object):

        def __init__(self, local='127.0.0.1:8088', target=None, size=506, l4='http'):
            self._l4 = l4
            self._size = int(size)
            try:
                self._tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self._tcp.bind(self.verify_target_input(local))
            except Exception, e:
                print 'Error while creating local tcpProxy socket in thread: %s' % e
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
            #returns tuple of (string, int)
            return ('.'.join(str(i) for i in outbound_ip), port)

        def start(self):
            self._tcp.listen(10)

            while 1:
                reise.ClientThread(self._l4, self._target, self._size, self._tcp.accept()).start()

    class udpProxy(tcpProxy):

        def __init__(self, local='127.0.0.1:8089', target=None, size=506,  l4='http'):
            # self._l4 = l4
            try:
                self._udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                self._udp.bind(self.verify_target_input(local))
            except Exception, e:
                print 'Error while creating local udpProxy socket in thread: %s' % e
            self._target = self.verify_target_input(target)

        def start(self):
            buffer = []
            start = time.time()
            while 1:
                buffer.append(self._udp.recvfrom(4096))
                packet = self.check(buffer)
                if packet is not None:
                    reise.udpThread(l4, self._target, size, (''.join([i[0][6:] for i in packet]),
                                     packet[0][1]), self._udp).start()
                if time.time() - start > 5:
                    try:
                        del buffer[0]
                    except:
                        pass
                    start = time.time()


        def check(self, buffer):
            for i in buffer:
                packet = filter(lambda x: x[1] == i[1], buffer)
                if len(packet) == int(i[0][3:6]):
                    buffer[:] = (i for i in buffer if i not in packet)
                    return packet


    class ClientThread(threading.Thread):
        def __init__(self, l4, target, size, sokit, local=None):
            self.SIZE = size
            self.TIMEOUT = 2
            self.target = target
            self.l4 = l4
            self.sokit = sokit  
            self.loc = local         
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
            print 'sent ,CLOSING THREAD' 
            soket.close()
            print '[closing thread]'      

        def getIP(self, buffer):
            end = buffer.find('/n')
            try:
                host = buffer[:end].split()[1]      
            except IndexError:
                print 'IndexError in getIP function, buffer state: ', buffer, end
                raise IndexError
            end = host[7:].find('/')
            host_ip = socket.gethostbyname(host[7:(end+7)])
            print '%s %s' % (host, host_ip)
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
                except Exception, e:
                    print 'Error in ClientThread module recv_tcp function: %s' % e
                    pass
            local.close()
            return None

        def recv_udp(self, udp, t, local=None):
            '''This function is responsible for receiving udp data, defragging it,
            and passing it back to the local interface.
            '''
            data = []
            start = time.time()
            udp.settimeout(t*4)
            while 1:
                if data and time.time() - start > t:
                    break
                elif time.time() - start > t * 1.3:
                    break
                try:
                    recv, addr = udp.recvfrom(2048)
                    if recv:
                        data.append(recv)
                        #following is a performance tweak, that uses the delimiter of
                        #a fragment to break the loop and send it back faster. 
                        if len(data) == int(data[0][3:6]):
                            break
                        start = time.time()
                    else:
                        time.sleep(0.1)
                        print 'sleeping'
                except Exception, e:
                    print 'Error in ClientThread module recv_udp function: %s' % e
                    print '(timing out is normal)'
                    pass
            data.sort()
            local.sendall(''.join([i[6:] for i in data]))
            udp.close()
            return None

        def connect_tcp(self, data, ip_port, s = None):
            if s is None:
                try:
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.connect(ip_port)
                except Exception, e:
                    print 'Error in connect_tcp function while creating or connecting \
                            to target ip: %s' %s
                    pass
            s.sendall(data)
            return s

        def connect_udp(self, data, ip_port):
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            except Exception, e:
                print 'Error in connect_udp function while creating socket: %s' % e
                pass
            for i in self.fragment_and_sequence(data):
                s.sendto(i, ip_port)        
            return s

        def connect_http(self, data, ip_port=None):
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.connect((self.getIP(data), 80))
            except Exception, e:
                print 'Error in connect_http function while creating socket or connecting \
                        to target ip: %s' % e
            s.sendall(data)
            return s

        def fragment_and_sequence(self, pack):
            '''
            This function is responsible for fragmentation and sequencing of data.
            It uses self._SIZE for maximum packet size and it adds 6 bytes for sequencing.
            Maximum number of sequenced packets is 999 for now. 
            It adds a 6 byte long string with in the format of frag_num|num_of_frags|fragment.
            '''
            max = len(pack)/self.SIZE+1
            return ['%03d%03d%s' % ((i/self.SIZE)+1, max, 
                pack[(0+i):(self.SIZE+i)]) for i in [j*self.SIZE for j in xrange(0, max)]]
   
    class udpThread(ClientThread):
        
        def run(self):
            connection = {'tcp': self.connect_tcp, 'udp': self.connect_udp, 'http': self.connect_http}
            receive = {'tcp': self.recv_tcp, 'http': self.recv_tcp, 'udp': self.recv_udp}

            print '[starting thread]'
            buffer, addr = self.sokit
            print 'Buffer length: %d' % len(buffer)
            print 'BUFFER: %s' % buffer
            soket = connection[self.l4](buffer, self.target)  
            recv = receive[self.l4](soket, self.TIMEOUT-1, addr)
            print 'got reply, closing socket, sending back to localhost'
            print 'sent, CLOSING THREAD' 
            soket.close()
            print '[closing thread]'
        def recv_tcp(self, out, t, addr):
            '''
            This is a revised recv_tcp function for us in the udpProxy class to ensure
            a more efficient handling of incoming data.
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
                        data.append(recv)
                        start = time.time()  
                    else:
                        time.sleep(0.1)
                except Exception, e:
                    print 'Error in recv_tcp function in udpThread: %s' % e
                    pass

            for i in self.fragment_and_sequence(''.join(data)):
                self.loc.sendto(i, addr)
            out.close()
    
if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('-l', '--local', help = 'The local [ip:port] on which to listen to,\
                                     blank is 127.0.0.1  AUTO is set by socket.getfqdn()',
                                    default = '127.0.0.0:8088')
    parser.add_argument('-t', '--target', help = 'The target host [ip:port], blank on tcp defaults to \
                                         global, blank on udp defaults to localhost', )
    parser.add_argument('-p', '--protocol', help = 'Outbound protocl to use [http/tcp/udp]. \
                            Use http if this is the exit node, tcp for connectivity \
                            between tcp nodes and udp for connectivity between \
                             udp nodes.', default = 'http')
    parser.add_argument('-n', '--node', help = '[tcp/udp] - Set the local node type. Default: TCP.', 
                                        default = 'tcp')
    parser.add_argument('-s', '--size', help = 'Adjust the size of udp packets if using \
                                        udpProxy. Default is 506.', default = 506)

    args = parser.parse_args()
    if args.node == 'tcp':
        proxy = reise.tcpProxy(args.local, args.target, args.size, args.protocol)
        proxy.start()
    elif args.node == 'udp':
        proxy = reise.udpProxy(args.local, args.target, args.size, args.protocol)
        proxy.start()
    else:
        print 'Type \'reise.py -h\' for help'