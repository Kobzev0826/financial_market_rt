from fastapi import APIRouter
from fin_market_rt.third_party.facet import ServiceMixin

from fin_market_rt.entrypoints.web.api.v1.handlers import WebApiV1HandlersService
from fin_market_rt.third_party.giveme import inject, register


class WebApiHandlersService(ServiceMixin):
    def __init__(
        self,
        web_api_v1_handlers: WebApiV1HandlersService,
    ):
        self.web_api_v1_handlers = web_api_v1_handlers
        self.router = APIRouter()
        self._configure_routes()

    def _configure_routes(self) -> None:
        self.router.include_router(self.web_api_v1_handlers.router)

    @property
    def dependencies(self) -> list[ServiceMixin | list[ServiceMixin]]:
        return [
            self.web_api_v1_handlers,
        ]


@register(name="web_api_handlers")
@inject
def web_api_handlers_factory(
    web_api_v1_handlers: WebApiV1HandlersService,
) -> WebApiHandlersService:
    return WebApiHandlersService(
        web_api_v1_handlers=web_api_v1_handlers,
    )
