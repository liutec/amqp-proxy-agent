#!/usr/bin/env python
import sys
import json


def indent(tabs, text, tab_size=4):
    return ''.join([' ' * tabs * tab_size, text])


def lookahead(iterable):
    it = iter(iterable)
    last = next(it)
    for val in it:
        yield last, True
        last = val
    yield last, False


class AMQPSpecsParser:
    @staticmethod
    def parse_args(output, tabs, arguments, data_types, domains):
        arg_names = []
        arg_defaults = []
        for arg_specs, more in lookahead(arguments):
            if 'type' in arg_specs:
                arg_name = arg_specs['name']
                arg_type = data_types[arg_specs['type']]
            else:
                arg_name = arg_specs['domain']
                arg_type = data_types[domains[arg_specs['domain']]]
            arg_name = arg_name.replace('-', '_')
            arg_def = arg_specs['default-value'] if 'default-value' in arg_specs else None
            arg_default = repr(arg_def).replace('u\'', '\'')
            if arg_type == 'DT_BOOL':
                arg_names.append('\'%s\'' % arg_name)
                arg_defaults.append(arg_default)
                if more or len(arg_names) < 8:
                    continue
            num_args = len(arg_names)
            if num_args:
                if num_args > 1:
                    output += [
                        indent(tabs, '([%s], DT_BOOL, [%s]),' % (', '.join(arg_names), ', '.join(arg_defaults))),
                    ]
                arg_names = []
                arg_defaults = []
                if num_args > 1:
                    continue
            output += [
                indent(tabs, '(\'%s\', %s, %s),' % (arg_name, arg_type, arg_default)),
            ]

    def __init__(self, specs_file_name):
        with open(specs_file_name) as data_file:
            data = json.load(data_file)
        ver_nums = (data['major-version'], data['minor-version'], data['revision'])
        ver = ''.join([str(x) for x in ver_nums])
        output = [
            indent(0, '#!/usr/bin/env python'),
            '',
            indent(0, '# AUTO GENERATED WITH \'parse.py %s\'' % specs_file_name),
            '',
            indent(0, 'from stream import *'),
            indent(0, 'from protocol import AMQPProtocol'),
            '',
            '',
            indent(0, 'class AMQPProtocol%s(AMQPProtocol):' % ver),
            indent(1, 'HEADER = b\'AMQP\\x00' + ''.join(['\\x' + ('%X' % x).rjust(2, '0') for x in ver_nums]) + '\''),
        ]
        const_classes = {}
        for const_specs in data['constants']:
            const_name = const_specs['name'].replace('-', '_')
            if const_name in ['FRAME_METHOD', 'FRAME_HEADER', 'FRAME_BODY', 'FRAME_HEARTBEAT']:
                continue
            if 'class' in const_specs:
                const_cls = const_specs['class'].upper().replace('-', '_')
                if const_cls not in const_classes:
                    const_classes[const_cls] = [const_name]
                else:
                    const_classes[const_cls].append(const_name)
            output += [
                indent(1, '%s = 0x%X' % (const_name, const_specs['value'])),
            ]
        for const_cls, class_members in const_classes.iteritems():
            output += [
                indent(1, '%s = {' % const_cls),
            ]
            for class_member in class_members:
                output += [
                    indent(2, '%s: \'%s.\',' % (class_member, (class_member[0].upper() + class_member[1:].lower()).replace('_', ' '))),
                ]
            output += [
                indent(1, '}'),
            ]
        output += [
            indent(1, 'CLASS_METHODS = {'),
        ]
        data_types = {
            'octet': 'DT_OCTET',
            'table': 'DT_TABLE',
            'longstr': 'DT_STRING_LONG',
            'shortstr': 'DT_STRING_SHORT',
            'short': 'DT_SHORT',
            'long': 'DT_LONG',
            'bit': 'DT_BOOL',
            'longlong': 'DT_LONGLONG',
            'timestamp': 'DT_TIMESTAMP',
        }
        domains = {}
        for domain_spec in data['domains']:
            domains[domain_spec[0]] = domain_spec[1]
        for class_specs in data['classes']:
            output += [
                indent(2, '0x%X: {' % int(class_specs['id'])),
                indent(3, '\'name\': \'%s\',' % class_specs['name']),
            ]
            if 'properties' in class_specs:
                if len(class_specs['properties']) == 0:
                    output += [
                        indent(3, '\'properties\': [],'),
                    ]
                else:
                    output += [
                        indent(3, '\'properties\': ['),
                    ]
                    self.parse_args(output, 4, class_specs['properties'], data_types, domains)
                    output += [
                        indent(3, '],'),
                    ]
            output += [
                indent(3, '\'methods\': {'),
            ]
            for method_specs in class_specs['methods']:
                output += [
                    indent(4, '0x%X: {' % int(method_specs['id'])),
                    indent(5, '\'name\': \'%s\',' % method_specs['name'].replace('-', '_')),
                ]
                if len(method_specs['arguments']) == 0:
                    output += [
                        indent(5, '\'arguments\': [],'),
                    ]
                else:
                    output += [
                        indent(5, '\'arguments\': ['),
                    ]
                    self.parse_args(output, 6, method_specs['arguments'], data_types, domains)
                    output += [
                        indent(5, ']'),
                    ]
                output += [
                    indent(4, '},'),
                ]
            output += [
                indent(3, '},'),
                indent(2, '},'),
            ]
        output += [
            indent(1, '}'),
            '',
        ]
        output_file_name = '../protocol%s.py' % ver
        with open(output_file_name, "w") as output_file:
            output_file.write("\n".join(output))


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print "Usage:\n%s specs/amqp-rabbitmq-0.9.1.json\n" % sys.argv[0]
        exit(1)
    parser = AMQPSpecsParser(sys.argv[1])
    exit(0)
