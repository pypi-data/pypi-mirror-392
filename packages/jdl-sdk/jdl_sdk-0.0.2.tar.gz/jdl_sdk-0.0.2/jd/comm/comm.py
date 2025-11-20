#!/usr/bin/python3
# @Time    : 2025-10-18
# @Author  : Kevin Kong (kfx2007@163.com)

import requests
import json
from datetime import datetime
import hashlib
import base64
import hmac


SANDBOXURL = "https://uat-api.jdl.com"
URL = "https://api.jdl.com"
OAUTHURL = "https://oauth.jdl.com"
SANDBOXAUTHURL = "https://uat-oauth.jdl.com"

class Comm(object):
    """JD 通用类"""

    def __get__(self, instance, owner):
        """
        初始化方法
        """
        self.app_key = instance.app_key
        self.app_secret = instance.app_secret
        self.sandbox = instance.sandbox
        self.customer_code = instance.customer_code
        self.access_token = instance.access_token
        if self.sandbox:
            self.base_url = SANDBOXURL
            self.oauth_url = SANDBOXAUTHURL
        else:
            self.base_url = URL
            self.oauth_url = OAUTHURL
        return self
            
    def get_authorize_url(self, redirect_uri=None):
        """
        获取授权URL
        """
        redirect = redirect_uri if redirect_uri else "urn:ietf:wg:oauth:2.0:oob"
        return f"{self.oauth_url}/oauth/authorize?client_id={self.app_key}&redirect_uri={redirect}&response_type=code"
    
    def get_timestamp(self):
        try:
            from zoneinfo import ZoneInfo  # Python 3.9+
            tz = ZoneInfo('Asia/Shanghai')  # GMT+8
            ts = datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S')
        except Exception:
            try:
                import pytz
                tz = pytz.timezone('Asia/Shanghai')
                ts = datetime.now(tz).strftime('%Y-%m-%d %H:%M:%S')
            except Exception:
                # Fallback: assume server local time already GMT+8
                ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        return ts

    def get_access_token(self, code):
        """
        获取访问令牌
        """
        url = f"{self.oauth_url}/oauth/token"
        params = {
            "client_id": self.app_key,
            "client_secret": self.app_secret,
            "code": code,
        }
        response = requests.get(url, params=params)
        return response.json()
    
    def refresh_access_token(self, refresh_token):
        """
        刷新访问令牌
        """
        ts = self.get_timestamp()
        signature = self.refresh_sign(self.app_secret, self.app_key, refresh_token, ts)
        url = f"{self.oauth_url}/oauth/refresh"
        params = {
            "app_key": self.app_key,
            "refresh_token": refresh_token,
            "timestamp": ts,
            "sign": signature,
        }
        
        response = requests.get(url, params=params)
        return response.json()

    def refresh_sign(self, app_secret: str, app_key: str, refresh_token: str, timestamp: str) -> str:
        """生成京东物流刷新 access_token 的签名。

        拼接规则：
          content = appSecret + 'app_key' + appKey + 'refresh_token' + refreshToken + 'timestamp' + timestamp + appSecret
        然后对 content 做 MD5，输出 32 位小写十六进制。

        Args:
            app_secret (str): 应用的 appSecret
            app_key (str): 应用的 appKey
            refresh_token (str): refreshToken
            timestamp (str): 格式 yyyy-MM-dd HH:mm:ss (GMT+8)

        Returns:
            str: 32位小写十六进制 MD5 签名
        """
        if not all([app_secret, app_key, refresh_token, timestamp]):
            raise ValueError("签名参数缺失: app_secret/app_key/refresh_token/timestamp 必填")
        content = f"{app_secret}app_key{app_key}refresh_token{refresh_token}timestamp{timestamp}{app_secret}"
        return hashlib.md5(content.encode('utf-8')).hexdigest()
    
    def sign(self, algorithm: str, data: bytes, secret: bytes) -> str:
        if algorithm == "md5-salt":
            h = hashlib.md5()
            h.update(data)
            return h.digest().hex()
        elif algorithm == "HMacMD5":
            return base64.b64encode(hmac.new(secret, data, hashlib.md5).digest()).decode("UTF-8")
        elif algorithm == "HMacSHA1":
            return base64.b64encode(hmac.new(secret, data, hashlib.sha1).digest()).decode("UTF-8")
        elif algorithm == "HMacSHA256":
            return base64.b64encode(hmac.new(secret, data, hashlib.sha256).digest()).decode("UTF-8")
        elif algorithm == "HMacSHA512":
            return base64.b64encode(hmac.new(secret, data, hashlib.sha512).digest()).decode("UTF-8")
        raise NotImplementedError("Algorithm " + algorithm + " not supported yet")

    def post(self, endpoint, data, lopdn='ECAP', access_token=None):
        """
        发送POST请求
        """
        url = f"{self.base_url}{endpoint}"
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "lop-http/python3"
        }
        
        timestamp = self.get_timestamp()
        
        access_token = access_token if access_token else self.access_token
        
        content = "".join([
            self.app_secret,
            "access_token", access_token,
            "app_key", self.app_key,
            "method", endpoint,
            "param_json", json.dumps(data),
            "timestamp", timestamp,
            "v", "2.0",
            self.app_secret
        ])
        
        
        sign_ = self.sign('md5-salt',content.encode('utf-8'),self.app_secret.encode('utf-8'))
        
        params = {
            "LOP-DN": lopdn,
            "app_key": self.app_key,
            "access_token": access_token,
            "timestamp": timestamp,
            "v": "2.0",
            "sign": sign_,
            "algorithm": "md5-salt"
        }
        
        print("+++++")
        print(url)
        print(params)
        
        response = requests.post(url, headers=headers, params=params, data=json.dumps(data))
        return response.json()
    
    