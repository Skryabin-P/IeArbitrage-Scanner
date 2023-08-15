import threading
import time
from Client.Binance import BinanceApi
from Client.Kucoin import KucoinApi
import os
"""
There will be Arbitrage scanner part

"""
import itertools


class Scanner:
    def __init__(self, *exchanges):
        self.exchanges = exchanges

    def get_symbols(self):
        """
        Gets symbols which intersects between at least 2 exchanges
        :return: dict

        Probably will be deprecated
        """
        symbols = []
        for exchange1, exchange2 in itertools.combinations(self.exchanges, 2):
            symbols_set = set(exchange1.subscriptions.keys()) & set(exchange2.subscriptions.keys())
            symbols.append(symbols_set)
        return symbols

    def scan(self):
        for exchange1, exchange2 in itertools.combinations(self.exchanges, 2):
            # print('Next try')
            # ex1_status = exchange1.get_status()
            # print(f"status with Lock {ex1_status}")
            # print(f"status without lock {exchange1.status}")
            # ex2_status = exchange2.get_status()
            ex1_status = exchange1.status
            ex2_status = exchange2.status
            print(exchange2.name)
            print(ex2_status)
            print(len(exchange2.orderbook))
            # print('Ex1:')
            # print(len(exchange1.get_orderbook()))
            # print('--------------------------------')
            # print('Ex2:')
            # print(len(exchange2.get_orderbook()))
            # print('---------------------------------')
            if ex1_status and ex2_status:
                symbols_set = set(exchange1.subscriptions.keys()).intersection(set(exchange2.subscriptions.keys()))
                for symbol in symbols_set:
                    ex1_prices = exchange1.orderbook[symbol]
                    ex2_prices = exchange2.orderbook[symbol]
                    profits = self.calculate_symbol_profit(ex1_prices, ex2_prices)
                    print(f"Profit on {symbol} from {exchange1.name} to {exchange2.name} is {profits[0]}")
                    print(f"Profit on {symbol} from {exchange2.name} to {exchange1.name} is {profits[1]}")

    def calculate_symbol_profit(self, ex1_prices, ex2_prices):
        best_bid_price1 = float(ex1_prices['bids'][0][0])
        best_ask_price1 = float(ex1_prices['asks'][0][0])
        # print(best_ask_price1)
        best_bid_price2 = float(ex2_prices['bids'][0][0])
        best_ask_price2 = float(ex2_prices['asks'][0][0])
        ex1_to_ex2_profit = (best_bid_price2 - best_ask_price1) / best_ask_price1 * 100
        ex2_to_ex1_profit = (best_bid_price1 - best_ask_price2) / best_ask_price2 * 100
        return ex1_to_ex2_profit, ex2_to_ex1_profit
    # def run_scanner(self):
    #     scanner_thread = threading.Thread(target=self.scan)
    #     scanner_thread.start()
    #     scanner_thread.join()


if __name__ == "__main__":
    binance = BinanceApi('asdad', 'asd')
    kucoin = KucoinApi('asdasd', 'asdad')

    # binance2 = BinanceApi('asdad2','asd2')
    # binance = TestExchange(name='Binance')
    # kucoin = TestExchange(name='Kucoin')
    #
    # binance.subscriptions = {'eth_btc': {'symbol': 'ETHBTC', 'baseAsset': 'ETH', 'quoteAsset': 'BTC'},
    #                        'ltc_btc': {'symbol': 'LTCBTC', 'baseAsset': 'LTC', 'quoteAsset': 'BTC'}}
    # binance.orderbook = {'ltc_btc': {'bids': [['0.0029500', '107.66200000'], ['0.00289600', '48.56300000'],
    #                                           ['0.00289500', '297.47600000'], ['0.00289400', '523.68300000'],
    #                                           ['0.00289300', '28.09500000']], 'asks': [['0.00289800', '36.80300000'],
    #                             ['0.00289900', '104.95500000'], ['0.00290000', '568.71800000'], ['0.00290100', '15.57800000'], ['0.00290200', '38.29700000']]}, 'eth_btc': {'bids': [['0.06149000', '48.71730000'], ['0.06148000', '13.86510000'], ['0.06147000', '16.19940000'], ['0.06146000', '79.25280000'], ['0.06145000', '14.52650000']], 'asks': [['0.06150000', '26.64400000'], ['0.06151000', '13.77430000'], ['0.06152000', '22.17120000'], ['0.06153000', '26.65360000'], ['0.06154000', '11.58990000']]}}
    #
    # kucoin.subscriptions = {'ltc_btc': {'symbol': 'LTCBTC', 'baseAsset': 'LTC', 'quoteAsset': 'BTC'},
    #                         'eth_btc': {'symbol': 'ETHBTC', 'baseAsset': 'ETH', 'quoteAsset': 'BTC'}}
    #
    # kucoin.orderbook = {'ltc_btc': {'bids': [['0.00289700', '126.00700000'], ['0.00289600', '69.39500000'], ['0.00289500', '290.34900000'], ['0.00289400', '523.68300000'], ['0.00289300', '28.09500000']], 'asks': [['0.00289800', '1.55400000'], ['0.00289900', '40.66600000'], ['0.00290000', '568.71800000'], ['0.00290100', '15.57800000'], ['0.00290200', '38.29700000']]}, 'eth_btc': {'bids': [['0.06149000', '48.55470000'], ['0.06148000', '13.72570000'], ['0.06147000', '16.08990000'], ['0.06146000', '64.71740000'], ['0.06145000', '15.33120000']], 'asks': [['0.06150000', '20.39310000'], ['0.06151000', '21.66670000'], ['0.06152000', '21.73320000'], ['0.06153000', '43.48520000'], ['0.06154000', '12.49130000']]}}
    scanner = Scanner(binance, kucoin)
    while True:
        scanner.scan()
        # os.system('cls' if os.name == 'nt' else 'clear')
        # time.sleep(1)
    # # print(scanner.get_symbols())
