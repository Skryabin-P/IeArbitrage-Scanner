import json
from Client.BaseExchange import ExchangeApi,quoteasset
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
        print(F"{self.name} - ping interval={self.ping_interval}, ping timeout={self.ping_timeout}")
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
                normalized_name = self.normalize_pair(symbol['baseCurrency'],symbol['quoteCurrency'])
                self.subscriptions[normalized_name] = {'symbol':symbol['symbol'],'baseAsset': symbol['baseCurrency'],
                                                    'quoteAsset': symbol['quoteCurrency']}
            if len(self.subscriptions) == 100:
                break