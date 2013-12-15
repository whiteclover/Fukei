
import logging

try:
    from  json import loads
except:
    #handle the low python version < 2.6
    from  simplejson import loads



def json_loads(raw):
    def ascii_list(data):
        rv = []
        for item in data:
            if isinstance(item, unicode):
                item = item.encode('utf-8')
            elif isinstance(item, list):
                item = _decode_list(item)
            elif isinstance(item, dict):
                item = _decode_dict(item)
            rv.append(item)
        return rv

    def ascii_dict(data):
        rv = {}
        for key, value in data.iteritems():
            if isinstance(key, unicode):
                key = key.encode('utf-8')
            if isinstance(value, unicode):
                value = value.encode('utf-8')
            elif isinstance(value, list):
                value = ascii_list(value)
            elif isinstance(value, dict):
                value = ascii_dict(value)
            rv[key] = value
        return rv
    return loads(raw, object_hook= ascii_dict)


class lazy_property(object):

    """
    be used for lazy evaluation of an object attribute.
    property should represent non-mutable data, as it replaces itself.
    """

    def __init__(self, fget):
        self.func_name = fget.__name__
        self.fget = fget

    def __get__(self, obj, cls):
        if obj is None:
            return
        value = self.fget(obj)
        setattr(obj, self.func_name, value)
        return value


def import_classes(moudle_name, class_names):
    classes = []
    m = __import__(moudle_name, globals(), locals(), class_names)
    for c in class_names:
        classes.append(getattr(m, c))
    return classes


def import_class(module2cls):
    d = module2cls.rfind(".")
    classname = module2cls[d + 1: len(module2cls)]
    m = __import__(module2cls[0:d], globals(), locals(), [classname])
    return getattr(m, classname)


def log_config(tag, debug=False):
    """"
    be used for confguration log level and format
    >>> log_config('log_test', debug=True)
    >>> logger = logging.getLogger('utils')
    >>> logger.debug('test debug')
    >>> logger.info('test info')
    
    """
    logfmt = tag + \
        '[%%(process)d]: [%%(levelname)s] %s%%(message)s' % '%(name)s - '
    config = lambda x: logging.basicConfig(level=x, format='[%(asctime)s] ' + logfmt, datefmt='%Y%m%d %H:%M:%S')
    if debug:
        config(logging.DEBUG)
    else:
        config(logging.INFO)


import socket
import ctypes


class sockaddr(ctypes.Structure):
    _fields_ = [('sa_family', ctypes.c_short),
                ('__pad1', ctypes.c_ushort),
                ('ipv4_addr', ctypes.c_byte * 4),
                ('ipv6_addr', ctypes.c_byte * 16),
                ('__pad2', ctypes.c_ulong)]


WSAStringToAddressA = ctypes.windll.ws2_32.WSAStringToAddressA
WSAAddressToStringA = ctypes.windll.ws2_32.WSAAddressToStringA


def inet_pton(address_family, ip_string):
    """
    inet_pton for windows
    """
    addr = sockaddr()
    addr.sa_family = address_family
    addr_size = ctypes.c_int(ctypes.sizeof(addr))
    if WSAStringToAddressA(ip_string, address_family, None, ctypes.byref(addr), ctypes.byref(addr_size)) != 0:
        raise socket.error(ctypes.FormatError())
    if address_family == socket.AF_INET:
        return ctypes.string_at(addr.ipv4_addr, 4)
    if address_family == socket.AF_INET6:
        return ctypes.string_at(addr.ipv6_addr, 16)
    raise socket.error('unknown address family')


def inet_ntop(address_family, packed_ip):
    """
    inet_ntop for windows
    """
    addr = sockaddr()
    addr.sa_family = address_family
    addr_size = ctypes.c_int(ctypes.sizeof(addr))
    ip_string = ctypes.create_string_buffer(128)
    ip_string_size = ctypes.c_int(ctypes.sizeof(addr))
    if address_family == socket.AF_INET:
        if len(packed_ip) != ctypes.sizeof(addr.ipv4_addr):
            raise socket.error('packed IP wrong length for inet_ntoa')
        ctypes.memmove(addr.ipv4_addr, packed_ip, 4)
    elif address_family == socket.AF_INET6:
        if len(packed_ip) != ctypes.sizeof(addr.ipv6_addr):
            raise socket.error('packed IP wrong length for inet_ntoa')
        ctypes.memmove(addr.ipv6_addr, packed_ip, 16)
    else:
        raise socket.error('unknown address family')
    if WSAAddressToStringA(ctypes.byref(addr), addr_size, None, ip_string, ctypes.byref(ip_string_size)) != 0:
        raise socket.error(ctypes.FormatError())
    return ip_string[:ip_string_size.value]


def socket_bind_np():
    """
    if platform is windows need to bind custom inet_ntop and inet_pton in socket moudle
    """
    import sys
    import platform
    sock = sys.modules['socket']
    if platform.system() == 'Windows':
        setattr(sock, 'inet_pton', inet_pton)
        setattr(sock, 'inet_ntop', inet_ntop)


if __name__ == '__main__':
    import doctest
    doctest.testmod()
