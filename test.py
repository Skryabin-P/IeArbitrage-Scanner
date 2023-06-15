import ccxt

BinanceEx = ccxt.binance()

orderbook = BinanceEx.watch_order_book('btcusdt')
print(123)
print(orderbook)