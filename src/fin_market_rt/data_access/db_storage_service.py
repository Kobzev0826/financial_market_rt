from abc import ABC

from fin_market_rt.data_access.entites import KLineData
import sqlalchemy as sa
from fin_market_rt.data_access.sql_db import SqlDbService
from fin_market_rt.third_party.facet import ServiceMixin
from fin_market_rt.third_party.giveme import inject, register
from sqlalchemy.ext.declarative import declarative_base

from fin_market_rt.data_access.tables import KLineDataTable
from fin_market_rt.settings import Settings
from loguru import logger

from src.fin_market_rt.services.v1.entities import IntervalEnum

Base = declarative_base()


class DBStorage(ABC):
    ...

    def save_to_db(self, kline_data):
        pass


class KlineFinancialDataDataAccess(DBStorage, ServiceMixin):
    def __init__(self, sql_db: SqlDbService, settings: Settings):
        self.sql_db = sql_db
        self.cache: dict[int, KLineData] = {}
        self.cache_treshold = settings.project.cache_treshold + settings.project.metrics_min_data_size
        self.batch_size = settings.project.cache_treshold
        # asyncio.create_task(self.sql_db.create_tables())

    @property
    def dependencies(self) -> list[ServiceMixin | list[ServiceMixin]]:
        return [
            self.sql_db,
        ]

    async def add_new_kline_data(self, kline_data: KLineData):
        self.cache.update({kline_data.timestamp: kline_data})
        await self.check_and_save()

    async def check_and_save(self):
        if len(self.cache) >= self.cache_treshold:
            await self.save_to_db(list(self.cache.values())[:self.batch_size])
            self.cache.clear()

    async def save_to_db(self, kline_data: list[KLineData]):
        insert_stmt = sa.insert(KLineDataTable)
        batch_data = []
        batch_data.extend([{
            'timestamp': data.timestamp,
            'open': data.open,
            'high': data.high,
            'low': data.low,
            'close': data.close,
            'volume': data.volume
        } for data in kline_data])

        async with self.sql_db.transaction() as conn:
            await conn.execute(insert_stmt, batch_data)
        logger.info(f"K-Line data saved to database: {kline_data}")

    async def get_k_data(self, k: int) -> list[KLineData]:
        select_stmt = sa.select(KLineDataTable).limit(k)
        async with self.sql_db.transaction() as conn:
            result = await conn.execute(select_stmt)
            rows = result.fetchall()
            breakpoint()
            return [KLineData(**row._mapping) for row in rows]

    async def get_kline(self, interval: IntervalEnum, num: int) -> list[KLineData]:

        # v = list(self.cache.values())
        # return v[-num:]
        k_line_data = await self.get_k_data(num)
        return k_line_data

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
