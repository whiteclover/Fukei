import socket
import logging

import functools

logger = logging.getLogger('upstream.base')


class Upstream(object):

    """
    The Base Upstream class for handle data from remote
    and reply data to local , the callbacks are used for sending  the received data from remote to local

    """

    def __init__(self, dest, address_type, connection_callback,
                 error_callback, streaming_callbak, close_callback):
        assert address_type in [socket.AF_INET, socket.AF_INET6]
        self.dest = dest
        self._address_type = address_type
        self.connection_callback = connection_callback
        self.error_callback = error_callback
        self.streaming_callback = streaming_callbak
        self.close_callback = close_callback
        logger.debug("create a upstream on (%s, %s)" % dest)
        self.initialize()
        self.do_connect()

    def write(self, data):
        self.do_write(data)
        logger.debug("sent %d bytes of data." % len(data))

    def close(self):
        self.do_close()

    def initialize(self):
        """ 
        The more setting and attr bind before request.
        """
        pass

    def do_connect(self):
        raise NotImplemented("subclass of Upstream must implement do_connect")

    def do_close(self):
        raise NotImplemented("subclass of Upstream must implement do_close")

    def do_write(self, data):
        raise NotImplemented("subclass of Upstream must implement do_write")
