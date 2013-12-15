#!/usr/bin/env python


from .base import Socks5Connection
import socket
import logging 

logger = logging.getLogger('connection.remote')

class RemoteConnection(Socks5Connection):

    """RemoteConnection"""

    def on_connected(self):
        logger.debug('start connect...')
        self.stream.set_close_callback(self.on_connection_close)
        if self.stream.iv_len: 
        	self.stream.read_bytes(self.stream.iv_len, self.wait_request)
        else:
        	self.wait_request()

    def do_connect(self):
        self.upstream = self.upstream_cls(self.dest,
                            socket.AF_INET6 if self.atyp == 0x04 else socket.AF_INET,
                            self.on_upstream_connect, self.on_upstream_error,
                            self.on_upstream_data, self.on_upstream_close)

    def on_upstream_connect(self, _dummy):
        
        logger.debug("upstream connected from %s:%d" % self.upstream.address)

        on_finish = functools.partial(self.on_socks_data, finished=True)
        self.stream.read_until_close(on_finish, self.on_socks_data)





