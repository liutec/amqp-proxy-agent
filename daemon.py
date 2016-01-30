#!/usr/bin/python
import socket
import select
import time
import sys
import struct
import psutil
from collections import namedtuple

g_delay = 0.0001
g_listen_addr = ('', 9090)
g_fwd_addr = ('localhost', 5672)


AMQPFrameHeader = namedtuple('AMQPFrameHeader', 'type channel frame_size msig')


class AMQPConnection:
    AMQP091_HEADER = '\x41\x4D\x51\x50\x00\x00\x09\x01'
    KNOWN_HEADERS = [AMQP091_HEADER]
    FRAME_HEADER_SIZE = 11
    METHOD_MAP_91 = {
        0x000A000A: 'connection_start',
        0x000A000B: 'connection_start_ok',
        0x000A0014: 'connection_secure',
        0x000A0015: 'connection_secure_ok',
        0x000A001E: 'connection_tune',
        0x000A001F: 'connection_tune_ok',
        0x000A0028: 'connection_open',
        0x000A0029: 'connection_open_ok',
        0x000A0032: 'connection_close',
        0x000A0033: 'connection_close_ok',
        0x000A003C: 'connection_blocked',
        0x000A003D: 'connection_unblocked',
        0x0014000A: 'channel_open',
        0x0014000B: 'channel_open_ok',
        0x00140014: 'channel_flow',
        0x00140015: 'channel_flow_ok',
        0x00140028: 'channel_close',
        0x00140029: 'channel_close_ok',
        0x001E000A: 'access_request',
        0x001E000B: 'access_request_ok',
        0x0028000A: 'exchange_declare',
        0x0028000B: 'exchange_declare_ok',
        0x00280014: 'exchange_delete',
        0x00280015: 'exchange_delete_ok',
        0x0028001E: 'exchange_bind',
        0x0028001F: 'exchange_bind_ok',
        0x00280028: 'exchange_unbind',
        0x00280033: 'exchange_unbind_ok',
        0x0032000A: 'queue_declare',
        0x0032000B: 'queue_declare_ok',
        0x00320014: 'queue_bind',
        0x00320015: 'queue_bind_ok',
        0x0032001E: 'queue_purge',
        0x0032001F: 'queue_purge_ok',
        0x00320028: 'queue_delete',
        0x00320029: 'queue_delete_ok',
        0x00320032: 'queue_unbind',
        0x00320033: 'queue_unbind_ok',
        0x003C000A: 'basic_qos',
        0x003C000B: 'basic_qos_ok',
        0x003C0014: 'basic_consume',
        0x003C0015: 'basic_consume_ok',
        0x003C001E: 'basic_cancel_from_server',
        0x003C001F: 'basic_cancel_ok',
        0x003C0028: 'basic_publish',
        0x003C0032: 'basic_return',
        0x003C003C: 'basic_deliver',
        0x003C0046: 'basic_get',
        0x003C0047: 'basic_get_ok',
        0x003C0048: 'basic_get_empty',
        0x003C0050: 'basic_ack_from_server',
        0x003C005A: 'basic_reject',
        0x003C0064: 'basic_recover_async',
        0x003C006E: 'basic_recover',
        0x003C006F: 'basic_recover_ok',
        0x003C0078: 'basic_nack_from_server',
        0x005A000A: 'tx_select',
        0x005A000B: 'tx_select_ok',
        0x005A0014: 'tx_commit',
        0x005A0015: 'tx_commit_ok',
        0x005A001E: 'tx_rollback',
        0x005A001F: 'tx_rollback_ok',
        0x0055000A: 'confirm_select',
        0x0055000B: 'confirm_select_ok',
    }

    # send header
    # recv capabilities + login method
    # send capabilities + login credentials

    def __init__(self):
        self.recv_next = 8
        self.header = None
        self.expecting_frame_header = False
        self.expecting_frame_data = False
        self.frame_header = None
        self.frame_max = 131072
        self.connected = False

    def handle_send(self, data):
        if not self.header:
            if data in self.KNOWN_HEADERS:
                self.expecting_frame_header = True
                self.recv_next = self.FRAME_HEADER_SIZE
                self.header = data
        else:
            self.header_logic(data)

    def handle_recv(self, data):
        if self.header:
            self.header_logic(data)
        pass

    def header_logic(self, data):
        if self.expecting_frame_header:
            self.frame_header = self.unpack_frame_header(data)
            if self.frame_header:
                self.print_frame_header(self.frame_header)
                self.expecting_frame_header = False
                self.expecting_frame_data = True
                self.recv_next = self.frame_header.frame_size - 3
        elif self.expecting_frame_data:
            self.expecting_frame_header = True
            self.expecting_frame_data = False
            self.recv_next = self.FRAME_HEADER_SIZE

    def get_method_by_sig(self, msig):
        return self.METHOD_MAP_91[msig] if msig in self.METHOD_MAP_91 else 'UNKNOWN'

    def print_frame_header(self, header):
        if header:
            print ' ' * 7, 'frame type: %d, channel: %d, frame size: %d, method: %s' % \
                           (header.type, header.channel, header.frame_size, self.get_method_by_sig(header.msig))
        else:
            print 'Packet too short to contain frame header.'

    def unpack_frame_header(self, data):
        # frame type (1: byte), channel id (2: short), frame size (4: long), method (4: long)
        if len(data) >= self.FRAME_HEADER_SIZE:
            return AMQPFrameHeader._make(struct.unpack('!bhll', data[:self.FRAME_HEADER_SIZE]))
        return None

    def expect_header(self, data):
        return False

    def parse_header(self, data):
        print '<<AMQP HEADER v%d.%d>>' % (ord(data[-2]), ord(data[-1]))

    def expect_remote_capabilities(self, data):
        pass

    def expect_login(self, data):
        pass


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
        self.amqp = AMQPConnection()

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
            self.amqp.handle_recv(data)
            self.csockinfo.sock.send(data)
        else:
            print self.strc, ">>", self.strf
            self.amqp.handle_send(data)
            self.fwdsock.send(data)
        self.print_data(data)


class ServerProxy:
    def __init__(self, addr):
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
                    data = sock.recv(conn.amqp.recv_next)
                except socket.error, e:
                    print e
                    data = ''
                if not len(data):
                    self.handle_close(conn)
                    break
                conn.handle_data(sock, data)

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

