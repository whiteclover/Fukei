
from .base import Upstream
from tornado.iostream import IOStream
import socket
import logging
import functools

logger = logging.getLogger('upstream.remote')


class RemoteUpstream(Upstream):

    """
    The most methods are the same in LocalUpstream, but maybe in future
    need to be diffrent.

    """

    def initialize(self):
        self.socket = socket.socket(self._address_type, socket.SOCK_STREAM)
        self.stream = IOStream(self.socket)
        self.stream.set_close_callback(self.on_close)

    def do_connect(self):
        self.stream.connect(self.dest, self.on_connect)

    @property
    def address(self):
        return self.socket.getsockname()

    @property
    def address_type(self):
        return self._address_type

    def on_connect(self):

        self.connection_callback(self)
        on_finish = functools.partial(self.on_streaming_data, finished=True)
        self.stream.read_until_close(on_finish, self.on_streaming_data)

    def on_close(self):
        if self.stream.error:
            self.error_callback(self, self.stream.error)
        else:
            self.close_callback(self)

    def on_streaming_data(self, data, finished=False):
        if len(data):
            self.streaming_callback(self, data, finished)

    def do_write(self, data):
        try:
            self.stream.write(data)
        except IOError as e:
            self.close()

    def do_close(self):
        if self.socket:
            logger.debug("close upstream: %s" % self.socket)
            self.stream.close()
