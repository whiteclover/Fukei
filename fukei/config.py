#!/usr/bin/env python

    
import logging
import os.path
import sys
from argparse import ArgumentParser
from .utils import json_loads

logger = logging.getLogger('config')


class Config(dict):

    """Config  reads json file config firstly, then
      parses command line and override the file config settings

    >>> from utils import log_config
    >>> log_config('test_config', True)
    >>> config = Config()
    >>> config.server
    '127.0.0.1'
    >>> config['server']
    '127.0.0.1'
    >>> config.test_attr1 = 'test_attr1'
    >>> config.test_attr1
    'test_attr1'
    >>> config['test_attr1']
    'test_attr1'
    >>> config['test_attr2'] = 'test_attr2'
    >>> config.test_attr2
    'test_attr2'
    >>> config['test_attr2']
    'test_attr2'
    >>> config['test_attr2'] = 'new_test_attr2'
    >>> config['test_attr2']
    'new_test_attr2'

    """

    @staticmethod
    def current(default_path='path2json', args=sys.argv):
        if not hasattr(Config, '_current'):
            Config._current = Config(default_path, args)
        return Config._current
   

    def __init__(self,default_path='path2json', args=sys.argv) :

        super(Config, self).__init__()
        self.args = args
        self.default_path = default_path
        self.config_opt()

    def __getattr__(self, name):
        return self[name]

    def __setattr__(self, name, val):
        self[name] = val

    def config_opt(self):
        opt = self.parse_cmdline()
        self.server = opt.server
        self.password = opt.password
        self.server_port = opt.server_port
        self.local_port = opt.local_port
        self.method = opt.method
        self.timeout = opt.timeout
        self.debug = opt.debug

    def get_file_opt(self):
        p = ArgumentParser(add_help=False)
        p.add_argument("-c", "--config", default=self.default_path,
          help="config.json path",  metavar="FILE")
        opt, _ = p.parse_known_args(self.args)
        if os.path.exists(opt.config):
            with open(opt.config) as f:
                return json_loads(f.read())
        else:
            logger.warning("the json file path `%s` is not exists" % opt.config)
            return {}


    def config_file_opt(self, path2json):
        if os.path.exists(path2json):
            with codecs.open(opt.config, 'r', encoding='ascii') as f:
                json_con = json_loads(f.read())
            self.server = self.server or json_con.get('server', None)
            self.password = self.password or json_con.get('password', None)
            self.server_port = self.server_port or json_con.get('server_port', None)
            self.local_port = self.local_port or json_con.get('local_port', None)
            self.method = self.method or json_con.get('method', 'table')
            self.timeout = self.timeout or json_con.get('timeout', None)
            self.debug = self.debug or json_con.get('debug', False)
        else:
            logger.warning("the json file path `%s` is not exists" % path2json)

    def parse_cmdline(self):
        from fukei import __version__
        parser = ArgumentParser(usage="usage: PROG [options]")
        _ = parser.add_argument
        _("-s", "--server", default='127.0.0.1',
          help="Remote server, IP address or domain (default %(default)r)", type=str)
        _("-k", "--password", default='123', help=
          "Password, should be same in client and server sides (default %(default)r)", type=str)
        _("-c", "--config", default=self.default_path,
          help="config.json path (default %(default)r)", metavar="FILE")
        _("-p", "--server-port", default=8388, help="Remote server port (default %(default)r)", type=int)
        _("-l", "--local-port", default=1080,
          help="Local client port (default %(default)r)", type=int)
        _("-m", "--method", default='table',
          help="Encryption method (default %(default)r)", type=str)
        _("-t", "--timeout", default=10,
          help="connection timeout (default %(default)r)", type=int)
        _("-d", "--debug", action='store_true', default=False,
          help="open debug mode (default %(default)r)",)
        _("-v", "--version", help="Show Fukei version %s" % __version__)
        c = self.get_file_opt()
        parser.set_defaults(**c)

        opt, _ = parser.parse_known_args(self.args)
        return opt

if __name__ == '__main__':
    import doctest
    doctest.testmod()
