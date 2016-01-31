#!/usr/bin/env python

from amqp.protocol080 import AMQPProtocol080
from amqp.protocol091 import AMQPProtocol091

KNOWN_PROTOCOLS = [AMQPProtocol080, AMQPProtocol091]
LOADED_PROTOCOLS = {}


def get_protocol(header):
    if header not in LOADED_PROTOCOLS:
        found = False
        for protocol_class in KNOWN_PROTOCOLS:
            if protocol_class.HEADER == header:
                LOADED_PROTOCOLS[header] = protocol_class()
                found = True
                break
        if not found:
            print header
            raise Exception('No protocol registered for header.')
    return LOADED_PROTOCOLS[header]
