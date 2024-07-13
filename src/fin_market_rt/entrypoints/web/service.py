from fin_market_rt.third_party.facet import ServiceMixin

from fin_market_rt.third_party.giveme import register, inject

from fin_market_rt.entrypoints.web.net import NetHttpServer

from fin_market_rt.entrypoints.web.api.handlers import WebApiHandlersService


class FinancialMarketWebService(ServiceMixin):
    def __init__(
        self,
        web_api_handlers: WebApiHandlersService,
        net_http_server: NetHttpServer,
    ):
        self.web_api_handlers = web_api_handlers
        self.server = net_http_server

    @property
    def dependencies(self) -> list[ServiceMixin | list[ServiceMixin]]:
        return [
            self.web_api_handlers,
            self.server,
        ]

    async def start(self) -> None:
        self.server.app.include_router(self.web_api_handlers.router)


@register(name="fmrt_web_service", singleton=True)
@inject
def sm_web_service_factory(
    web_api_handlers: WebApiHandlersService,
    net_http_server: NetHttpServer,
) -> FinancialMarketWebService:
    return FinancialMarketWebService(
        web_api_handlers=web_api_handlers,
        net_http_server=net_http_server,
    )
