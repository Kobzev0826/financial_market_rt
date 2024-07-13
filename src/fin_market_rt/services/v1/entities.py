from enum import Enum

from fin_market_rt.data_access.entites import KLineData


class IntervalEnum(Enum):
    ONEMIN = '1m'
    FIVEMIN = '5m'
    HOUR = '60m'

ListKLineData = list[KLineData]