#!/usr/bin/env python


from .base import Socks5Connection

from fukei.config import Config
import socket
import logging 

logger = logging.getLogger('connection.local')

class LocalConnection(Socks5Connection):

    """LocalSocksServer"""

    # def __init__(self, stream, address, upstream_cls=None)

    #     super(LocalConncection, self).__init__(stream, address, upstream_cls)

    def on_connected(self):
        logger.debug('start connect...')
        self.stream.set_close_callback(self.on_connection_close)
        self.stream.read_bytes(2, self.on_auth_num_methods)


    def do_connect(self):
    	config = Config.current()
        logger.error( "add type : %s " % socket.AF_INET)

        self.upstream = self.upstream_cls((config.server, config.server_port),
                            socket.AF_INET,
                            self.on_upstream_connect, self.on_upstream_error,
                            self.on_upstream_data, self.on_upstream_close)

    def on_upstream_connect(self, _dummy):
        self.write_reply(0x00, socket.inet_aton('0.0.0.0') + struct.pack("!H", config.server_port))
        on_finish = functools.partial(self.on_socks_data, finished=True)
        #self.upstream.write()
        self.stream.read_until_close(on_finish, self.on_socks_data)