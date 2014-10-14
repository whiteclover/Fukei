#!/usr/bin/env python


from .base import Socks5Connection

from fukei.config import Config
import socket
import struct
import logging
import functools

logger = logging.getLogger('connection.local')


class LocalConnection(Socks5Connection):

    """LocalSocksServer"""

    def do_connect(self):
        config = Config.current()

        logger.debug("server : %s, %s" % (config.server, config.server_port))
        logger.debug("server dest: %s, %s" % self.dest)
        dest = (config.server, config.server_port)
        self.upstream = self.upstream_cls(dest, socket.AF_INET,
                    self.on_upstream_connect, self.on_upstream_error,
                    self.on_upstream_data, self.on_upstream_close)

    def on_upstream_connect(self, _dummy):
        config = Config.current()
        self.write_reply(0x00, socket.inet_aton('0.0.0.0')
                         + struct.pack("!H", config.server_port))
        self.write_request()
        on_finish = functools.partial(self.on_socks_data, finished=True)
        self.stream.read_until_close(on_finish, self.on_socks_data)

    def write_request(self, data=None):
        logger.debug('wait request...')
        address_type = self.atyp
        if data is None:
            if self.dest:
                data = self.raw_dest_addr + self.raw_dest_port
            else:
                data = struct.pack("!BLH", 0x01, 0x00, 0x00)
        else:
            if self.atyp == 0x03:
                address_type = 0x01
        self.upstream.write(struct.pack("!B", address_type) + data)
