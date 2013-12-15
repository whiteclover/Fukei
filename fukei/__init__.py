__version__ = "0.1"
version = __version__

import tornado.ioloop
from utils import  log_config

log_config('Fukei', True)
# from socks import Socks5Server

# class FukeiSocksServer(object):

# 	def __init__(self, side, config):
# 		self.side = side
# 		self.config = config

# 	def create_server(self, address, port):

# 	    server = Socks5Server(upstream_name)
# 	    "Startting Fukei ...."
# 	    server.bind(port, address=addr, backlog=1024)
# 	    return server


# 	def server_forevet(self):
# 		num_processes = 12
# 		try:
# 			server = self.create_server()
# 			server.start(num_processes)
# 			tornado.ioloop.IOLoop.instance().start()
# 		except KeyboardInterrupt:
# 			tornado.ioloop.IOLoop.instance().stop()
# 		return 0


# import tornado.ioloop
# from utils import  log_config

# from socks5server import Socks5Server


# def create_server(num_processes, addr, port, upstream_name):
#     server = Socks5Server(upstream_name)

#     "Startting Fukei ...."
#     server.bind(port, address=addr, backlog=1024)

#     try:
        
#         server.start(num_processes)
#         tornado.ioloop.IOLoop.instance().start()
#     except KeyboardInterrupt:
#         tornado.ioloop.IOLoop.instance().stop()
#     return 0

# def get_commandline_options():
#     from argparse import ArgumentParser

#     parser = ArgumentParser(
#         usage="usage: PROG [options] testfile_or_dir [testfile_or_dir...]")
#     _ = parser.add_argument
#     _("--port", default=8888,
#         help="Run SOCKS proxy on a specific port", type=int)
#     _("--processes", default=1,
#         help="Run multiple processes", type=int)
#     _("--bind", default='0.0.0.0',
#         help="Bind address", type=str)
#     _("--upstream", default="local",
#         help="Upstream class path", type=str)
#     _("--debug", default=False,
#         help="set debug mode", type=bool)
#     return parser.parse_args()


# if __name__ == '__main__':
    
#     opt =  get_commandline_options()
#     log_config('Fukei', opt.debug)
#     create_server(opt.processes,
#         opt.bind,
#         opt.port, opt.upstream)
#     