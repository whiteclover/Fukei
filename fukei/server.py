#!/usr/bin/env python

import tornado.ioloop
from tornado.tcpserver import TCPServer
from .connection import get_connection
from .upstream import get_streams
import logging

logger = logging.getLogger('server')


class Socks5Server(TCPServer):

    def __init__(self, connection_cls, streams, io_loop=None, **kwargs):
        self.connection_cls = connection_cls
        self.upstream_cls, self.stream_cls = streams
        TCPServer.__init__(self, io_loop=io_loop, **kwargs)

    def handle_stream(self, stream, address):
        self.connection_cls(stream, address, self.upstream_cls)

    def _handle_connection(self, connection, address):
        try:
            stream = self.stream_cls(connection, io_loop=self.io_loop, 
            	max_buffer_size=self.max_buffer_size)
            self.handle_stream(stream, address)
        except Exception:
            logger.error("Error in connection callback", exc_info=True)


class FukeiSocksServer(object):

    def __init__(self, side, config):
        self.side = 'remote' if side == 'server' else side
        if self.side == 'remote':
            self.address = config.server
            self.port = config.server_port
        else:
            self.address = '127.0.0.1'
            self.port = config.local_port

    def create_server(self, addr, port):
        connection_cls = get_connection(self.side)()
        streams = get_streams(self.side)()
        server = Socks5Server(connection_cls, streams)
        
        server.bind(port, address=addr, backlog=1024)
        return server

    def server_forever(self):
        try:
            logger.debug("Start Listening on %s:%s ...." % (self.address, self.port))
            self.server = self.create_server(self.address, self.port)
            self.server.start()
            tornado.ioloop.IOLoop.instance().start()
        except KeyboardInterrupt:
            tornado.ioloop.IOLoop.instance().stop()
        return 0
    run = server_forever

    def stop(self):
        return tornado.ioloop.IOLoop.instance().stop()
