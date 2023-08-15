import requests
import websocket
import threading

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
    def get_status(self):
        with self.lock:
            return self.status
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
    def normalize_pair(self,base_asset:str,quote_asset:str):
        return base_asset.lower()+"_"+quote_asset.lower()