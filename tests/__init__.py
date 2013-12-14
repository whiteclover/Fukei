import unittest

from test_crypto import TestCrypto


if __name__ == '__main__':
	from fukei.utils import log_config
	log_config('test', True)
	unittest.main(verbosity=2)