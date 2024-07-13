import asyncio
from contextlib import suppress

from src.fin_market_rt.data_access.BinanceWebSocketClient import BinanceWebSocketProvider
from src.fin_market_rt.data_access.db_storage_service import DBStorage
from src.fin_market_rt.services.stock_data_ingestion_service import KLineDataManager
from src.fin_market_rt.settings import Settings


async def amain() -> None:
    stock_data_service = KLineDataManager(BinanceWebSocketProvider, DBStorage, Settings)
    await stock_data_service.manage_data_flow()

def main() -> None:
    with suppress(KeyboardInterrupt):
        asyncio.run(amain())


if __name__ == "__main__":
    main()