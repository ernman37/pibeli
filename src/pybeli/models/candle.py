"""candle.py"""

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field


class CandleInterval(StrEnum):
    ONE_MINUTE = "1m"
    FIVE_MINUTES = "5m"
    FIFTEEN_MINUTES = "15m"
    ONE_HOUR = "1h"
    ONE_DAY = "1d"


class Candle(BaseModel):
    ticker: str = Field(..., description="The ticker symbol of the asset")
    open: float = Field(..., description="The opening price of the candle")
    high: float = Field(..., description="The highest price of the candle")
    low: float = Field(..., description="The lowest price of the candle")
    close: float = Field(..., description="The closing price of the candle")
    volume: float = Field(..., description="The trading volume of the candle")
    interval: CandleInterval = Field(..., description="The time interval of the candle")
    timestamp: datetime = Field(..., description="The timestamp of the candle")

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Candle):
            return NotImplemented
        return (
            self.ticker == other.ticker
            and self.interval == other.interval
            and self.timestamp == other.timestamp
        )

    def __hash__(self) -> int:
        return hash((self.ticker, self.interval, self.timestamp))
