#!/usr/bin/env python
# -*- coding: utf-8 -*-

# The MIT License

# Copyright (c) 2017 Daniel

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import requests
import base64
import hashlib
import hmac
import random
import re
import string
import json

Session = requests.Session()
Retrier = Retry(total=3, read=3, connect=3, backoff_factor=0.3, status_forcelist=(500, 502, 504))
adapter = HTTPAdapter(max_retries=Retrier)
Session.mount('http://', adapter)
Session.mount('https://', adapter)

JWToken = re.compile(r'(eyJhbGciOiJIUzI1NiJ9\.[a-zA-Z0-9_-]*\.[a-zA-Z0-9_-]*)')

class NintendoOAuthService(object):
    def __init__(self, username, password):
        self.headers = {
            'Accept-Encoding': 'gzip',
            'User-Agent': 'OnlineLounge/1.0.4 NASDKAPI Android',
        }
        self.clientid = '71b963c1b7b6d119'
        self.username = username
        self.password = password
        self.verifier = self.rand()

    def rand(self):
        return ''.join(random.choice(string.ascii_letters) for _ in range(50))

    def hash(self, text):
        text = hashlib.sha256(text.encode()).digest()
        text = base64.urlsafe_b64encode(text).decode()
        return text.replace('=', '')

    def hmac(self, csrf_token):
        msg = '{}:{}:{}'.format(self.username, self.password, csrf_token)
        return hmac.new(csrf_token[-8:].encode(), msg=msg.encode(), digestmod=hashlib.sha256).hexdigest()

    def unpack(self, data):
        data = data.split('.')[1]
        missing_padding = len(data) % 4
        if missing_padding != 0:
            data += '='* (4 - missing_padding)
        return json.loads(base64.urlsafe_b64decode(data.encode()))

    def authorize(self):
        # Login sometimes error, I don't know why, but retry will solve...
        while True:
            url = 'https://accounts.nintendo.com/connect/1.0.0/authorize'
            payload = {
                'client_id'                           : self.clientid,
                'redirect_uri'                        : 'npf{}://auth'.format(self.clientid),
                'response_type'                       : 'session_token_code',
                'scope'                               : 'openid user user.birthday user.mii user.screenName',
                'session_token_code_challenge'        : self.hash(self.verifier),
                'session_token_code_challenge_method' : 'S256',
                'state'                               : self.rand(),
                'theme'                               : 'login_form'
            }
            request = Session.get(url, params=payload, headers=self.headers)
            post_login = request.history[0].url
            csrf_token = JWToken.findall(request.text)[0]

            url = 'https://accounts.nintendo.com/login'
            payload = {
                'csrf_token'                          : csrf_token,
                'display'                             : '',
                'post_login_redirect_uri'             : post_login,
                'redirect_after'                      : 5,
                'subject_id'                          : self.username,
                'subject_password'                    : self.password,
                '_h'                                  : self.hmac(csrf_token),
            }
            self.headers['Referer'] = request.url
            request = Session.post(url, data=payload, headers=self.headers)
            token_code = JWToken.findall(request.text)[0]
            if self.unpack(token_code)['typ'] == 'session_token_code':
                break

        url = 'https://accounts.nintendo.com/connect/1.0.0/api/session_token'
        payload = {
            'client_id': self.clientid,
            'session_token_code': token_code,
            'session_token_code_verifier': self.verifier
        }
        content = Session.post(url, data=payload, headers=self.headers).json()
        return content['session_token']

def main():
    username = ''
    password = ''
    session_token = NintendoOAuthService(username, password).authorize()
    print(session_token)

if __name__ == '__main__':
    main()
