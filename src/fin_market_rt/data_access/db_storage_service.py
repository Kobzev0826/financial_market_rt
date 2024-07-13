import asyncio
from abc import ABC
from datetime import datetime

from fin_market_rt.data_access.entites import KLineData
import sqlalchemy as sa
from fin_market_rt.data_access.sql_db import SqlDbService
from fin_market_rt.third_party.facet import ServiceMixin
from fin_market_rt.third_party.giveme import inject, register
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from fin_market_rt.data_access.tables import KLineDataTable
from fin_market_rt.settings import Settings
from loguru import logger
Base = declarative_base()
class DBStorage(ABC):
    ...

    def save_to_db(self, kline_data):
        pass


class KlineFinancialDataDataAccess(DBStorage, ServiceMixin):
    def __init__(self, sql_db :SqlDbService, settings: Settings):
        self.sql_db = sql_db
        self.cache: dict[int,KLineData] = {}
        self.cache_treshold = settings.project.cache_treshold + settings.project.metrics_min_data_size
        self.batch_size = settings.project.cache_treshold
        # asyncio.create_task(self.sql_db.create_tables())

    async def add_new_kline_data(self, kline_data: KLineData):
        self.cache.update({kline_data.timestamp:kline_data})
        await self.check_and_save()

    async def check_and_save(self):
        if len(self.cache) >= self.cache_treshold:
            await self.save_to_db(list(self.cache.values())[:self.batch_size])
            self.cache.clear()

    async def save_to_db(self, kline_data: list[KLineData]):
        insert_stmt = sa.insert(KLineDataTable)
        # .values(
        #     timestamp=kline_data.timestamp,
        #     open=kline_data.open,
        #     high=kline_data.high,
        #     low=kline_data.low,
        #     close=kline_data.close,
        #     volume=kline_data.volume
        # ))
        batch_data = []
        batch_data.extend([{
            'timestamp': data.timestamp,
            'open': data.open,
            'high': data.high,
            'low': data.low,
            'close': data.close,
            'volume': data.volume
        } for data in kline_data])
        breakpoint()
        async with self.sql_db.transaction() as conn:
            await conn.execute(insert_stmt, batch_data)
        logger.info(f"K-Line data saved to database: {kline_data}")


@register(name="kline_financial_data_access", singleton=True)
@inject
def kline_financial_data_access_factory(
        sql_db: SqlDbService,
        settings: Settings
) -> DBStorage:
    return KlineFinancialDataDataAccess(
        sql_db=sql_db,
        settings=settings
    )