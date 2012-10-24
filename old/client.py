import socket
from sys import argv
script, port = argv
if __name__ == '__main__':
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind((socket.gethostbyname(socket.getfqdn()), int(port)))
    print (socket.gethostbyname(socket.getfqdn()), int(port))
    s.settimeout(15)
    reply = '''HTTP/1.0 200 OK
    Date: Fri, 31 Dec 1999 23:59:59 GMT
    Content-Type: text/html
    Content-Length: 1354

    <html>
    <body>
    <h1>Happy New Millennium!</h1>
    <a href="google.com">CLICK</a>
    </body>
    </html>'''
    print 'setup complete'
    while 1:
       # try:
        print 'receiving'
        data, addr = s.recvfrom(2048)
        print data, addr
        print data
        print 'replying'
        print addr
        s.sendto(reply, addr)
        print 'replied'
       # except:
            # print 'closing'
            # s.close()


    print 'done'
    s.close()
    