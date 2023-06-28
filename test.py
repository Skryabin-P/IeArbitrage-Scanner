class TestExchange:
    def __init__(self,name):
        self.subscriptions = {}
        self.orderbook = {}
        self.name = name
        self.status=True
        print(f"Initiate {self.name}")
