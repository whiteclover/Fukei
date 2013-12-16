from fukei import crypto
import unittest

class TestCrypto(unittest.TestCase):

    def setUp(self):
        self.data = 'HELLO World'

    def test_method_is_table(self):
        crypto.setup_table('12233')
        e = crypto.new_crypto()
        for i in range(2000):
            d = e.encrypt(self.data)
            self.assertEqual(e.decrypt(d), self.data)

    def test_aes_128_cfb(self):
        crypto.setup_table('12233', 'aes-128-cfb')
        e = crypto.new_crypto()
        for i in range(2000):
            d = e.encrypt(self.data)
            self.assertEqual(e.decrypt(d), self.data)

    def test_des_cfb(self):
        crypto.setup_table('12233', 'des-cfb')
        e = crypto.new_crypto()
        for i in range(2000):
            d = e.encrypt(self.data)
            self.assertEqual(e.decrypt(d), self.data)

    def test_pairs(self):
        from uuid import uuid4
        crypto.setup_table('12233', 'des-cfb')
        e = crypto.new_crypto()
        d = crypto.new_crypto()
        for i in range(100):
            data = uuid4().bytes
            e_data = e.encrypt(str(data))
            self.assertEqual(d.decrypt(e_data ), data)


if __name__ == '__main__':
    unittest.main(verbosity=2)