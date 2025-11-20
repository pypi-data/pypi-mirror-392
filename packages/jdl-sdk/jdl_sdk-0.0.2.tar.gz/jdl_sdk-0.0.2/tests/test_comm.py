#!/usr/bin/python3
# @Time    : 2025-10-18
# @Author  : Kevin Kong (kfx2007@163.com)

import unittest
from jd.api import JDL

class TestComm(unittest.TestCase):
    
    def setUp(self):
        self.jd = JDL(
            "588bd6c100af4c36b9521bf0068cebf9",
            "3a39e9e08a4e42d1aaa1fec5f9f9cf98",
            sandbox=True,
        )
        
    def test_get_oauth_url(self):
        url = "https://192.168.195.6:8069"
        url = self.jd.comm.get_authorize_url(redirect_uri=url)
        print(url)
        
    def test_get_access_token(self):
        code = "93e355ccd5134d179c2b88b99130dde0"
        token_info = self.jd.comm.get_access_token(code)
        print(token_info)
        # {"accessExpire":"2026-10-20 19:53:51",
        # "accessToken":"526746aa7f0a4fbbaef7508b9c2a61a5","
        # clientId":"588bd6c100af4c36b9521bf0068cebf9","
        # code":"93e355ccd5134d179c2b88b99130dde0",
        # "refreshExpire":"2026-11-20 19:53:51",
        # "refreshToken":"188afd53bb6b46cfa1ca0bccf27e9e51",
        # "sellerId":"kfx2007_m"}
    
    def test_refresh_access_token(self):
        refresh_token = "188afd53bb6b46cfa1ca0bccf27e9e51"
        token_info = self.jd.comm.refresh_access_token(refresh_token)
        print(token_info)
    
if __name__ == "__main__":
    unittest.main()
    