import asyncio
from contextlib import suppress

from fin_market_rt.data_access.BinanceWebSocketClient import BinanceWebSocketProvider
from fin_market_rt.data_access.db_storage_service import DBStorage
from fin_market_rt.entrypoints.web.service import FinancialMarketWebService
from fin_market_rt.services.stock_data_ingestion_service import KLineDataManager
from fin_market_rt.settings import Settings
from fin_market_rt.third_party.giveme import inject


@inject
async def amain_kline(kline_data_manager: KLineDataManager) -> None:
    await kline_data_manager.manage_data_flow()

@inject
async def amain_api(fmrt_web_service: FinancialMarketWebService) -> None:
    await fmrt_web_service.run()

async def amain() -> None:
    await asyncio.gather(
        amain_kline(),
        amain_api(),
    )


def main() -> None:
    with suppress(KeyboardInterrupt):
        asyncio.run(amain())

if __name__ == "__main__":
    main()