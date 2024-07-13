from fastapi import APIRouter, Body, HTTPException, Query, status
from fin_market_rt.data_access.db_storage_service import KlineFinancialDataDataAccess
from fin_market_rt.third_party.facet import ServiceMixin

from fin_market_rt.third_party.giveme import register, inject

from fin_market_rt.services.v1.entities import IntervalEnum

from src.fin_market_rt.services.v1.entities import ListKLineData


class WebApiV1HandlersService(ServiceMixin):
    def __init__(self, market_data_operations_service: KlineFinancialDataDataAccess) -> None:
        self.market_data_operations_service = market_data_operations_service
        self.router = APIRouter()
        self._configure_routes()

    @property
    def dependencies(self) -> list[ServiceMixin | list[ServiceMixin]]:
        return [
            self.market_data_operations_service,
        ]

    def _configure_routes(self) -> None:
        router = APIRouter(tags=["klines_data"])
        router.add_api_route("/klines_data", self.get_kline_data, methods=["get"])
        self.router.include_router(router)

        # router = APIRouter(tags=["export ranking configuration"])
        # router.add_api_route("/export_ranking_cfg", self.export_ranking_configurations, methods=["post"])
        # self.router.include_router(router)

    async def get_kline_data(self, interval: IntervalEnum = Query(...), num: int = Query(...)) -> ListKLineData:
        return await self.market_data_operations_service.get_kline(interval, num)


@register(name="web_api_v1_handlers", singleton=True)
@inject
def web_api_v1_handlers_factory(kline_financial_data_access: KlineFinancialDataDataAccess) -> WebApiV1HandlersService:
    return WebApiV1HandlersService(
        market_data_operations_service=kline_financial_data_access,
    )
