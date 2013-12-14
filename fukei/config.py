

try:
    import json
except:
    #handle the low python version < 2.6
    import simplejson as json
    
import logging
import os.path

logger = logging.getLogger('config')


class Config(dict):

    """Config  reads json file config firstly, then
      parses command line and override the file config settings

    >>> from utils import log_config
    >>> log_config('test_config', True)
    >>> config = Config()
    >>> config.args
    ()
    >>> config['args']
    ()
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

    def __init__(self, *args):

        super(Config, self).__init__()
        self.args = args
        self.config_opt()

    def __getattr__(self, name):
        return self[name]

    def __setattr__(self, name, val):
        self[name] = val

    def config_opt(self):
        opt = self.parse_cmdline()
        self.server = opt.server
        self.password = opt.password
        self.port = opt.port
        self.local_port = opt.local_port
        self.method = opt.method
        self.timeout = opt.timeout
        if opt.config:
            self.config_file_opt(opt.config)

    def config_file_opt(self, path2json):
        if os.path.exists(path2json):
            with open(path2json) as f:
                json_con = json.loads(f.read())
            self.server = self.server or json_con.get('server', None)
            self.password = self.password or json_con.get('password', None)
            self.port = self.port or json_con.get('port', None)
            self.local_port = self.local_port or json_con.get('local_port', None)
            self.method = self.method or json_con.get('method', 'table')
            self.timeout = self.timeout or json_con.get('timeout', None)
        else:
            logger.warning("the json file path `%s` is not exists" % path2json)

    def parse_cmdline(self):
        from argparse import ArgumentParser
        from fukei import __version__
        parser = ArgumentParser(usage="usage: PROG [options]")
        _ = parser.add_argument
        _("-s", "--server", default='127.0.0.1',
          help="Remote server, IP address or domain", type=str)
        _("-k", "--password", default='123', help=
          "Password, should be same in client and server sides", type=str)
        _("-c", "--config", default='0.0.0.0',
          help="config.json path", type=str)
        _("-p", "--port", default=89, help="Remote server port", type=int)
        _("-l", "--local_port", default=90,
          help="Local client port", type=int)
        _("-m", "--method", default='table',
          help="Encryption method", type=str)
        _("-t", "--timeout", default=3,
          help="connection timeout", type=int)
        _("-v", "--version", help="Show Fukei version %s" % __version__)

        return parser.parse_args()


if __name__ == '__main__':
    import doctest
    doctest.testmod()
