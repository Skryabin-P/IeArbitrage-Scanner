from Client.BaseExchange import ExchangeApi


class BybitApi(ExchangeApi):
    def __init__(self,api_key,secret_key):
        super().__init__(api_key, secret_key)
        self.name = 'Bybit'
        self.url = 'wss://stream.bybit.com/v5/public/spot'

