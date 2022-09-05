import time
import binanceOrders as bo
import asyncio

from apiKeySecret import credentials

from binance import Client
from binance import AsyncClient, BinanceSocketManager

client = Client(credentials['key'], credentials['secret'])

limitbuy = bo.Buy('APEBUSD',9,2)
print('bought')
time.sleep(5)

limitbuy.cancel()

'''async def async_event_update():
    async_client = await AsyncClient.create(credentials['key'], credentials['secret'])
    bm = BinanceSocketManager(async_client)
    async with bm.user_socket() as stream:
        print("Running")
        while True:
            data = await stream.recv()
            print(data)

asyncio.run(async_event_update())'''
