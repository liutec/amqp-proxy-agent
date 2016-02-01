#!/usr/bin/env python
import struct

DT_OCTET_SIGNED = 0
DT_OCTET = 1
DT_SHORT_SIGNED = 2
DT_SHORT = 3
DT_LONG_SIGNED = 4
DT_LONG = 5
DT_LONGLONG_SIGNED = 6
DT_LONGLONG = 7
DT_DECIMAL = 8
DT_TIMESTAMP = 9
DT_VOID = 10
DT_BOOL = 11
DT_STRING_SHORT = 12
DT_STRING_LONG = 13
DT_ARRAY = 14
DT_TABLE = 15

DT_MAPPING = {
    DT_OCTET_SIGNED:    ('>b',  1, False),
    DT_OCTET:           ('>B',  1, False),
    DT_SHORT_SIGNED:    ('>h',  2, False),
    DT_SHORT:           ('>H',  2, False),
    DT_LONG_SIGNED:     ('>l',  4, False),
    DT_LONG:            ('>L',  4, False),
    DT_LONGLONG_SIGNED: ('>q',  8, False),
    DT_LONGLONG:        ('>Q',  8, False),
    DT_DECIMAL:         ('>Bl', 5, False),
    DT_TIMESTAMP:       ('>Q',  8, False),
    DT_VOID:            (None,  0, False),
    DT_STRING_SHORT:    ('>B',  1, True),
    DT_STRING_LONG:     ('>L',  4, True),
    DT_ARRAY:           ('>L',  4, True),
    DT_TABLE:           ('>L',  4, True),
    DT_BOOL:            ('?',   1, False),
}


class AMQPStreamReader:
    def __init__(self, data, dt_sig_map):
        self.offset = 0
        self.size = len(data)
        self.data = data
        self.dt_sig_map = dt_sig_map

    def eof(self):
        return self.offset >= self.size

    def reset(self):
        self.offset = 0
        return self.eof()

    def avail(self, size):
        return (self.offset + size) <= self.size

    def skip(self, size):
        self.offset += size
        return self.eof()

    def read(self, data_type, peek=False):
        if data_type in [DT_OCTET, DT_BOOL]:
            return self.read_octet(peek)
        if data_type not in DT_MAPPING:
            raise Exception('Invalid data type.')
        dt_info = DT_MAPPING[data_type]
        raw = self.read_raw(dt_info, peek)
        if data_type in [DT_STRING_SHORT, DT_STRING_LONG]:
            return ''.join(raw)
        elif data_type == DT_DECIMAL:
            return self.parse_decimal(raw)
        elif data_type == DT_ARRAY:
            return self.parse_array(raw)
        elif data_type == DT_TABLE:
            return self.parse_table(raw)
        else:
            return raw

    def read_raw(self, dt_info, peek=False):
        size = dt_info[1]
        if not dt_info[0] or not self.avail(size):
            return None
        result = struct.unpack(dt_info[0], self.data[self.offset:self.offset + size])[0]
        if dt_info[2]:
            size += result
            if not self.avail(size):
                if not peek:
                    self.offset += size
                return None
            result = self.data[self.offset + dt_info[1]:self.offset + size]
        if not peek:
            self.offset += size
        return result

    def read_char(self, peek=False):
        if not self.avail(1):
            return None
        result = self.data[self.offset]
        if not peek:
            self.offset += 1
        return result

    def read_octet(self, peek=False):
        if not self.avail(1):
            return None
        result = ord(self.data[self.offset])
        if not peek:
            self.offset += 1
        return result

    def read_short(self, peek=False):
        return self.read(DT_SHORT, peek)

    def read_long(self, peek=False):
        return self.read(DT_LONG, peek)

    @staticmethod
    def parse_decimal(raw):
        return raw[0] / (10 ** raw[1])

    def parse_array(self, raw):
        reader = AMQPStreamReader(raw, self.dt_sig_map)
        result = []
        while not reader.eof():
            dt_sig = reader.read_char()
            dt = self.dt_sig_map[dt_sig]
            value = reader.read(dt)
            result.append((dt_sig, value))
        return result

    def parse_table(self, raw):
        result = {}
        if not raw or len(raw) == 0:
            return result
        reader = AMQPStreamReader(raw, self.dt_sig_map)
        while not reader.eof():
            key = ''.join(reader.read(DT_STRING_SHORT))
            dt_sig = reader.read_char()
            dt = self.dt_sig_map[dt_sig]
            value = reader.read(dt)
            result[key] = (dt_sig, value)
        return result
