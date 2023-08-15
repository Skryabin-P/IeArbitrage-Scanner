import json

from Client.BaseExchange import ExchangeApi,quoteasset

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
            normalized_name = self.normalize_pair(symbol['baseAsset'],symbol['quoteAsset'])
            self.subscriptions[normalized_name] = {'symbol':symbol['symbol'],'baseAsset':symbol['baseAsset'],'quoteAsset':symbol['quoteAsset']}
            if len(self.subscriptions) == 100:
                break



