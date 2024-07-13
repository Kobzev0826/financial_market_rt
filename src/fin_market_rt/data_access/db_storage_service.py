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
    def __init__(self, sql_db :SqlDbService):
        self.sql_db = sql_db
        # asyncio.create_task(self.sql_db.create_tables())


    async def save_to_db(self, kline_data: KLineData):
        insert_stmt = sa.insert(KLineDataTable).values(
            timestamp=kline_data.timestamp,
            open=kline_data.open,
            high=kline_data.high,
            low=kline_data.low,
            close=kline_data.close,
            volume=kline_data.volume
        )

        async with self.sql_db.transaction() as conn:
            await conn.execute(insert_stmt)
        logger.info(f"K-Line data saved to database: {kline_data}")


# @register(name="kline_financial_data_access", singleton=True)
# @inject
# def kline_financial_data_access_factory(sql_db: SqlDbService) -> DBStorage:
#     return KlineFinancialDataDataAccess(
#         sql_db=sql_db,
#     )