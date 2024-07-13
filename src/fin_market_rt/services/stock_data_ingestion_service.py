import asyncio
from typing import Type

from fin_market_rt.data_access.BinanceWebSocketClient import StockDataProvider
from fin_market_rt.settings import Settings

from src.fin_market_rt.data_access.db_storage_service import DBStorage


class KLineDataManager:
    def __init__(self, stock_data_provider: Type[StockDataProvider], db_storage: Type[DBStorage], settings: Settings):
        self.ws_client = stock_data_provider("ETHUSDT", "1m")
        self.db_manager = db_storage()

    async def manage_data_flow(self):
        # await self.db_manager.create_pool()
        await self.ws_client.connect()
        while True:
            try:
                kline_data = await self.ws_client.get_k_lines()
                print("K-Line Data:")
                print(f" Open: {kline_data.open}")
                print(f" High: {kline_data.high}")
                print(f" Low: {kline_data.low}")
                print(f" Close: {kline_data.close}")
                print(f" Volume: {kline_data.volume}")
                print()

                # asyncio.create_task(self.db_manager.save_to_db(kline_data))

            except Exception as e:
                print(f"An error occurred: {e}")
                await asyncio.sleep(5)
        await self.ws_client.disconnect()