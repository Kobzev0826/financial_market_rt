import asyncio
from typing import Type

from fin_market_rt.data_access.entites import KLineData
from fin_market_rt.data_access.sql_db import SqlDbService
from loguru import logger
from fin_market_rt.data_access.BinanceWebSocketClient import StockDataProvider, BinanceWebSocketProvider
from fin_market_rt.settings import Settings
from fin_market_rt.third_party.facet import ServiceMixin

from fin_market_rt.data_access.db_storage_service import DBStorage, KlineFinancialDataDataAccess
from fin_market_rt.third_party.giveme import register, inject


class KLineDataManager(ServiceMixin):
    def __init__(self, stock_data_provider: StockDataProvider, kline_financial_data_access: KlineFinancialDataDataAccess):
        self.ws_client = stock_data_provider
        self.db_manager = kline_financial_data_access

    async def manage_data_flow(self):
        await self.ws_client.connect()
        while True:
            try:
                kline_data = await self.ws_client.get_k_lines()
                logger.info(f"K-Line data received: {kline_data}")

                await self.db_manager.add_new_kline_data(kline_data)

            except Exception as e:
                print(f"An error occurred: {e}")
                await asyncio.sleep(5)
        await self.ws_client.disconnect()


@register(name="kline_data_manager", singleton=True)
@inject
def kline_data_manager_factory(
kline_financial_data_access: KlineFinancialDataDataAccess
) -> KLineDataManager:
    return KLineDataManager(
        BinanceWebSocketProvider("ETHUSDT", "1m"),
        kline_financial_data_access
    )