#!/usr/bin/env python


from .base import Socks5Connection
import socket
import struct
import functools
import logging

logger = logging.getLogger('connection.remote')


class RemoteConnection(Socks5Connection):

    """RemoteConnection"""

    def __init__(self, stream, address, upstream_cls=None):
        self.cmd = 0x01
        self.ver = 0x05
        Socks5Connection.__init__(self, stream, address, upstream_cls)

    def on_connected(self):
        self.stream.read_bytes(1, self.on_request)

    def on_request(self, data):
        self.atyp, = struct.unpack('!B', data)
        logger.debug(" remote address type: %s" % (
            self.ADDRESS_TYPE_MAP.get(self.atyp, "UNKNOWN ADDRESS TYPE")))

        if self.atyp not in self.ACCEPTED_ADDRESS_TYPES:
            self.write_reply(0x08)
            self.stream.close()

        if self.atyp in self.ADDRESS_TYPE_LENGTH:
            self.stream.read_bytes(self.ADDRESS_TYPE_LENGTH[self.atyp],
                                   self.on_request_fixed_length_address)
        else:
            self.wait_for_domain_name()

    def do_connect(self):
        self.upstream = self.upstream_cls(self.dest,
                    socket.AF_INET6 if self.atyp == 0x04 else socket.AF_INET,
                    self.on_upstream_connect, self.on_upstream_error,
                    self.on_upstream_data, self.on_upstream_close)

    def on_upstream_connect(self, _dummy):
        logger.debug("upstream connected from %s:%d" % self.upstream.address)

        on_finish = functools.partial(self.on_socks_data, finished=True)
        self.stream.read_until_close(on_finish, self.on_socks_data)

    def write_reply(self, code, data=None):
        # do nothing remote server request
        pass
