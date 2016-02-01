#!/usr/bin/env python
from stream import *


class AMQPProtocol:
    SIG_TO_DATA_TYPE = {
        'b': DT_OCTET_SIGNED,
        'B': DT_OCTET,
        'U': DT_SHORT_SIGNED,
        'u': DT_SHORT,
        'I': DT_LONG_SIGNED,
        'i': DT_LONG,
        'L': DT_LONGLONG_SIGNED,
        'l': DT_LONGLONG,
        'D': DT_DECIMAL,
        'T': DT_TIMESTAMP,
        'V': DT_VOID,
        't': DT_BOOL,
        's': DT_STRING_SHORT,
        'S': DT_STRING_LONG,
        'A': DT_ARRAY,
        'F': DT_TABLE,
    }
    FRAME_TYPE_METHOD = 0x01
    FRAME_TYPE_HEADER = 0x02
    FRAME_TYPE_BODY = 0x03
    FRAME_TYPE_HEARTBEAT = 0x08
    FRAME_TYPES = {
        FRAME_TYPE_METHOD: 'method frame',
        FRAME_TYPE_HEADER: 'header frame',
        FRAME_TYPE_BODY: 'body frame',
        FRAME_TYPE_HEARTBEAT: 'heartbeat frame',
    }
    CLASS_METHODS = {}

    def __init__(self):
        self.DATA_TYPE_TO_SIG = {}
        for sig, dt in self.SIG_TO_DATA_TYPE.iteritems():
            self.DATA_TYPE_TO_SIG[dt] = sig
        pass

    def read_frame(self, reader):
        frame_type = reader.read_octet()
        if frame_type not in self.FRAME_TYPES:
            return 'UNKNOWN FRAME TYPE 0x%X' % frame_type

        if frame_type == AMQPProtocol.FRAME_TYPE_METHOD:
            return self.read_method_frame(frame_type, reader)
        elif frame_type == AMQPProtocol.FRAME_TYPE_HEADER:
            return self.read_header_frame(frame_type, reader)
        elif frame_type == AMQPProtocol.FRAME_TYPE_BODY:
            return self.read_body_frame(frame_type, reader)
        elif frame_type == AMQPProtocol.FRAME_TYPE_HEARTBEAT:
            return self.read_heartbeat_frame(frame_type, reader)

    def read_method_arguments(self, reader, arguments):
        result = []
        for argument in arguments:
            if isinstance(argument[0], list):
                if argument[1] == DT_BOOL:
                    flags = 0
                    num_bits = 0
                    for arg_name in argument[0]:
                        if num_bits == 0:
                            flags = reader.read_octet()
                            num_bits = 8
                        result.append((arg_name, (flags & 1) == 1))
                        flags >>= 1
                        num_bits -= 1
                else:
                    raise Exception('Non boolean concatenation attempt.')
            else:
                result.append((argument[0], (self.DATA_TYPE_TO_SIG[argument[1]], reader.read(argument[1]))))
        return result

    def read_method_frame(self, frame_type, reader):
        channel = reader.read_short()
        frame_size = reader.read_long()
        class_id = reader.read_short()
        method_id = reader.read_short()
        known_class = class_id in self.CLASS_METHODS
        known_method = known_class and (method_id in self.CLASS_METHODS[class_id]['methods'])
        if known_method:
            arguments = self.read_method_arguments(reader, self.CLASS_METHODS[class_id]['methods'][method_id]['arguments'])
        else:
            arguments = None
            reader.skip(frame_size - 4)
        reader.read_octet()  # FRAME_END
        class_name = self.CLASS_METHODS[class_id]['name'] if known_class else 'UNKNOWN'
        method_name = self.CLASS_METHODS[class_id]['methods'][method_id]['name'] if known_method else 'UNKNOWN'
        result = [
            '%s: %s.%s [channel: %d, size: %d]' % (self.FRAME_TYPES[frame_type], class_name, method_name, channel, frame_size),
        ]
        if arguments:
            result.append('arguments:')
            for name, value in arguments:
                result.append(' - %s = %s' % (name, repr(value)))
        return "\n".join(result)

    def read_header_frame(self, frame_type, reader):
        channel = reader.read_short()
        frame_size = reader.read_long()
        class_id = reader.read_short()
        weight = reader.read_short()
        reader.skip(frame_size - 4)
        reader.read_octet()  # FRAME_END
        class_name = 'UNKNOWN'
        if class_id in self.CLASS_METHODS:
            class_name = self.CLASS_METHODS[class_id]['name']
        return '%s, channel: %d, size: %d, weight: %d, class: %s' % (self.FRAME_TYPES[frame_type], channel, frame_size, weight, class_name)

    def read_body_frame(self, frame_type, reader):
        channel = reader.read_short()
        frame_size = reader.read_long()
        payload = reader.read_raw(frame_size)
        reader.read_octet()  # FRAME_END
        return "%s, channel: %d, payload size: %d,\nPayload: %s" % (self.FRAME_TYPES[frame_type], channel, frame_size, payload)

    def read_heartbeat_frame(self, frame_type, reader):
        return '%s' % (self.FRAME_TYPES[frame_type])
