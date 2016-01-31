#!/usr/bin/python
import socket
import select
import time
import sys
import psutil
import array
from amqp.factory import get_protocol
from amqp.stream import AMQPStreamReader


g_buffer_size = 4096
g_delay = 0.0001
g_listen_addr = ('', 9090)
g_fwd_addr = ('localhost', 5672)


class AMQPStateMachine:
    def __init__(self):
        self.protocol = None

    def handle_client_send(self, data):
        if not self.protocol:
            self.protocol = get_protocol(''.join([x for x in data]))
            return
        self.handle_frame(data)

    def handle_client_recv(self, data):
        if not self.protocol:
            return
        self.handle_frame(data)

    def handle_frame(self, data):
        reader = AMQPStreamReader(data, self.protocol.SIG_TO_DATA_TYPE)
        while not reader.eof():
            frame = self.protocol.read_frame(reader)
            print frame


class ClientSocketInfo:
    def __init__(self, sock, addr):
        self.sock = sock
        self.addr = addr
        self.pid = self.find_pid_by_laddr(self.addr)
        self.cmdline = self.find_cmdline(self.pid) if self.pid else None

    @staticmethod
    def find_pid_by_laddr(laddr):
        nc = psutil.net_connections()
        for c in nc:
            if c.laddr == laddr:
                return c.pid
        return None

    @staticmethod
    def find_cmdline(pid):
        p = psutil.Process(pid)
        return p.cmdline()

    def __str__(self):
        pid = self.pid if self.pid else -1
        cmdline = ' '.join(self.cmdline) if self.cmdline else str(self.addr[0])
        port = self.addr[1] if len(self.addr) == 2 else -1
        return "%.8f\n%6d: %s [%d]" % (time.time(), pid, cmdline, port)


class ClientConnection:
    def __init__(self, csockinfo, fwdsock):
        self.csockinfo = csockinfo
        self.fwdsock = fwdsock
        self.strc = str(csockinfo)
        self.strf = str(fwdsock.getpeername())
        self.amqp = AMQPStateMachine()

    def close(self):
        self.csockinfo.sock.close()
        self.fwdsock.close()
        self.csockinfo.sock = None
        self.csockinfo = None
        self.fwdsock = None

    @staticmethod
    def print_data(data):
        non_ascii = range(0, 31) + [127, 255]
        l = len(data)
        i = 0
        while i < l:
            sl = [data[i:i+8], data[i+8:i+16]]
            ln = [
                ' '.join('%02X' % ord(x) for x in sl[0]).ljust(24),
                ' '.join('%02X' % ord(x) for x in sl[1]).ljust(24),
                ''.join('.' if ord(x) in non_ascii else x for x in sl[0]),
                ''.join('.' if ord(x) in non_ascii else x for x in sl[1])
            ]
            print '%7d' % i, ' '.join(ln)
            i += 16
        print '-' * 75

    def handle_data(self, sock, data):
        if sock == self.fwdsock:
            print self.strc, "<<", self.strf
            self.amqp.handle_client_recv(data)
            self.csockinfo.sock.send(data)
        else:
            print self.strc, ">>", self.strf
            self.amqp.handle_client_send(data)
            self.fwdsock.send(data)
        self.print_data(data)


class ServerProxy:
    def __init__(self, addr):
        self.buffer_size = 1024 * 512  # 512KB
        self.buffer = array.array('c', b'\x00' * self.buffer_size)
        self.conns = {}
        self.socks = []
        self.ssock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.ssock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.ssock.bind(addr)
        self.ssock.listen(200)
        self.socks.append(self.ssock)

    def run(self):
        while 1:
            time.sleep(g_delay)
            iready, oready, exready = select.select(self.socks, [], [])
            # todo: use threads
            for sock in iready:
                if sock == self.ssock:
                    self.handle_connect()
                    break
                conn = self.conns[sock]
                try:
                    read_size = sock.recv_into(self.buffer, self.buffer_size)
                except socket.error, e:
                    print e
                    read_size = 0
                if not read_size:
                    self.handle_close(conn)
                    break
                conn.handle_data(sock, self.buffer[:read_size])

    @staticmethod
    def make_fwdsock(addr):
        fwdsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            fwdsock.connect(addr)
        except Exception, e:
            print e
            fwdsock = False
        return fwdsock

    def handle_connect(self):
        fwdsock = self.make_fwdsock(g_fwd_addr)
        csock, caddr = self.ssock.accept()
        csockinfo = ClientSocketInfo(csock, caddr)
        if fwdsock:
            conn = ClientConnection(csockinfo, fwdsock)
            self.conns[conn.csockinfo.sock] = conn
            self.conns[conn.fwdsock] = conn
            self.socks.append(conn.csockinfo.sock)
            self.socks.append(conn.fwdsock)
            print csockinfo, "has connected"
        else:
            print "Can't establish connection with remote server." % self.ssock.getpeername(),
            print "Closing connection with client side", csockinfo
            csock.close()

    def handle_close(self, conn):
        print conn.csockinfo, "disconnected"
        del self.conns[conn.csockinfo.sock]
        del self.conns[conn.fwdsock]
        self.socks.remove(conn.csockinfo.sock)
        self.socks.remove(conn.fwdsock)
        conn.close()


if __name__ == '__main__':
    server = ServerProxy(g_listen_addr)
    try:
        server.run()
    except KeyboardInterrupt:
        print " INTERRUPTED"
        sys.exit(1)

