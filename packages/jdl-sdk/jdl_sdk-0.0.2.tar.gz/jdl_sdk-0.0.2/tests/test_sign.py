#!/usr/bin/python3
# @Time    : 2025-10-20
# @Author  : Kevin Kong (kfx2007@163.com)

import unittest
from jd.comm.comm import Comm

class DummyApp:
    app_key = '1d2d101eXXXXXXXXab0cf3a8148f9254'
    app_secret = 'e146f1dbXXXXXXXXbb762a650b9c3b65'
    sandbox = True

class TestSign(unittest.TestCase):
    def setUp(self):
        self.comm = Comm().__get__(DummyApp(), None)

    def test_sign_md5(self):
        refresh_token = '191e9433XXXXXXXXb2933b244d3ef18d'
        timestamp = '2020-01-01 00:00:00'
        sig = self.comm.sign(self.comm.app_secret, self.comm.app_key, refresh_token, timestamp)
        # 手动计算副本对比
        import hashlib
        content = f"{self.comm.app_secret}app_key{self.comm.app_key}refresh_token{refresh_token}timestamp{timestamp}{self.comm.app_secret}"
        expect = hashlib.md5(content.encode()).hexdigest()
        self.assertEqual(sig, expect)
        self.assertEqual(len(sig), 32)
        self.assertTrue(all(c in '0123456789abcdef' for c in sig))

if __name__ == '__main__':
    unittest.main()
