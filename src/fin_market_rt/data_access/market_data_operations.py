from fin_market_rt.data_access.sql_db import SqlDbService
from fin_market_rt.third_party.facet import ServiceMixin


class MarketDataOperationsDataAccess(ServiceMixin):
    def __init__(self, sql_db: SqlDbService):
        self.sql_db = sql_db


