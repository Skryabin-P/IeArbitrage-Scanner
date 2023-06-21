from Exchanges import BinanceApi,KucoinApi
"""
There will be Arbitrage scanner part

"""

class Scanner:
    def __init__(self,*exchanges):
        self.exchanges = exchanges

    def get_symbols(self):
        """
        Gets symbols which intersects between at least 2 exchanges
        :return:
        """
        symbols_sets = []
        for i in range(len(self.exchanges)):
            for j in range(i+1,len(self.exchanges)):
                # symbols_set = set(ex.subscriptions.keys() for ex in [self.exchanges[i],self.exchanges[j]])
                for
        pass
    def scan(self):
        symbols_sets = [set(ex.subscriptions.keys)]
