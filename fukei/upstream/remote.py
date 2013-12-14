
from .base import Upstream
from tornado.iostream import IOStream

class RemoteUpstream(Upstream):

    """
    The most methods are the same in LocalUpstream, but maybe in future
    need to be diffrent.

    """

    def initialize(self):
        self.socket = socket.socket(self.address_type, socket.SOCK_STREAM)
        self.stream = IOStream(self.socket)
        self.stream.set_close_callback(self.on_close)

    def do_connect(self):
        self.stream.connect(self.dest, self.on_connect)

    @property
    def address(self):
        return self.socket.getsockname()

    @property
    def address_type(self):
        return self.address_type

    def on_connect(self):
        logger.debug("connected!")
        self.connection_callback()
        on_finish = functools.partial(self.on_streaming_data, finished=True)
        self.stream.read_until_close(on_finish, self.on_streaming_data)

    def on_close(self):
        if self.stream.error:
            logger.debug("closed due to error: " + str(self.stream.error))
            self.error_callback(self.stream.error)
        else:
            logger.debug("closed")
            self.close_callback()

    def on_streaming_data(self, data, finished=False):
        if len(data):
            logger.debug("received %d bytes of data." % len(data))
            self.streaming_callback(data)

    def do_write(self, data):
        self.stream.write(data)

    def do_close(self):
        self.stream.close()