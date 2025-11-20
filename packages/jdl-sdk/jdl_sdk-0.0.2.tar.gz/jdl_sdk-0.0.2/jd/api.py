#!/usr/bin/python3
# @Time    : 2025-10-18
# @Author  : Kevin Kong (kfx2007@163.com)

from jd.comm import Comm
from jd.order import Order

class JDL(object):
    """JD SDK"""

    def __init__(self, app_key, app_secret, customer_code, access_token=None, sandbox=False):
        """
        初始化方法
        """
        self.app_key = app_key
        self.app_secret = app_secret
        self.sandbox = sandbox
        self.customer_code = customer_code
        self.access_token = access_token
        
    comm = Comm()
    order = Order()