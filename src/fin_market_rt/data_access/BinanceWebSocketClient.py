import asyncio
import json
from abc import ABC

from src.fin_market_rt.data_access.entites import KLineData
import websockets


class StockDataProvider(ABC):
    def __init__(self, pair: str, interval: str):
        self.uri = None

    async def get_k_lines(self, pair) -> KLineData:
        """
        Get K-Line data for a trading pair
        :param pair:
        :return:
        """

    async def connect(self):
        self.websocket = await websockets.connect(self.uri)

    async def disconnect(self):
        ...

class BinanceWebSocketProvider(StockDataProvider):
    def __init__(self, pair: str, interval: str):
        self.pair = pair
        self.interval = interval
        self.uri = f"wss://stream.binance.com:9443/ws/{pair.lower()}@kline_{interval}"
        self.websocket = None


    async def disconnect(self):
        if self.websocket:
            await self.websocket.close()
            self.websocket = None

    async def get_k_lines(self) -> KLineData:
        if not self.websocket:
            await self.connect()

        try:
            message = await self.websocket.recv()
            data = json.loads(message)
            kline = data['k']

            kline_data = KLineData(
                timestamp=int(kline['t']),
                open=float(kline['o']),
                high=float(kline['h']),
                low=float(kline['l']),
                close=float(kline['c']),
                volume=float(kline['v'])
            )

            return kline_data

        except websockets.ConnectionClosed:
            print("Connection closed, attempting to reconnect...")
            await self.disconnect()
            await asyncio.sleep(5)
            return await self.get_k_lines()