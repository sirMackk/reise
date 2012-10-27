#threading proxy using Queue
#early stage

import threading
import socket
import Queue
import time
from sys import argv
#TODO 
#- initial testing shows that this script uses about 30% of the CPU, so it would
#be nice to think about optimizing it later. Maybe Cython?
#- think about using getopt instead of just argv, might make things easier and nicer.

#To make this class more universal, I should let the user be able to chose source
#and destination ports. By default they could be 80 and 53. I must also get a resource
#to forge dns packets along with being able to fragment them as normal dns packet size is
#512 bytes whereas normal http packets size is about 1500 bytes. Main issue now is
#to make this project highly reusable. Best idea so far is have some default values
#that can be overridden in the script. Will this impact the performance?
#Gotta think about the general tcpProxy class structure.


#Think about this
#- using decorators for building spoofed packets
#- using an external configuration file for the script to run on


class reise(object):


    class tcpProxy(object):

        def __init__(self, target, threads, l4):
            #ask for user input via argv here?

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
        def run(self, l4, target):
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
            #have to do good unit testin and refactoring on this function
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

            s.sendto(data, (ip, 53))
            return recv_udp(s)

        def fragment_and_sequence(self, data):
            pass
def __init__(self):

    loadConfig()


def load_config(self):
    try:
        config_file = open('reise.conf')
    except IOError:
        print 'Problem reading reise.conf file'

    #this function should handle most of the config file
    #knowing which lines to load and what the configuration does
    #to the tcpProtocol class and clientThread classes.




#example code, place-holder
if __name__ == '__main__':
    script, target, port, threads, protocol = argv
    proxy = tcpProxy(target, port, threads, protocol)
    proxy.run()