from fin_market_rt.third_party.facet import ServiceMixin
from fin_market_rt.third_party.giveme import inject, register


class MarketDataOperationsService(ServiceMixin):
    ...


@register(name="market_data_operations_service", singleton=True)
@inject
def market_data_operations_service_factory() -> MarketDataOperationsService:
    return MarketDataOperationsService(
    )
