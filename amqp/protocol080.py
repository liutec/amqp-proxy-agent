#!/usr/bin/env python

# AUTO GENERATED WITH 'parse.py amqp-rabbitmq-0.8.json'

from stream import *
from protocol import AMQPProtocol


class AMQPProtocol080(AMQPProtocol):
    HEADER = b'AMQP\x01\x01\x08\x00'
    FRAME_OOB_METHOD = 0x4
    FRAME_OOB_HEADER = 0x5
    FRAME_OOB_BODY = 0x6
    FRAME_TRACE = 0x7
    FRAME_MIN_SIZE = 0x1000
    FRAME_END = 0xCE
    REPLY_SUCCESS = 0xC8
    NOT_DELIVERED = 0x136
    CONTENT_TOO_LARGE = 0x137
    NO_ROUTE = 0x138
    NO_CONSUMERS = 0x139
    ACCESS_REFUSED = 0x193
    NOT_FOUND = 0x194
    RESOURCE_LOCKED = 0x195
    PRECONDITION_FAILED = 0x196
    CONNECTION_FORCED = 0x140
    INVALID_PATH = 0x192
    FRAME_ERROR = 0x1F5
    SYNTAX_ERROR = 0x1F6
    COMMAND_INVALID = 0x1F7
    CHANNEL_ERROR = 0x1F8
    UNEXPECTED_FRAME = 0x1F9
    RESOURCE_ERROR = 0x1FA
    NOT_ALLOWED = 0x212
    NOT_IMPLEMENTED = 0x21C
    INTERNAL_ERROR = 0x21D
    SOFT_ERROR = {
        NOT_DELIVERED: 'Not delivered.',
        CONTENT_TOO_LARGE: 'Content too large.',
        NO_ROUTE: 'No route.',
        NO_CONSUMERS: 'No consumers.',
        ACCESS_REFUSED: 'Access refused.',
        NOT_FOUND: 'Not found.',
        RESOURCE_LOCKED: 'Resource locked.',
        PRECONDITION_FAILED: 'Precondition failed.',
    }
    HARD_ERROR = {
        CONNECTION_FORCED: 'Connection forced.',
        INVALID_PATH: 'Invalid path.',
        FRAME_ERROR: 'Frame error.',
        SYNTAX_ERROR: 'Syntax error.',
        COMMAND_INVALID: 'Command invalid.',
        CHANNEL_ERROR: 'Channel error.',
        UNEXPECTED_FRAME: 'Unexpected frame.',
        RESOURCE_ERROR: 'Resource error.',
        NOT_ALLOWED: 'Not allowed.',
        NOT_IMPLEMENTED: 'Not implemented.',
        INTERNAL_ERROR: 'Internal error.',
    }
    CLASS_METHODS = {
        0xA: {
            'name': 'connection',
            'properties': [],
            'methods': {
                0xA: {
                    'name': 'start',
                    'arguments': [
                        ('version_major', DT_OCTET, 0),
                        ('version_minor', DT_OCTET, 8),
                        ('peer_properties', DT_TABLE, None),
                        ('mechanisms', DT_STRING_LONG, 'PLAIN'),
                        ('locales', DT_STRING_LONG, 'en_US'),
                    ]
                },
                0xB: {
                    'name': 'start_ok',
                    'arguments': [
                        ('peer_properties', DT_TABLE, None),
                        ('mechanism', DT_STRING_SHORT, 'PLAIN'),
                        ('response', DT_STRING_LONG, None),
                        ('locale', DT_STRING_SHORT, 'en_US'),
                    ]
                },
                0x14: {
                    'name': 'secure',
                    'arguments': [
                        ('challenge', DT_STRING_LONG, None),
                    ]
                },
                0x15: {
                    'name': 'secure_ok',
                    'arguments': [
                        ('response', DT_STRING_LONG, None),
                    ]
                },
                0x1E: {
                    'name': 'tune',
                    'arguments': [
                        ('channel_max', DT_SHORT, 0),
                        ('frame_max', DT_LONG, 0),
                        ('heartbeat', DT_SHORT, 0),
                    ]
                },
                0x1F: {
                    'name': 'tune_ok',
                    'arguments': [
                        ('channel_max', DT_SHORT, 0),
                        ('frame_max', DT_LONG, 0),
                        ('heartbeat', DT_SHORT, 0),
                    ]
                },
                0x28: {
                    'name': 'open',
                    'arguments': [
                        ('virtual_host', DT_STRING_SHORT, '/'),
                        ('capabilities', DT_STRING_SHORT, ''),
                        ('insist', DT_BOOL, False),
                    ]
                },
                0x29: {
                    'name': 'open_ok',
                    'arguments': [
                        ('known_hosts', DT_STRING_SHORT, ''),
                    ]
                },
                0x32: {
                    'name': 'redirect',
                    'arguments': [
                        ('host', DT_STRING_SHORT, None),
                        ('known_hosts', DT_STRING_SHORT, ''),
                    ]
                },
                0x3C: {
                    'name': 'close',
                    'arguments': [
                        ('reply_code', DT_SHORT, None),
                        ('reply_text', DT_STRING_SHORT, ''),
                        ('class_id', DT_SHORT, None),
                        ('method_id', DT_SHORT, None),
                    ]
                },
                0x3D: {
                    'name': 'close_ok',
                    'arguments': [],
                },
            },
        },
        0x14: {
            'name': 'channel',
            'methods': {
                0xA: {
                    'name': 'open',
                    'arguments': [
                        ('out_of_band', DT_STRING_SHORT, ''),
                    ]
                },
                0xB: {
                    'name': 'open_ok',
                    'arguments': [],
                },
                0x14: {
                    'name': 'flow',
                    'arguments': [
                        ('active', DT_BOOL, None),
                    ]
                },
                0x15: {
                    'name': 'flow_ok',
                    'arguments': [
                        ('active', DT_BOOL, None),
                    ]
                },
                0x1E: {
                    'name': 'alert',
                    'arguments': [
                        ('reply_code', DT_SHORT, None),
                        ('reply_text', DT_STRING_SHORT, ''),
                        ('details', DT_TABLE, {}),
                    ]
                },
                0x28: {
                    'name': 'close',
                    'arguments': [
                        ('reply_code', DT_SHORT, None),
                        ('reply_text', DT_STRING_SHORT, ''),
                        ('class_id', DT_SHORT, None),
                        ('method_id', DT_SHORT, None),
                    ]
                },
                0x29: {
                    'name': 'close_ok',
                    'arguments': [],
                },
            },
        },
        0x1E: {
            'name': 'access',
            'methods': {
                0xA: {
                    'name': 'request',
                    'arguments': [
                        ('realm', DT_STRING_SHORT, '/data'),
                        (['exclusive', 'passive', 'active', 'write', 'read'], DT_BOOL, [False, True, True, True, True]),
                        ('read', DT_BOOL, True),
                    ]
                },
                0xB: {
                    'name': 'request_ok',
                    'arguments': [
                        ('ticket', DT_SHORT, 1),
                    ]
                },
            },
        },
        0x28: {
            'name': 'exchange',
            'methods': {
                0xA: {
                    'name': 'declare',
                    'arguments': [
                        ('ticket', DT_SHORT, 1),
                        ('exchange', DT_STRING_SHORT, None),
                        ('type', DT_STRING_SHORT, 'direct'),
                        (['passive', 'durable', 'auto_delete', 'internal', 'nowait'], DT_BOOL, [False, False, False, False, False]),
                        ('arguments', DT_TABLE, {}),
                    ]
                },
                0xB: {
                    'name': 'declare_ok',
                    'arguments': [],
                },
                0x14: {
                    'name': 'delete',
                    'arguments': [
                        ('ticket', DT_SHORT, 1),
                        ('exchange', DT_STRING_SHORT, None),
                        (['if_unused', 'nowait'], DT_BOOL, [False, False]),
                        ('nowait', DT_BOOL, False),
                    ]
                },
                0x15: {
                    'name': 'delete_ok',
                    'arguments': [],
                },
            },
        },
        0x32: {
            'name': 'queue',
            'methods': {
                0xA: {
                    'name': 'declare',
                    'arguments': [
                        ('ticket', DT_SHORT, 1),
                        ('queue', DT_STRING_SHORT, ''),
                        (['passive', 'durable', 'exclusive', 'auto_delete', 'nowait'], DT_BOOL, [False, False, False, False, False]),
                        ('arguments', DT_TABLE, {}),
                    ]
                },
                0xB: {
                    'name': 'declare_ok',
                    'arguments': [
                        ('queue', DT_STRING_SHORT, None),
                        ('message_count', DT_LONG, None),
                        ('consumer_count', DT_LONG, None),
                    ]
                },
                0x14: {
                    'name': 'bind',
                    'arguments': [
                        ('ticket', DT_SHORT, 1),
                        ('queue', DT_STRING_SHORT, ''),
                        ('exchange', DT_STRING_SHORT, None),
                        ('routing_key', DT_STRING_SHORT, ''),
                        ('arguments', DT_TABLE, {}),
                    ]
                },
                0x15: {
                    'name': 'bind_ok',
                    'arguments': [],
                },
                0x1E: {
                    'name': 'purge',
                    'arguments': [
                        ('ticket', DT_SHORT, 1),
                        ('queue', DT_STRING_SHORT, ''),
                        ('nowait', DT_BOOL, False),
                    ]
                },
                0x1F: {
                    'name': 'purge_ok',
                    'arguments': [
                        ('message_count', DT_LONG, None),
                    ]
                },
                0x28: {
                    'name': 'delete',
                    'arguments': [
                        ('ticket', DT_SHORT, 1),
                        ('queue', DT_STRING_SHORT, ''),
                        (['if_unused', 'if_empty', 'nowait'], DT_BOOL, [False, False, False]),
                        ('nowait', DT_BOOL, False),
                    ]
                },
                0x29: {
                    'name': 'delete_ok',
                    'arguments': [
                        ('message_count', DT_LONG, None),
                    ]
                },
                0x32: {
                    'name': 'unbind',
                    'arguments': [
                        ('ticket', DT_SHORT, 1),
                        ('queue', DT_STRING_SHORT, ''),
                        ('exchange', DT_STRING_SHORT, None),
                        ('routing_key', DT_STRING_SHORT, ''),
                        ('arguments', DT_TABLE, {}),
                    ]
                },
                0x33: {
                    'name': 'unbind_ok',
                    'arguments': [],
                },
            },
        },
        0x3C: {
            'name': 'basic',
            'properties': [
                ('content_type', DT_STRING_SHORT, None),
                ('content_encoding', DT_STRING_SHORT, None),
                ('headers', DT_TABLE, None),
                ('delivery_mode', DT_OCTET, None),
                ('priority', DT_OCTET, None),
                ('correlation_id', DT_STRING_SHORT, None),
                ('reply_to', DT_STRING_SHORT, None),
                ('expiration', DT_STRING_SHORT, None),
                ('message_id', DT_STRING_SHORT, None),
                ('timestamp', DT_TIMESTAMP, None),
                ('type', DT_STRING_SHORT, None),
                ('user_id', DT_STRING_SHORT, None),
                ('app_id', DT_STRING_SHORT, None),
                ('cluster_id', DT_STRING_SHORT, None),
            ],
            'methods': {
                0xA: {
                    'name': 'qos',
                    'arguments': [
                        ('prefetch_size', DT_LONG, 0),
                        ('prefetch_count', DT_SHORT, 0),
                        ('global', DT_BOOL, False),
                    ]
                },
                0xB: {
                    'name': 'qos_ok',
                    'arguments': [],
                },
                0x14: {
                    'name': 'consume',
                    'arguments': [
                        ('access_ticket', DT_SHORT, 1),
                        ('queue', DT_STRING_SHORT, ''),
                        ('consumer_tag', DT_STRING_SHORT, ''),
                        (['no_local', 'no_ack', 'exclusive', 'nowait'], DT_BOOL, [False, False, False, False]),
                        ('nowait', DT_BOOL, False),
                    ]
                },
                0x15: {
                    'name': 'consume_ok',
                    'arguments': [
                        ('consumer_tag', DT_STRING_SHORT, None),
                    ]
                },
                0x1E: {
                    'name': 'cancel',
                    'arguments': [
                        ('consumer_tag', DT_STRING_SHORT, None),
                        ('nowait', DT_BOOL, False),
                    ]
                },
                0x1F: {
                    'name': 'cancel_ok',
                    'arguments': [
                        ('consumer_tag', DT_STRING_SHORT, None),
                    ]
                },
                0x28: {
                    'name': 'publish',
                    'arguments': [
                        ('ticket', DT_SHORT, 1),
                        ('exchange', DT_STRING_SHORT, ''),
                        ('routing_key', DT_STRING_SHORT, ''),
                        (['mandatory', 'immediate'], DT_BOOL, [False, False]),
                        ('immediate', DT_BOOL, False),
                    ]
                },
                0x32: {
                    'name': 'return',
                    'arguments': [
                        ('reply_code', DT_SHORT, None),
                        ('reply_text', DT_STRING_SHORT, ''),
                        ('exchange', DT_STRING_SHORT, None),
                        ('routing_key', DT_STRING_SHORT, None),
                    ]
                },
                0x3C: {
                    'name': 'deliver',
                    'arguments': [
                        ('consumer_tag', DT_STRING_SHORT, None),
                        ('delivery_tag', DT_LONGLONG, None),
                        ('exchange', DT_STRING_SHORT, None),
                        ('routing_key', DT_STRING_SHORT, None),
                    ]
                },
                0x46: {
                    'name': 'get',
                    'arguments': [
                        ('ticket', DT_SHORT, 1),
                        ('queue', DT_STRING_SHORT, ''),
                        ('no_ack', DT_BOOL, False),
                    ]
                },
                0x47: {
                    'name': 'get_ok',
                    'arguments': [
                        ('delivery_tag', DT_LONGLONG, None),
                        ('exchange', DT_STRING_SHORT, None),
                        ('routing_key', DT_STRING_SHORT, None),
                        ('message_count', DT_LONG, None),
                    ]
                },
                0x48: {
                    'name': 'get_empty',
                    'arguments': [
                        ('cluster_id', DT_STRING_SHORT, ''),
                    ]
                },
                0x50: {
                    'name': 'ack',
                    'arguments': [
                        ('delivery_tag', DT_LONGLONG, 0),
                        ('multiple', DT_BOOL, False),
                    ]
                },
                0x5A: {
                    'name': 'reject',
                    'arguments': [
                        ('delivery_tag', DT_LONGLONG, None),
                        ('requeue', DT_BOOL, True),
                    ]
                },
                0x64: {
                    'name': 'recover_async',
                    'arguments': [
                        ('requeue', DT_BOOL, False),
                    ]
                },
                0x6E: {
                    'name': 'recover',
                    'arguments': [
                        ('requeue', DT_BOOL, False),
                    ]
                },
                0x6F: {
                    'name': 'recover_ok',
                    'arguments': [],
                },
            },
        },
        0x46: {
            'name': 'file',
            'properties': [
                ('content_type', DT_STRING_SHORT, None),
                ('content_encoding', DT_STRING_SHORT, None),
                ('headers', DT_TABLE, None),
                ('priority', DT_OCTET, None),
                ('reply_to', DT_STRING_SHORT, None),
                ('message_id', DT_STRING_SHORT, None),
                ('filename', DT_STRING_SHORT, None),
                ('timestamp', DT_TIMESTAMP, None),
                ('cluster_id', DT_STRING_SHORT, None),
            ],
            'methods': {
                0xA: {
                    'name': 'qos',
                    'arguments': [
                        ('prefetch_size', DT_LONG, 0),
                        ('prefetch_count', DT_SHORT, 0),
                        ('global', DT_BOOL, False),
                    ]
                },
                0xB: {
                    'name': 'qos_ok',
                    'arguments': [],
                },
                0x14: {
                    'name': 'consume',
                    'arguments': [
                        ('ticket', DT_SHORT, 1),
                        ('queue', DT_STRING_SHORT, ''),
                        ('consumer_tag', DT_STRING_SHORT, ''),
                        (['no_local', 'no_ack', 'exclusive', 'nowait'], DT_BOOL, [False, False, False, False]),
                        ('nowait', DT_BOOL, False),
                    ]
                },
                0x15: {
                    'name': 'consume_ok',
                    'arguments': [
                        ('consumer_tag', DT_STRING_SHORT, None),
                    ]
                },
                0x1E: {
                    'name': 'cancel',
                    'arguments': [
                        ('consumer_tag', DT_STRING_SHORT, None),
                        ('nowait', DT_BOOL, False),
                    ]
                },
                0x1F: {
                    'name': 'cancel_ok',
                    'arguments': [
                        ('consumer_tag', DT_STRING_SHORT, None),
                    ]
                },
                0x28: {
                    'name': 'open',
                    'arguments': [
                        ('identifier', DT_STRING_SHORT, None),
                        ('content_size', DT_LONGLONG, None),
                    ]
                },
                0x29: {
                    'name': 'open_ok',
                    'arguments': [
                        ('staged_size', DT_LONGLONG, None),
                    ]
                },
                0x32: {
                    'name': 'stage',
                    'arguments': [],
                },
                0x3C: {
                    'name': 'publish',
                    'arguments': [
                        ('ticket', DT_SHORT, 1),
                        ('exchange', DT_STRING_SHORT, ''),
                        ('routing_key', DT_STRING_SHORT, ''),
                        (['mandatory', 'immediate'], DT_BOOL, [False, False]),
                        ('identifier', DT_STRING_SHORT, None),
                    ]
                },
                0x46: {
                    'name': 'return',
                    'arguments': [
                        ('reply_code', DT_SHORT, 200),
                        ('reply_text', DT_STRING_SHORT, ''),
                        ('exchange', DT_STRING_SHORT, None),
                        ('routing_key', DT_STRING_SHORT, None),
                    ]
                },
                0x50: {
                    'name': 'deliver',
                    'arguments': [
                        ('consumer_tag', DT_STRING_SHORT, None),
                        ('delivery_tag', DT_LONGLONG, None),
                        ('exchange', DT_STRING_SHORT, None),
                        ('routing_key', DT_STRING_SHORT, None),
                        ('identifier', DT_STRING_SHORT, None),
                    ]
                },
                0x5A: {
                    'name': 'ack',
                    'arguments': [
                        ('delivery_tag', DT_LONGLONG, 0),
                        ('multiple', DT_BOOL, False),
                    ]
                },
                0x64: {
                    'name': 'reject',
                    'arguments': [
                        ('delivery_tag', DT_LONGLONG, None),
                        ('requeue', DT_BOOL, True),
                    ]
                },
            },
        },
        0x50: {
            'name': 'stream',
            'properties': [
                ('content_type', DT_STRING_SHORT, None),
                ('content_encoding', DT_STRING_SHORT, None),
                ('headers', DT_TABLE, None),
                ('priority', DT_OCTET, None),
                ('timestamp', DT_TIMESTAMP, None),
            ],
            'methods': {
                0xA: {
                    'name': 'qos',
                    'arguments': [
                        ('prefetch_size', DT_LONG, 0),
                        ('prefetch_count', DT_SHORT, 0),
                        ('consume_rate', DT_LONG, 0),
                        ('global', DT_BOOL, False),
                    ]
                },
                0xB: {
                    'name': 'qos_ok',
                    'arguments': [],
                },
                0x14: {
                    'name': 'consume',
                    'arguments': [
                        ('ticket', DT_SHORT, 1),
                        ('queue', DT_STRING_SHORT, ''),
                        ('consumer_tag', DT_STRING_SHORT, ''),
                        (['no_local', 'exclusive', 'nowait'], DT_BOOL, [False, False, False]),
                        ('nowait', DT_BOOL, False),
                    ]
                },
                0x15: {
                    'name': 'consume_ok',
                    'arguments': [
                        ('consumer_tag', DT_STRING_SHORT, None),
                    ]
                },
                0x1E: {
                    'name': 'cancel',
                    'arguments': [
                        ('consumer_tag', DT_STRING_SHORT, None),
                        ('nowait', DT_BOOL, False),
                    ]
                },
                0x1F: {
                    'name': 'cancel_ok',
                    'arguments': [
                        ('consumer_tag', DT_STRING_SHORT, None),
                    ]
                },
                0x28: {
                    'name': 'publish',
                    'arguments': [
                        ('ticket', DT_SHORT, 1),
                        ('exchange', DT_STRING_SHORT, ''),
                        ('routing_key', DT_STRING_SHORT, ''),
                        (['mandatory', 'immediate'], DT_BOOL, [False, False]),
                        ('immediate', DT_BOOL, False),
                    ]
                },
                0x32: {
                    'name': 'return',
                    'arguments': [
                        ('reply_code', DT_SHORT, 200),
                        ('reply_text', DT_STRING_SHORT, ''),
                        ('exchange', DT_STRING_SHORT, None),
                        ('routing_key', DT_STRING_SHORT, None),
                    ]
                },
                0x3C: {
                    'name': 'deliver',
                    'arguments': [
                        ('consumer_tag', DT_STRING_SHORT, None),
                        ('delivery_tag', DT_LONGLONG, None),
                        ('exchange', DT_STRING_SHORT, None),
                        ('queue', DT_STRING_SHORT, None),
                    ]
                },
            },
        },
        0x5A: {
            'name': 'tx',
            'methods': {
                0xA: {
                    'name': 'select',
                    'arguments': [],
                },
                0xB: {
                    'name': 'select_ok',
                    'arguments': [],
                },
                0x14: {
                    'name': 'commit',
                    'arguments': [],
                },
                0x15: {
                    'name': 'commit_ok',
                    'arguments': [],
                },
                0x1E: {
                    'name': 'rollback',
                    'arguments': [],
                },
                0x1F: {
                    'name': 'rollback_ok',
                    'arguments': [],
                },
            },
        },
        0x64: {
            'name': 'dtx',
            'methods': {
                0xA: {
                    'name': 'select',
                    'arguments': [],
                },
                0xB: {
                    'name': 'select_ok',
                    'arguments': [],
                },
                0x14: {
                    'name': 'start',
                    'arguments': [
                        ('dtx_identifier', DT_STRING_SHORT, None),
                    ]
                },
                0x15: {
                    'name': 'start_ok',
                    'arguments': [],
                },
            },
        },
        0x6E: {
            'name': 'tunnel',
            'properties': [
                ('headers', DT_TABLE, None),
                ('proxy_name', DT_STRING_SHORT, None),
                ('data_name', DT_STRING_SHORT, None),
                ('durable', DT_OCTET, None),
                ('broadcast', DT_OCTET, None),
            ],
            'methods': {
                0xA: {
                    'name': 'request',
                    'arguments': [
                        ('meta_data', DT_TABLE, None),
                    ]
                },
            },
        },
        0x78: {
            'name': 'test',
            'methods': {
                0xA: {
                    'name': 'integer',
                    'arguments': [
                        ('integer_1', DT_OCTET, None),
                        ('integer_2', DT_SHORT, None),
                        ('integer_3', DT_LONG, None),
                        ('integer_4', DT_LONGLONG, None),
                        ('operation', DT_OCTET, None),
                    ]
                },
                0xB: {
                    'name': 'integer_ok',
                    'arguments': [
                        ('result', DT_LONGLONG, None),
                    ]
                },
                0x14: {
                    'name': 'string',
                    'arguments': [
                        ('string_1', DT_STRING_SHORT, None),
                        ('string_2', DT_STRING_LONG, None),
                        ('operation', DT_OCTET, None),
                    ]
                },
                0x15: {
                    'name': 'string_ok',
                    'arguments': [
                        ('result', DT_STRING_LONG, None),
                    ]
                },
                0x1E: {
                    'name': 'table',
                    'arguments': [
                        ('table', DT_TABLE, None),
                        ('integer_op', DT_OCTET, None),
                        ('string_op', DT_OCTET, None),
                    ]
                },
                0x1F: {
                    'name': 'table_ok',
                    'arguments': [
                        ('integer_result', DT_LONGLONG, None),
                        ('string_result', DT_STRING_LONG, None),
                    ]
                },
                0x28: {
                    'name': 'content',
                    'arguments': [],
                },
                0x29: {
                    'name': 'content_ok',
                    'arguments': [
                        ('content_checksum', DT_LONG, None),
                    ]
                },
            },
        },
    }
