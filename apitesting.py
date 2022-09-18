from apiKeySecret import credentials

from binance import Client

client = Client(credentials['key'], credentials['secret'], testnet=True)

order = client.order_limit_buy(symbol='ETHUSDT',
                                quantity=2,
                                price=5000)

print(order)