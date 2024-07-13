from pydantic import BaseModel, HttpUrl


class KLineData(BaseModel):
    timestamp: int
    open: float
    high: float
    low: float
    close: float
    volume: float