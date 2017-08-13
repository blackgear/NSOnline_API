#!/usr/bin/env python
# -*- coding: utf-8 -*-

from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import requests
import base64
import hashlib
import hmac
import random
import re
import string

Session = requests.Session()
Retrier = Retry(total=3, read=3, connect=3, backoff_factor=0.3, status_forcelist=(500, 502, 504))
adapter = HTTPAdapter(max_retries=Retrier)
Session.mount('http://', adapter)
Session.mount('https://', adapter)

class NintendoOAuthService(object):
    def __init__(self, token):
        self.headers = {
            'Accept-Encoding': 'gzip',
            'User-Agent': 'OnlineLounge/1.0.4 NASDKAPI Android',
        }
        self.cookies = {
            'NASID': token
        }
        self.clientid = '71b963c1b7b6d119'
        self.verifier = self.rand()

    def rand(self):
        return ''.join(random.choice(string.ascii_letters) for _ in range(50))

    def hash(self, text):
        text = hashlib.sha256(text.encode()).digest()
        text = base64.urlsafe_b64encode(text).decode()
        return text.replace('=', '')

    def authorize(self):
        url = 'https://accounts.nintendo.com/connect/1.0.0/authorize'
        payload = {
            'client_id' : self.clientid,
            'redirect_uri' : 'npf{}://auth'.format(self.clientid),
            'response_type' : 'session_token_code',
            'scope' : 'openid user user.birthday user.mii user.screenName',
            'session_token_code_challenge' : self.hash(self.verifier),
            'session_token_code_challenge_method' : 'S256',
            'state' : self.rand(),
            'theme' : 'login_form'
        }
        content = Session.get(url, params=payload, headers=self.headers, cookies=self.cookies).text
        token_code = re.findall(r'(eyJhbGciOiJIUzI1NiJ9\.[a-zA-Z0-9_-]*\.[a-zA-Z0-9_-]*)', content)[0]

        url = 'https://accounts.nintendo.com/connect/1.0.0/api/session_token'
        payload = {
            'client_id': self.clientid,
            'session_token_code': token_code,
            'session_token_code_verifier': self.verifier
        }
        content = Session.post(url, data=payload, headers=self.headers).json()

        url = 'https://accounts.nintendo.com/connect/1.0.0/api/token'
        payload = {
            'client_id': self.clientid,
            'grant_type': 'urn:ietf:params:oauth:grant-type:jwt-bearer-session-token',
            'session_token': content['session_token']
        }
        content = Session.post(url, json=payload, headers=self.headers).json()
        return content

class SwitchAccountService(object):
    def __init__(self, token):
        self.headers = {
            'Accept': 'application/json',
            'Accept-Encoding': 'gzip',
            'Authorization': 'Bearer {}'.format(token['access_token']),
            'User-Agent': 'com.nintendo.znca/1.0.4 (Android/6.0.1)'
        }
        self.id_token = token['id_token']

    def authorize(self):
        url = 'https://api-lp1.znc.srv.nintendo.net/v1/Account/GetToken'
        payload = {
            'parameter': {
                'naIdToken': self.id_token,
                'naCountry': 'null',
                'naBirthday': 'null',
                'language': 'null'
            }
        }
        content = Session.post(url, json=payload, headers=self.headers).json()
        self.headers['Authorization'] = 'Bearer {}'.format(content['result']['webApiServerCredential']['accessToken'])

        url = 'https://api-lp1.znc.srv.nintendo.net/v1/Game/ListWebServices'
        payload = {}
        content = Session.post(url, json=payload, headers=self.headers).json()
        service = content['result'][0]['id']

        url = 'https://api-lp1.znc.srv.nintendo.net/v1/Game/GetWebServiceToken'
        payload = {
            'parameter': {
                'id': service
            }
        }
        content = Session.post(url, json=payload, headers=self.headers).json()
        return content['result']

class SplatoonLoginService(object):
    def __init__(self, token):
        self.headers = {
            'Accept-Encoding': 'gzip',
            'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0.1; Nexus 5 Build/M4B30Z; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/59.0.3071.125 Mobile Safari/537.36',
            'x-gamewebtoken': token['accessToken']
        }

    def authorize(self):
        url = 'https://app.splatoon2.nintendo.net'
        request = Session.get(url, headers=self.headers)
        return request.cookies['iksm_session']

class Splatoon(object):
    def __init__(self, token):
        self.headers = {
            'Accept': 'application/json',
            'Accept-Encoding': 'gzip',
            'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0.1; Nexus 5 Build/M4B30Z; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/59.0.3071.125 Mobile Safari/537.36'
        }
        self.cookies = {
            'iksm_session': token
        }

    def get_merchandises(self):
        url = 'https://app.splatoon2.nintendo.net/api/onlineshop/merchandises'
        content = Session.get(url, headers=self.headers, cookies=self.cookies).json()
        return content['merchandises']

def main():
    token = 'Login to https://accounts.nintendo.com, then copy NASID value from cookies and paste here'
    token = NintendoOAuthService(token).authorize()
    token = SwitchAccountService(token).authorize()
    token = SplatoonLoginService(token).authorize()

    splatoon = Splatoon(token)
    print(splatoon.get_merchandises())

if __name__ == '__main__':
    main()
