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
        self.url = 'wss://stream.binance.com:443/stream'
        self.subscriptions = ['btcusdt','ethusdt']

    def get_orderbook(self):
        self.ws = websocket.WebSocketApp(f'{self.url}',
                                         on_open=self.on_open,
                                         on_message=self.on_message,
                                         on_close=self.on_close,
                                         on_error=self.on_error)
        self.ws.run_forever()
    def on_open(self,ws):
        # When initialize Websocket connection
        i = 1
        for symbol in self.subscriptions:

            subscribe_message = {
                "method": "SUBSCRIBE",
                "params":
                    [

                        f"{symbol.lower()}@depth5"
                    ],
                "id": i
            }
            i += 1
            ws.send(json.dumps(subscribe_message))


    def on_close(self,ws,close_status_code,close_msg):
        print(close_msg)
        self.ws = None
    def on_message(self,ws,message):
        data = json.loads(message)
        print(data)
    def on_error(self,ws,error):
        print(error)

test = BinanceApi(api_key='asdasd',secret_key='asd')
test.get_orderbook()