"""graph.py"""

from datetime import datetime

from pydantic import BaseModel, Field, model_validator

from pybeli.models.candle import Candle, CandleInterval


class Graph(BaseModel):
    """
    Represents a collection of Candles for a specific ticker and time interval.

    Attributes:
        ticker (str): The ticker symbol of the asset.
        interval (CandleInterval): The time interval of the candles.
        candles (list[Candle]): A list of Candle objects sorted by timestamp.
    """

    ticker: str = Field(..., frozen=True, description="The ticker symbol of the asset")
    interval: CandleInterval = Field(
        ..., frozen=True, description="The time interval of the candles"
    )
    candles: list[Candle] = Field(..., description="A list of Candle objects")

    @model_validator(mode="after")
    def validate_and_sort_candles(self) -> "Graph":
        mismatched = [
            c
            for c in self.candles
            if c.ticker != self.ticker or c.interval != self.interval
        ]
        if mismatched:
            raise ValueError(
                f"{len(mismatched)} candle(s) do not match ticker='{self.ticker}' "
                f"and interval='{self.interval}': "
                + ", ".join(f"({c.ticker}, {c.interval})" for c in mismatched)
            )
        self.candles = sorted(set(self.candles), key=lambda c: c.timestamp)
        return self

    def add_candle(self, candle: Candle) -> None:
        if candle.ticker != self.ticker:
            raise ValueError(
                f"Candle ticker '{candle.ticker}' "
                f"does not match graph ticker '{self.ticker}'"
            )
        if candle.interval != self.interval:
            raise ValueError(
                f"Candle interval '{candle.interval}' "
                f"does not match graph interval '{self.interval}'"
            )
        if candle in self.candles:
            raise ValueError(
                f"Candle with timestamp '{candle.timestamp}' already exists"
            )
        for i in range(len(self.candles)):
            if self.candles[i].timestamp > candle.timestamp:
                self.candles.insert(i, candle)
                return
        self.candles.append(candle)

    def remove_candle(self, candle: Candle) -> None:
        while candle in self.candles:
            self.candles.remove(candle)

    def get_candle_by_timestamp(self, timestamp: datetime) -> Candle | None:
        for candle in self.candles:
            if candle.timestamp == timestamp:
                return candle
        return None

    def get_candles_in_range(self, start: datetime, end: datetime) -> list[Candle]:
        return [candle for candle in self.candles if start <= candle.timestamp <= end]

    def get_candles_before(self, timestamp: datetime) -> list[Candle]:
        return [candle for candle in self.candles if candle.timestamp < timestamp]

    def get_candles_after(self, timestamp: datetime) -> list[Candle]:
        return [candle for candle in self.candles if candle.timestamp > timestamp]

    def trim(self, count: int) -> None:
        self.candles = self.candles[-count:]

    def __contains__(self, candle: Candle) -> bool:
        return candle in self.candles

    def __len__(self) -> int:
        return len(self.candles)

    def __getitem__(self, index: int) -> Candle:
        return self.candles[index]
