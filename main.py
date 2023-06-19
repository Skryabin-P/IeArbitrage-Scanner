import time

import requests
import websocket
import json
import threading

quoteasset = ['BUSD','BTC','ETH','USDT','TUSD','DAI','USDC','BNB']
#'BUSD','BTC','ETH','USDT','TUSD','DAI','USDC','BNB'
class ExchangeApi:
    """
    Base exchange API class
    """
    def __init__(self,api_key,secret_key=None):
        self.api_key = api_key
        self.secret_key = secret_key
        self.ws = None
        self.orderbook = {}
        self.ping_interval = 0
        self.ping_timeout = None
        self.lock = threading.Lock()
    def public_request(self,method,url,params=None):
        response = requests.request(method=method,url=url,params=params)
        return response.json()
    def private_request(self,url,data=None,method='POST'):
        headers = {
            'X-MBX-APIKEY':self.api_key
        }
        response = requests.request(method,url,headers=headers,data=data)
        return response.json()

    def connect_wss(self,wss_url):
        print('im here')
        self.ws = websocket.WebSocketApp(wss_url,
                                         on_open=self.on_open,
                                         on_message=self.on_message,
                                         on_close=self.on_close,
                                         on_error=self.on_error)
        # self.ws.run_forever()
        thread = threading.Thread(target=self.ws.run_forever, kwargs={'ping_interval': self.ping_interval,'ping_timeout': self.ping_timeout}, daemon=True)
        thread.start()

    def get_orderbook(self):
        with self.lock:
            return self.orderbook
    def get_market_symbols(self):
        pass
    def on_message(self,ws,message):
        raise NotImplementedError()
    def on_open(self,ws):
        raise NotImplementedError()
    def on_close(self,ws,close_status_code,close_msg):
        print(close_msg)
        self.ws = None
    def on_error(self,ws,error):
        # print(f"это я{error} ")
        print(error)

class BinanceApi(ExchangeApi):
    """
    Binance class for retrieving private market data
    Inherited from base ExchangeAPI class
    """
    def __init__(self,api_key,secret_key):
        super().__init__(api_key,secret_key)
        self.url = 'wss://stream.binance.com:443/stream'
        # self.subscriptions = ['ethbtc','ltcbtc']
        self.subscriptions = {}
        self.get_market_symbols()
        self.connect_wss(self.url)

    def on_open(self,ws):
        # When initialize Websocket connection
        params = []
        print(len(self.subscriptions))
        for symbol in self.subscriptions:
            params.append(f"{symbol.lower()}@depth5@100ms")
        subscribe_message = {
            "method": "SUBSCRIBE",
            "params": params,
            "id": 1
        }
        print(subscribe_message)
        ws.send(json.dumps(subscribe_message))
    def on_message(self,ws,message):
        print(message)
        data = json.loads(message)
        if 'data' in data:
            with self.lock:
                self.orderbook[data['stream'].split('@')[0]] = {"bids":data['data']['bids'],"asks":data['data']['asks']}

    def get_market_symbols(self):
        data = self.public_request(method='GET',url='https://api.binance.com/api/v3/exchangeInfo',
                            params={'permissions': 'SPOT'})
        valid_symbols = [x for x in data['symbols'] if x['status'] == 'TRADING' and x['quoteAsset'] in quoteasset]
        # print(len(valid_symbols))
        # symbols_info = {}
        for symbol in valid_symbols:
            self.subscriptions[symbol['symbol']] = {'baseAsset':symbol['baseAsset'],'quoteAsset':symbol['quoteAsset']}
            if len(self.subscriptions) == 300:
                break




class KucoinApi(ExchangeApi):
    def __init__(self,api_key,secret_key):
        super().__init__(api_key,secret_key)
        self.url = ''
        self.subscriptions = ['BTC-USDT','ETH-USDT']
        self.orderbook = {}
        self.token = ''
        self.get_public_token()
        self.connectId = 123
        self.connect_wss(f'{self.url}?token={self.token}&[connectId={self.connectId}]')
    def get_public_token(self):
        """
        Gets public token and wss url to access Websocket public,
        also it gets PingInterval (ping messages)
        :return: None
        """

        url = 'https://api.kucoin.com/api/v1/bullet-public'
        resp = self.public_request(method="POST",url=url)
        self.token = resp['data']['token']
        self.url = resp['data']['instanceServers'][0]['endpoint']
        self.ping_interval = int(resp['data']['instanceServers'][0]['pingInterval'])/1000
        self.ping_timeout = int(resp['data']['instanceServers'][0]['pingTimeout'])/1000
    def on_open(self,ws):
        topic = f"/spotMarket/level2Depth5:"
        for symbol in self.subscriptions:
            topic+=str(symbol)+','
        topic = topic[:len(topic)-1]
        subscribe_message = {
            "id": 1545910660739,                          #The id should be an unique value
            "type": "subscribe",
            "topic": topic,  #Topic needs to be subscribed. Some topics support to divisional subscribe the informations of multiple trading pairs through ",".
            "privateChannel": False,                      #Adopted the private channel or not. Set as false by default.
            "response": True                            #Whether the server needs to return the receipt information of this subscription or not. Set as false by default.
}
        ws.send(json.dumps(subscribe_message))
    def on_message(self,ws,message):
        # print(message)
        data = json.loads(message)
        if data['type'] =='message':
            if '/spotMarket/level2Depth5' in data['topic']:
                with self.lock:
                    self.orderbook[data['topic'].split(':')[1]] = {"bids": data['data']['bids'], "asks": data['data']['asks']}


    def get_market_symbols(self):
        data = self.public_request(method='GET', url='https://api.kucoin.com/api/v2/symbols')
        all_symbols = data['data']
        # print(len(valid_symbols))
        # symbols_info = {}
        for symbol in all_symbols:
            self.subscriptions[symbol['symbol']] = {'baseAsset': symbol['baseCurrency'],
                                                    'quoteAsset': symbol['quoteCurrency']}
            if len(self.subscriptions) == 300:
                break
        print(self.subscriptions)

if __name__ == "__main__":
    # binance_test = BinanceApi(api_key='asdasd',secret_key='asd')
    # while True:
    #     binance = binance_test.get_orderbook()
    #     time.sleep(0.5)
    #     print(binance)
    #
    kucoin_test = KucoinApi('asd','asd')
    kucoin_test.get_market_symbols()
    # while True:
    #     print('Binance')
    #     print(binance_test.get_orderbook())
    #     print('----------------------------')
    #     print('Kucoin')
    #     print(kucoin_test.get_orderbook())
    #     print('----------------------------')
    #     time.sleep(0.5)