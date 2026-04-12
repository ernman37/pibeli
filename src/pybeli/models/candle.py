"""candle.py"""

from datetime import datetime
from enum import StrEnum

from pydantic import BaseModel, Field


class CandleInterval(StrEnum):
    """
    Candle intervals.

    Represents the time intervals for candlestick data in stock charts.

    Valid intervals: 1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo
    """

    ONE_MINUTE = "1m"
    TWO_MINUTES = "2m"
    FIVE_MINUTES = "5m"
    FIFTEEN_MINUTES = "15m"
    THIRTY_MINUTES = "30m"
    SIXTY_MINUTES = "60m"
    NINETY_MINUTES = "90m"
    ONE_HOUR = "1h"
    ONE_DAY = "1d"
    FIVE_DAYS = "5d"
    ONE_WEEK = "1wk"
    ONE_MONTH = "1mo"
    THREE_MONTHS = "3mo"


class Candle(BaseModel):
    """Candle.

    Represents a single candlestick in a stock chart

    Attributes:
        ticker (str): The ticker symbol of the asset.
        open (float): The opening price of the candle.
        high (float): The highest price of the candle.
        low (float): The lowest price of the candle.
        close (float): The closing price of the candle.
        volume (float): The trading volume of the candle.
        interval (CandleInterval): The time interval of the candle.
        timestamp (datetime): The timestamp of the candle.
    """

    ticker: str = Field(..., description="The ticker symbol of the asset")
    open: float = Field(..., description="The opening price of the candle")
    high: float = Field(..., description="The highest price of the candle")
    low: float = Field(..., description="The lowest price of the candle")
    close: float = Field(..., description="The closing price of the candle")
    volume: float = Field(..., description="The trading volume of the candle")
    interval: CandleInterval = Field(..., description="The time interval of the candle")
    timestamp: datetime = Field(..., description="The timestamp of the candle")

    def __eq__(self, other: object) -> bool:
        """__eq__.

        Two candles are considered equal if they have the same
        ticker, interval, and timestamp.

        Returns:
            bool: True if the candles are equal, False otherwise.
        """
        if not isinstance(other, Candle):
            return NotImplemented
        return (
            self.ticker == other.ticker
            and self.interval == other.interval
            and self.timestamp == other.timestamp
        )

    def __hash__(self) -> int:
        """__hash__.

        Returns a hash of the candle based on its ticker, interval, and timestamp.

        Returns:
            int: A hash of the candle.
        """
        return hash((self.ticker, self.interval, self.timestamp))
