class TestExchange:
    def __init__(self,name):
        self.subscriptions = {}
        self.orderbook = {}
        self.name = name
        self.status=False
        print(f"Initiate {self.name}")
        self.scan()

    def scan(self):
        print(f'Scanning {self.name}')

        self.status=True
