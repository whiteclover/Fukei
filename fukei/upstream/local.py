
from .remote import RemoteUpstream
from tornado.iostream import IOStream
from fukei import crypto

class CryptoIOStream(IOStream):

    """CryptoIOStream overrive the `IOStrem#read_from_fd`
     `IOStrem#write_to_fd`for support encryption """

    def __init__(self, socket, *args, **kwargs):
        super(CryptoIOStream, self).__init__(socket, *args, **kwargs)
        self.crypto = crypto.new_crypto()

    def read_from_fd(self):
        chunk = super(CryptoIOStream, self).read_from_fd()
        return self.crypto.decrypt(chunk)

    def write_to_fd(self, data):
        data = self.crypto.encrypt(data)
        return super(CryptoIOStream, self).write_to_fd(data)

    @property
    def iv_len():
        return self.crypto.iv_len


class LocalUpstream(RemoteUpstream):

    def initialize(self):
        self.socket = socket.socket(self.address_type, socket.SOCK_STREAM)
        self.stream = CryptoIOStream(self.socket)
        self.stream.set_close_callback(self.on_close)
