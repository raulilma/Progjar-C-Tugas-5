import socket
import time
import sys
import asyncore
import logging


class BackendList:
	def __init__(self):
		self.servers=[]
		self.servers.append(('127.0.0.1',9001))
		self.servers.append(('127.0.0.1',9002))
		self.servers.append(('127.0.0.1',9003))
		self.servers.append(('127.0.0.1',9004))
		self.servers.append(('127.0.0.1',9005))
		self.current=0
        
	def getserver(self):
		s = self.servers[self.current]
		self.current=self.current+1
		if (self.current>=len(self.servers)):
			self.current=0
		return s
    
    
class Backend(asyncore.dispatcher_with_send):
    def __init__(self, targetaddress):
        super().__init__()
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect(targetaddress)
        self.connection = self

    def handle_read(self):
        try:
            data = self.recv(10240)
            if data:
                self.client_socket.send(data)
        except:
            self.close()

    def handle_close(self):
        try:
            self.close()
            self.client_socket.close()
        except:
            pass


class ProcessTheClient(asyncore.dispatcher):
    def handle_read(self):
        try:
            data = self.recv(10240)
            if data:
                self.backend.client_socket = self
                self.backend.send(data)
        except:
            self.close()

    def handle_close(self):
        try:
            self.close()
        except:
            pass


class Server(asyncore.dispatcher):
    def __init__(self, portnumber):
        super().__init__()
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind(('', portnumber))
        self.listen(5)
        self.bservers = BackendList()
        logging.warning("Load balancer running on port {}".format(portnumber))

    def handle_accept(self):
        pair = self.accept()
        if pair is not None:
            sock, addr = pair
            logging.warning("Connection from {}".format(repr(addr)))

            #menentukan ke server mana request akan diteruskan
            bs = self.bservers.getserver()
            logging.warning("koneksi dari {} diteruskan ke {}" . format(addr, bs))
            backend = Backend(bs)

            #mendapatkan handler dan socket dari client
            handler = ProcessTheClient(sock)
            handler.backend = backend


def main():
    portnumber = 55555
    try:
        portnumber = int(sys.argv[1])
    except:
        pass
    svr = Server(portnumber)
    asyncore.loop()


if __name__ == "__main__":
    main()
