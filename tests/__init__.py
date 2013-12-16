#!/usr/bin/env python

import unittest
from test_crypto import TestCrypto
from fukei.utils import log_config

if __name__ == '__main__':
    log_config('test', True)
    unittest.main(verbosity=2)
