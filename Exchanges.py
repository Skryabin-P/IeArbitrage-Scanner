import time

import requests
import websocket
import json
import threading
from func import normalize_pair
quoteasset = ['BUSD','BTC','ETH','USDT','TUSD','DAI','USDC','BNB']
#'BUSD','BTC','ETH','USDT','TUSD','DAI','USDC','BNB'

# btc_usdt - unified representation of crypto pairs

class ExchangeApi:
    """
    Base exchange API class
    """
    def __init__(self,api_key,secret_key=None):
        self.api_key = api_key
        self.secret_key = secret_key
        self.status = False
        self.ws = None
        self.subscriptions = {}
        self.name = ''
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
        print(f"Error from {self.name} is  {error}")
    def find_symbol(self,symbol:str):
        for key in self.subscriptions:
            if str(self.subscriptions[key]['symbol']).lower()==symbol.lower():
                return key
class BinanceApi(ExchangeApi):
    """
    Binance class for retrieving private market data
    Inherited from base ExchangeAPI class
    """
    def __init__(self,api_key,secret_key):
        super().__init__(api_key,secret_key)
        self.name = "Binance"
        self.url = 'wss://stream.binance.com:443/stream'
        # self.subscriptions = ['ethbtc','ltcbtc']
        self.subscriptions = {}
        self.get_market_symbols()
        self.connect_wss(self.url)

    def on_open(self,ws):
        # When initialize Websocket connection
        params = []
        print(len(self.subscriptions))
        for symbol,value in self.subscriptions.items():
            params.append(f"{value['symbol'].lower()}@depth5@100ms")
        subscribe_message = {
            "method": "SUBSCRIBE",
            "params": params,
            "id": 1
        }
        print(subscribe_message)
        ws.send(json.dumps(subscribe_message))
    def on_message(self,ws,message):
        # print(message)
        data = json.loads(message)
        if 'data' in data:
            with self.lock:
                unified_symbol = self.find_symbol(data['stream'].split('@')[0])
                self.orderbook[unified_symbol] = {"bids":data['data']['bids'],"asks":data['data']['asks']}
                if len(self.orderbook) == len(self.subscriptions):
                    self.status=True

    def get_market_symbols(self):
        data = self.public_request(method='GET',url='https://api.binance.com/api/v3/exchangeInfo',
                            params={'permissions': 'SPOT'})
        valid_symbols = [x for x in data['symbols'] if x['status'] == 'TRADING' and x['quoteAsset'] in quoteasset]
        # print(len(valid_symbols))
        # symbols_info = {}
        for symbol in valid_symbols:
            normalized_name = normalize_pair(symbol['baseAsset'],symbol['quoteAsset'])
            self.subscriptions[normalized_name] = {'symbol':symbol['symbol'],'baseAsset':symbol['baseAsset'],'quoteAsset':symbol['quoteAsset']}
            if len(self.subscriptions) == 100:
                break




class KucoinApi(ExchangeApi):
    """
        Kucoin class for retrieving private market data
        Inherited from base ExchangeAPI class
        """
    def __init__(self,api_key,secret_key):
        super().__init__(api_key,secret_key)
        self.name = "Kucoin"
        self.url = ''
        self.subscriptions = {}
        # self.subscriptions = ['ETH-USDT','ETH-BTC']
        self.orderbook = {}
        self.token = ''
        self.get_public_token()
        self.connectId = 123
        self.get_market_symbols()
        self.connect_wss(f'{self.url}?token={self.token}&[connectId={self.connectId}]')
    def get_public_token(self):
        """
        Gets public token and wss url to access Websocket public,
        also it gets PingInterval (ping messages)
        :return: None
        """

        url = 'https://api.kucoin.com/api/v1/bullet-public'
        resp = self.public_request(method="POST",url=url)
        print(resp)
        self.token = resp['data']['token']
        self.url = resp['data']['instanceServers'][0]['endpoint']
        self.ping_interval = int(resp['data']['instanceServers'][0]['pingInterval'])/1000

        self.ping_timeout = int(resp['data']['instanceServers'][0]['pingTimeout'])/1000

    def on_open(self,ws):
        topic = f"/spotMarket/level2Depth5:"
        for symbol,value in self.subscriptions.items():
            topic+=str(value['symbol'])+','
        topic = topic[:len(topic)-1]
        subscribe_message = {
            "id": 1545910660735,                          #The id should be an unique value
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
                    unified_symbol = self.find_symbol(data['topic'].split(':')[1])

                    self.orderbook[unified_symbol] = {"bids": data['data']['bids'], "asks": data['data']['asks']}
                    if len(self.orderbook) == len(self.subscriptions):
                        self.status = True

    def get_market_symbols(self):
        data = self.public_request(method='GET', url='https://api.kucoin.com/api/v2/symbols')
        all_symbols = data['data']
        # print(len(valid_symbols))
        # symbols_info = {}
        for symbol in all_symbols:
            if symbol['quoteCurrency'] in quoteasset and symbol['enableTrading']==True:
                normalized_name = normalize_pair(symbol['baseCurrency'],symbol['quoteCurrency'])
                self.subscriptions[normalized_name] = {'symbol':symbol['symbol'],'baseAsset': symbol['baseCurrency'],
                                                    'quoteAsset': symbol['quoteCurrency']}
            if len(self.subscriptions) == 100:
                break
        # print(self.subscriptions)

if __name__ == "__main__":
    # binance_test = BinanceApi(api_key='asdasd',secret_key='asd')
    # while True:
    #     binance = binance_test.get_orderbook()
    #     time.sleep(0.5)
    #     print(binance)
    #
    kucoin_test = KucoinApi('asd','asd')
    # kucoin_test.get_market_symbols()
    # print(kucoin_test.subscriptions)
    # print(kucoin_test.find_symbol('LOKI-BTC'))
    while True:
        # print('Binance')
        # print(binance_test.subscriptions)
        # print(binance_test.get_orderbook())
        # print('----------------------------')
        print('Kucoin')
        print(kucoin_test.get_orderbook())
        # print('----------------------------')

        time.sleep(2)
