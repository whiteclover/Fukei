#!/usr/bin/env python

from tornado import iostream
from tornado import ioloop
import socket
import logging
import struct
import errno
import functools
from tornado import stack_context
import os

from fukei.utils import socket_bind_np
socket_bind_np()


logger = logging.getLogger('connection.base')


class Socks5Connection(object):

    COMMAND_MAP = {
        0x01:   'CONNECT',
        0x02:   'BIND',
        0x03:   'UDP ASSOCIATION'
    }
    ACCEPTED_COMMANDS = [0x01, ]
    ADDRESS_TYPE_MAP = {
        0x01:   'IPv4 Address',
        0x03:   'Domain name',
        0x04:   'IPv6 Address'
    }
    ADDRESS_TYPE_LENGTH = {
        0x01:   4,
        0x04:   16
    }
    ACCEPTED_ADDRESS_TYPES = [0x01, 0x03, 0x04]
    REPLY_CODES = {
        0x00:   'succeeded',
        0x01:   'general SOCKS server failure',
        0x02:   'connection not allowed by ruleset',
        0x03:   'Network unreachable',
        0x04:   'Host unreachable',
        0x05:   'Connection refused',
        0x06:   'TTL expired',
        0x07:   'Command not supported',
        0x08:   'Address type not supported',
        0x09:   "to X'FF' unassigned"
    }
    ERRNO_MAP = {
        errno.ECONNREFUSED:     0x05,
        errno.EHOSTUNREACH:     0x04,
        errno.ENETUNREACH:      0x03,
    }

    def __init__(self, stream, address, upstream_cls=None):
        self.stream = stream
        self.addr = address
        if upstream_cls is None:
            raise TypeError('a upstream is necessary')
        self.upstream_cls = upstream_cls
        self.on_connected()
        self.dest = None
        self.sent_reply = False


    def on_connected(self):
        logger.debug('start connect...')
        self.stream.set_close_callback(self.on_connection_close)
        self.stream.read_bytes(2, self.on_auth_num_methods)

    def on_connection_close(self):
        logger.debug("disconnected!")
        self.clean_upstream()

    def on_auth_num_methods(self, data):
        # ver + nmethods. ref: rfc1928. P3
        self.ver, self.auth_nmethods = struct.unpack("!BB", data)
        logger.debug("version: 0x%X, number of methods: %d" %
                     (self.ver, self.auth_nmethods))
        if self.ver != 0x05:
            logger.warning("version mismatch, closing connection!")
            self.stream.close()
        else:
            self.stream.read_bytes(self.auth_nmethods, self.on_auth_methods)

    def on_auth_methods(self, data):
        self.auth_methods = struct.unpack("B" * self.auth_nmethods, data)
        if 0x00 in self.auth_methods:
            self.stream.write(struct.pack("!BB", self.ver, 0x00))
            self.on_auth_finished()
        else:
            logger.warning("the client does not support \"no authentication\", \
                closing connection!")
            self.stream.close()

    def on_auth_finished(self):
        logger.debug("authentication finished.")
        self.wait_request()

    def wait_request(self):
        self.stream.read_bytes(4, self.on_request_cmd_address_type)

    def wait_for_domain_name(self):
        self.raw_dest_addr = ""
        self.stream.read_bytes(1, self.on_domain_name_num_octets)

    def on_domain_name_num_octets(self, data):
        self.raw_dest_addr += data
        num, = struct.unpack("!B", data)
        self.stream.read_bytes(num, self.on_domain_name_octets)

    def on_domain_name_octets(self, data):
        self.raw_dest_addr += data
        self.domain_name = data
        self.on_domain_name_complete()

    def on_domain_name_complete(self):
        logger.debug("parsed domain name: %s" % self.domain_name)
        self.dest_addr = self.domain_name
        self.wait_destination_port()

    def on_request_cmd_address_type(self, data):
        _ver, self.cmd, _rsv, self.atyp = struct.unpack("!BBBB", data)
        logger.debug("command: %s, address type: %s" % (
            self.COMMAND_MAP.get(self.cmd, "UNKNOWN COMMAND"),
            self.ADDRESS_TYPE_MAP.get(self.atyp, "UNKNOWN ADDRESS TYPE")))

        if self.cmd not in self.ACCEPTED_COMMANDS:
            self.write_reply(0x07)
            self.stream.close()

        if self.atyp not in self.ACCEPTED_ADDRESS_TYPES:
            self.write_reply(0x08)
            self.stream.close()

        if self.atyp in self.ADDRESS_TYPE_LENGTH:
            self.stream.read_bytes(self.ADDRESS_TYPE_LENGTH[self.atyp],
                                   self.on_request_fixed_length_address)
        else:
            self.wait_for_domain_name()

    def wait_destination_port(self):
        self.stream.read_bytes(2, self.on_destination_port)

    def convert_readable_address(self, addr):
        return socket.inet_ntop(socket.AF_INET if self.atyp == 0x01
                                else socket.AF_INET6, addr)

    def convert_machine_address(self, addr_type, addr):
        return socket.inet_pton(addr_type, addr)

    def on_request_fixed_length_address(self, data):
        self.raw_dest_addr = data
        self.dest_addr = self.convert_readable_address(data)
        logger.debug("received address: %s" % self.dest_addr)
        self.wait_destination_port()

    def on_destination_port(self, data):
        self.raw_dest_port = data
        port, = struct.unpack("!H", data)
        self.dest = (self.dest_addr, port)
        logger.debug("received port: %s" % port)
        self.on_request_received()

    def on_request_received(self):
        logger.info("received request: " + self.COMMAND_MAP[
            self.cmd] + ", destination: %s:%d" % self.dest)

        self.command_processors = {
            0x01:   self.do_connect,
        }
        self.command_processors[self.cmd]()

    def do_connect(self):

        self.upstream = self.upstream_cls(self.dest,
                                    socket.AF_INET6 if self.atyp == 0x04 else socket.AF_INET,
                                    self.on_upstream_connect, self.on_upstream_error,
                                    self.on_upstream_data, self.on_upstream_close)



    def on_upstream_connect(self, _dummy):
        addr_type = self.upstream.address_type
        addr = self.upstream.address
        logger.debug("upstream connected from %s:%d" % addr)
        src_addr = self.convert_machine_address(addr_type, addr[0])
        self.write_reply(0x00, src_addr + struct.pack("!H", addr[1]))

        on_finish = functools.partial(self.on_socks_data, finished=True)
        self.stream.read_until_close(on_finish, self.on_socks_data)

    def on_upstream_error(self, _dummy, no):
        logger.debug("upstream error: %s" % no)
        if not self.sent_reply:
            self.write_reply(self.ERRNO_MAP.get(no, 0x01))
        self.stream.close()

    def on_upstream_data(self, _dummy, data):
        try:
            self.stream.write(data)
            logger.debug("transported %d bytes of data from upstream." %
                         len(data))
        except IOError as e:
            logger.debug("cannot write: %s" % str(e))
            if self.upstream:
                self.upstream.close()

    def on_upstream_close(self, _dummy=None):
        self.stream.close()
        logger.debug("upstream closed.")
        self.clean_upstream()

    def clean_upstream(self):
        if getattr(self, "upstream", None):
            self.upstream.close()
            self.upstream = None

    def on_socks_data(self, data, finished=False):
        if data:
            self.upstream.write(data)
            logger.debug("transported %d bytes of data to upstream." %
                         len(data))

    def write_reply(self, code, data=None):
        address_type = self.atyp
        if data is None:
            if self.dest:
                data = self.raw_dest_addr + self.raw_dest_port
            else:
                data = struct.pack("!BLH", 0x01, 0x00, 0x00)
        else:
            if self.atyp == 0x03:
                address_type = 0x01
        self.stream.write(struct.pack("!BBBB", self.ver, code, 0x00, address_type
                                      ) + data)
        logger.debug("sent reply: %s" % (self.REPLY_CODES.get(
            code, "UNKNOWN REPLY")))
        self.sent_reply = True
