#!/usr/bin/python
import socket
import select
import time
import sys
import os
import psutil

buffer_size = 1024 * 1024
delay = 0.0001
listen_on = ('localhost', 9090)
forward_to = ('localhost', 5672)

class SocketInfo:
	def __init__(self, addr):
		self.addr = addr
		self.pid = self.find_pid_by_laddr(self.addr)
		self.cmdline = self.find_cmdline(self.pid) if self.pid else None
		self.target = None
		
	def find_pid_by_laddr(self, laddr):
		nc = psutil.net_connections()
		for c in nc:
			if c.laddr == laddr:
				return c.pid
		return None

	def find_cmdline(self, pid):
		p = psutil.Process(pid)
		return p.cmdline()

	def __str__(self):
		return '%d: %s [%d]' % (self.pid, ' '.join(self.cmdline) if self.cmdline else 'unknown', self.addr[1] if len(self.addr) == 2 else str(self.addr))

class ForwardSocket:
    def __init__(self):
        self.forward = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def connect(self, host, port):
        try:
            self.forward.connect((host, port))
            return self.forward
        except Exception, e:
            print e
            return False
		
class ServerProxy:
    input_list = []
    channel = {}
    active_sockinfo = []

    def __init__(self, host, port):
        self.server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_sock.bind((host, port))
        self.server_sock.listen(200)

    def main_loop(self):
        self.input_list.append(self.server_sock)
        while 1:
            time.sleep(delay)
            inputready, outputready, exceptready = select.select(self.input_list, [], [])
			# todo: use threads
            for sock in inputready:
                if sock == self.server_sock:
                    self.handle_connect()
                    break

                data = sock.recv(buffer_size)
                if len(data) == 0:
                    self.handle_close(sock)
                    break
                else:
                    self.handle_recv(sock, data)

    def find_active_sockinfo(self, addr):
        for sockinfo in self.active_sockinfo:
            if sockinfo.addr == addr:
                return sockinfo
        return None

    def handle_connect(self):
        forward = ForwardSocket().connect(forward_to[0], forward_to[1])
        clientsock, clientaddr = self.server_sock.accept()
        sockinfo = SocketInfo(clientaddr)
	if forward:
            print sockinfo, "has connected"
            self.active_sockinfo.append(sockinfo)
            self.input_list.append(clientsock)
            self.input_list.append(forward)
            self.channel[clientsock] = forward
            self.channel[forward] = clientsock
        else:
            print "Can't establish connection with remote server." % self.server_sock.getpeername(),
            print "Closing connection with client side", sockinfo
            clientsock.close()

    def handle_close(self, sock):
        sockinfo = self.find_active_sockinfo(sock.getpeername())
        print sockinfo, "disconnected"
        self.active_sockinfo.remove(sockinfo)
        self.input_list.remove(sock)
        self.input_list.remove(self.channel[sock])
        out = self.channel[sock]
        self.channel[out].close()
        self.channel[sock].close()
        del self.channel[out]
        del self.channel[sock]

    def handle_recv(self, sock, data):
        sockinfo = self.find_active_sockinfo(sock.getpeername())
        print sockinfo, "receive---"
        print ''.join('%02x ' % ord(x)  for x in data)
        print sockinfo, "receive---end"
        self.channel[sock].send(data)

if __name__ == '__main__':
        server = ServerProxy(listen_on[0], listen_on[1])
        try:
            server.main_loop()
        except KeyboardInterrupt:
            print "STOPPED"
            sys.exit(1)

