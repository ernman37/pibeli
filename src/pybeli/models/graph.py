"""graph.py"""

from datetime import datetime

from pydantic import BaseModel, Field, model_validator

from pybeli.models.candle import Candle, CandleInterval


class Graph(BaseModel):
    """Graph.

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
        """validate_and_sort_candles.

        Validates the candles in the graph and sorts them by timestamp.

        Returns:
            Graph: The validated and sorted graph.

        Raises:
            ValueError: If any candle does not match the graph's ticker or interval.
        """
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
        """add_candle.

        Adds a candle to the graph.

        Raises:
            ValueError: If the candle does not match the
                graph's ticker or interval.
        """
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
        """remove_candle.

        Removes a candle from the graph if present.
        """
        while candle in self.candles:
            self.candles.remove(candle)

    def get_candle_by_timestamp(self, timestamp: datetime) -> Candle | None:
        """get_candle_by_timestamp.

        Retrieves a candle by its timestamp.

        Returns:
            Candle | None: The candle with the matching timestamp,
                or None if not found.
        """
        for candle in self.candles:
            if candle.timestamp == timestamp:
                return candle
        return None

    def get_candles_in_range(self, start: datetime, end: datetime) -> list[Candle]:
        """get_candles_in_range.

        Retrieves candles within a specific time range.

        Returns:
            list[Candle]: A list of candles within the specified range.
        """
        return [candle for candle in self.candles if start <= candle.timestamp <= end]

    def get_candles_before(self, timestamp: datetime) -> list[Candle]:
        """get_candles_before.

        Retrieves candles before a specific timestamp.

        Returns:
            list[Candle]: A list of candles before the specified timestamp.
        """
        return [candle for candle in self.candles if candle.timestamp < timestamp]

    def get_candles_after(self, timestamp: datetime) -> list[Candle]:
        """get_candles_after.

        Retrieves candles after a specific timestamp.

        Returns:
            list[Candle]: A list of candles after the specified timestamp.
        """
        return [candle for candle in self.candles if candle.timestamp > timestamp]

    def trim(self, count: int) -> None:
        """trim.

        Trims the candle list to the last 'count' candles.
        """
        self.candles = self.candles[-count:]

    def __contains__(self, candle: Candle) -> bool:
        """__contains__.

        Checks if a candle is in the graph.

        Args:
            candle (Candle): The candle to check for.

        Returns:
            bool: True if the candle is in the graph, False otherwise.
        """
        return candle in self.candles

    def __len__(self) -> int:
        """__len__.

        Length of the candle graph.

        Returns:
            int: The number of candles in the graph.
        """
        return len(self.candles)

    def __getitem__(self, index: int) -> Candle:
        """__getitem__.

        Get the candle at the specified index.

        Args:
            index (int): The index of the candle to retrieve.

        Returns:
            Candle: The candle at the specified index.

        Raises:
            IndexError: If the index is out of bounds.
        """
        return self.candles[index]
