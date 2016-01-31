#!/usr/bin/python
import socket
import select
import time
import sys
import psutil
import array
from amqp.factory import get_protocol
from amqp.stream import AMQPStreamReader


class AMQPStateMachine:
    def __init__(self):
        self.protocol = None

    def handle_client_send(self, data):
        if not self.protocol:
            self.protocol = get_protocol(''.join(data))
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
    def __init__(self, listen_addr, fwd_addr):
        self.buffer_size = 1024 * 512  # 512KB
        self.buffer = array.array('c', b'\x00' * self.buffer_size)
        self.conns = {}
        self.socks = []
        self.fwd_addr = fwd_addr
        self.ssock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.ssock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.ssock.bind(listen_addr)
        self.ssock.listen(200)
        self.socks.append(self.ssock)

    def run(self):
        while 1:
            time.sleep(0.0001)
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
        fwdsock = self.make_fwdsock(self.fwd_addr)
        csock, caddr = self.ssock.accept()
        csockinfo = ClientSocketInfo(csock, caddr)
        if fwdsock:
            conn = ClientConnection(csockinfo, fwdsock)
            self.conns[conn.csockinfo.sock] = conn
            self.conns[conn.fwdsock] = conn
            self.socks.append(conn.csockinfo.sock)
            self.socks.append(conn.fwdsock)
            print csockinfo, "connected client"
        else:
            print "Unable to connect to server." % self.ssock.getpeername(),
            print "Disconnecting client.", csockinfo
            csock.close()

    def handle_close(self, conn):
        print conn.csockinfo, "disconnected client"
        del self.conns[conn.csockinfo.sock]
        del self.conns[conn.fwdsock]
        self.socks.remove(conn.csockinfo.sock)
        self.socks.remove(conn.fwdsock)
        conn.close()


def show_usage():
    print "\n".join([
        'Usage:',
        '  %s --listen=[host]:port --forward=host:[port]' % sys.argv[0],
        'Example:',
        '  %s --listen=:9090 --forward=localhost:5672' % sys.argv[0],
        ''
    ])
    exit(1)


def parse_args():
    if len(sys.argv) != 3:
        show_usage()
    listen_host = ''
    listen_port = None
    fwd_host = None
    fwd_port = 5672
    for argv in sys.argv:
        nv = argv.split('=')
        if len(nv) != 2:
            continue
        if nv[0] == '--listen':
            hp = nv[1].split(':')
            if len(hp) != 2:
                continue
            listen_host = hp[0]
            try:
                listen_port = int(hp[1])
            except ValueError:
                print 'Invalid listen port.'
                show_usage()
        elif nv[0] == '--forward':
            hp = nv[1].split(':')
            if len(hp) != 2:
                continue
            fwd_host = hp[0]
            if len(hp[1]):
                try:
                    fwd_port = int(hp[1])
                except ValueError:
                    print 'Invalid forward port.'
                    show_usage()
    if not listen_port:
        print 'Listen port not specified.'
        show_usage()
    if not fwd_host:
        print 'Forward host not specified.'
        show_usage()
    return (listen_host, listen_port), (fwd_host, fwd_port)


if __name__ == '__main__':
    listen_addr, fwd_addr = parse_args()
    server = ServerProxy(listen_addr, fwd_addr)
    try:
        server.run()
    except KeyboardInterrupt:
        print " INTERRUPTED"
        sys.exit(1)

