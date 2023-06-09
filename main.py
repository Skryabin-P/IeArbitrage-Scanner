import requests
import websocket
import json

class ExchangeApi:
    def __init__(self,api_key,secret_key=None):
        self.api_key = api_key
        self.secret_key = secret_key
        self.ws = None

    def public_request(self,url,params=None):
        response = requests.get(url,params=params)
        return response.json()
    def private_request(self,url,data=None,method='POST'):
        headers = {
            'X-MBX-APIKEY':self.api_key
        }
        response = requests.request(method,url,headers=headers,data=data)
        return response.json()
    def get_orderbook(self,symbol):
        raise NotImplementedError()


class BinanceApi(ExchangeApi):
    def __init__(self,api_key,secret_key):
        super().__init__(api_key,secret_key)
        self.url = 'wss://stream.binance.com:443/ws'
        self.subscriptions = []

    def get_orderbook(self,symbol:str):
        stream_name = f'{symbol.lower()}@depth20'
        # self.ws = websocket.

