import asyncio
from contextlib import suppress

from fin_market_rt.entrypoints.web.service import FinancialMarketWebService
from fin_market_rt.settings import Settings
from fin_market_rt.third_party.giveme import inject


@inject
async def amain(fmrt_web_service: FinancialMarketWebService) -> None:
    await fmrt_web_service.run()


if __name__ == "__main__":
    with suppress(KeyboardInterrupt):
        asyncio.run(amain())
