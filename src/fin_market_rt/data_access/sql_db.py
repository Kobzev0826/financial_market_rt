import ssl
import time
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from enum import Enum
from typing import Any
from loguru import logger
import sqlalchemy as sa
from async_timeout import timeout
from fin_market_rt.third_party.facet import ServiceMixin
from sqlalchemy.ext.asyncio import AsyncConnection, create_async_engine

from fin_market_rt.helpers.backoff import default_backoff

from src.fin_market_rt.data_access.tables import metadata
from src.fin_market_rt.settings import Settings
from src.fin_market_rt.third_party.giveme import register, inject


# https://github.com/python/typing/issues/236#issuecomment-227180301
class Empty(Enum):
    value = -1


class SqlDbService(ServiceMixin):
    def __init__(
        self,
        url: str,
        pool_size: int,
        pool_recycle: int,
        healthy_delay: float,
        healthcheck_timeout: float,
        query_timeout: float | None = None,
        force_unverified_ssl: bool = False,
    ):
        # workaround for https://github.com/aio-libs/aiomysql/issues/757
        connect_args = {}
        if force_unverified_ssl:
            context = ssl.create_default_context()  # NOSONAR
            context.check_hostname = False  # NOSONAR
            context.verify_mode = ssl.CERT_NONE  # NOSONAR
            connect_args["ssl"] = context

        self.engine = create_async_engine(
            url,
            pool_size=pool_size,
            pool_recycle=pool_recycle,
            connect_args=connect_args,
        )
        self.query_timeout = query_timeout
        self.healthcheck_timeout = healthcheck_timeout
        self.healthy_delay = healthy_delay
        self._last_successful_execute_timestamp: float | None = None

    @default_backoff(max_value=5, max_time=60)
    async def start(self) -> None:
        await self.execute(sa.select(1))

    async def stop(self) -> None:
        await self.engine.dispose()

    @asynccontextmanager
    async def transaction(self) -> AsyncGenerator[AsyncConnection, None]:
        async with self.engine.begin() as connection:
            yield connection  # NOSONAR

    async def execute(
        self,
        query: sa.sql.expression.Executable,
        query_timeout: float | None | Empty = Empty.value,
    ) -> sa.CursorResult[Any]:
        if query_timeout is Empty.value:
            query_timeout = self.query_timeout
        async with timeout(query_timeout), self.transaction() as connection:
            res = await connection.execute(query)
            self._last_successful_execute_timestamp = time.monotonic()
            return res

    async def is_accessible(self) -> bool:
        """
        Checks if a dummy select request can be executed
        """
        if (
            self._last_successful_execute_timestamp
            and time.monotonic() - self._last_successful_execute_timestamp < self.healthy_delay
        ):
            return True

        query = sa.select(1)
        try:
            await self.execute(
                query,
                query_timeout=self.healthcheck_timeout,
            )
        except Exception as exc:
            logger.error("SQL DB is not accessible", exc_info=exc)
            return False
        else:
            return True

    async def create_tables(self) -> None:
        async with self.transaction() as connection:
            await connection.run_sync(metadata.create_all)

    async def drop_tables(self) -> None:
        async with self.transaction() as connection:
            await connection.run_sync(metadata.drop_all)


@register(name="sql_db", singleton=True)
@inject
def sql_db_factory(settings: Settings) -> SqlDbService:
    return SqlDbService(
        url=settings.sql_db_url_resolved,
        pool_size=settings.sql_db_pool_size,
        pool_recycle=settings.sql_db_pool_recycle,
        query_timeout=settings.sql_db_query_timeout,
        force_unverified_ssl=settings.sql_db_force_unverified_ssl,
        healthy_delay=settings.sql_db_healthy_delay,
        healthcheck_timeout=settings.sql_db_healthcheck_timeout,
    )
