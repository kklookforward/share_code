import hmac
import hashlib
import requests
import sys
import time
import base64
import json
from collections import OrderedDict

class Vaex():
    def __init__(self,base_url='https://openapi.vaex.tech/sapi/v1/', symbol=""):
        self.base_url = base_url
        self.symbol = symbol
        if not self.symbol:
            print("Init error, please add symbol")

    def auth(self, key, secret):
        # self.key = bytes(key,'utf-8')
        self.key = key
        self.secret = bytes(secret, 'utf-8') 

    def public_request(self, method, api_url, **payload):
        """request public url"""
        r_url = self.base_url + api_url
        # print(r_url)
        try:
            r = requests.request(method, r_url, params=payload)
            r.raise_for_status()
        except requests.exceptions.HTTPError as err:
            print(err)
        if r.status_code == 200:
            return r.json()

    def get_signed(self, sig_str):
        """signed params use sha256"""
        # sig_str = base64.b64encode(sig_str)
        # signature = base64.b64encode(hmac.new(self.secret, sig_str, digestmod=hashlib.sha256).hexdigest())
        signature = hmac.new(self.secret, sig_str, digestmod=hashlib.sha256).digest().hex()
        return signature

    def get_dict_str(sefl, input_dict):
        ret = {}
        for it in input_dict:
            ret[str(it)] = str(input_dict[it])
            # ret[str(it)] = input_dict[it]
        return json.dumps(ret).replace(" ", "")

    def signed_request(self, method, api_url, **payload):
        """request a signed url"""
        if not self.key or not self.secret:
            print("Please config api key and secret")
            exit(-1)
        param=''
        if payload:
            sort_pay = sorted(payload.items())
            for k in sort_pay:
                param += '&' + str(k[0]) + '=' + str(k[1])
            param = param.lstrip('&')
        timestamp = str(int(time.time() * 1000))
        full_url = self.base_url + api_url
        request_path = '/sapi/v1/' + api_url
        if method == 'GET':
            if param:
                full_url = full_url + '?' + param
                request_path = request_path + '?' + param
            sig_str = timestamp + method + request_path
        elif method == 'POST':
            sig_str = timestamp + method + request_path + self.get_dict_str(payload)
        # print(f"sig_str: {sig_str}")

        signature = self.get_signed(bytes(sig_str, 'utf-8'))

        headers = {
            'X-CH-SIGN': signature,
            'X-CH-APIKEY': self.key,
            'X-CH-TS': timestamp,
            'Content-Type': 'application/json'
        }

        try:
            # print(method)
            # print(full_url)
            # print(headers)
            # print(self.get_dict_str(payload))
            if method == "GET":
                r = requests.request(method, full_url, headers=headers)
            else:
                r = requests.request(method, full_url, headers=headers, data=self.get_dict_str(payload))
                # r = requests.request(method, full_url, headers=headers, data=payload)
            r.raise_for_status()
        except requests.exceptions.HTTPError as err:
            print(err)
            print(r.text)
        if r.status_code == 200:
            return r.json()

    def get_depth(self, limit=100):
        """get market depth"""
        return self.public_request('GET', 'depth', limit=limit, symbol=self.symbol)

    def get_account_info(self):
        """get account info(done)"""
        return self.signed_request('GET', 'account')

    def create_order(self, **payload):
        """create order(done)"""
        return self.signed_request('POST','order', **payload)

    def trade(self, price, amount, direction):
        """trade someting, buy(1) or sell(0)"""
        try:
            if direction == 1:
                return self.buy(price, amount)
            else:
                return self.sell(price, amount)
        except:
            print("Trade error")
            return "Trade error"

    def buy(self, price, amount):
        """buy someting(done)"""
        return self.create_order(symbol=self.symbol, side='BUY', type='LIMIT', price=price, volume=amount)

    def sell(self, price, amount):
        """sell someting(done)"""
        return self.create_order(symbol=self.symbol, side='SELL', type='LIMIT', price=price, volume=amount)

    def get_order(self,order_id):
        """get specfic order(done)"""
        return self.signed_request('GET', 'order', orderId=order_id, symbol=self.symbol)

    def get_open_order(self, limit=None):
        """get specfic order(done)"""
        if limit:
            return self.signed_request('GET', 'openOrders', symbol=self.symbol, limit=limit)
        else:
            return self.signed_request('GET', 'openOrders', symbol=self.symbol)

    def create_order_test(self):
        """get specfic order(done)"""
        # {"symbol":"BTCUSDT","price":"9300","volume":"1","side":"BUY","type":"LIMIT"} Copied!
        return self.signed_request('GET', 'order/test', symbol=self.symbol, volume=1, side="BUY", type="LIMIT", price=9300)

    def cancel_order(self,order_id):
        """cancel specfic order(done)"""
        return self.signed_request('POST', 'cancel', orderId=order_id, symbol=self.symbol)


if __name__ == "__main__":
    print("Start...")
    # vaex = Vaex(symbol="btcusdt")
    vaex = Vaex(symbol="HSPCUSDT")
    print(vaex.get_depth())