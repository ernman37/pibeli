"""rsi.py"""

from datetime import datetime

from pydantic import BaseModel, Field

from pybeli.models.candle import Candle, CandleInterval
from pybeli.models.signal import Signal


class RSI(BaseModel):
    """Relative Strength Index (RSI) calculation.

    The RSI is a momentum oscillator that measures the speed and change of price
    movements.
    It is typically used to identify overbought or oversold conditions in a market.
    """

    timestamp: datetime = Field(..., description="The timestamp of the RSI value")
    ticker: str = Field(..., description="The ticker symbol for the asset")
    interval: CandleInterval = Field(
        ..., description="The time interval for the RSI calculation"
    )
    window: int = Field(
        ..., description="The number of periods to use for the RSI calculation"
    )
    value: float = Field(..., description="The RSI value")

    @staticmethod
    def calculate(candles: list[Candle], window: int = 14) -> list["RSI"]:
        """
        Calculate the RSI values for a list of candles.

        Args:
            candles: A list of Candle objects to calculate the RSI for.
            window: The number of periods to use for the RSI calculation (default is
                14).

        Returns:
            A list of RSI objects corresponding to each candle.
        """
        if len(candles) < window + 1:
            raise ValueError("Not enough candles to calculate RSI")

        rsi_values: list[RSI] = []
        gains: list[float] = []
        losses: list[float] = []

        for i in range(1, len(candles)):
            change = candles[i].close - candles[i - 1].close
            gain = max(change, 0)
            loss = max(-change, 0)

            gains.append(gain)
            losses.append(loss)

            if i < window:
                continue

            avg_gain = sum(gains[-window:]) / window
            avg_loss = sum(losses[-window:]) / window

            if avg_loss == 0:
                rsi = 100.0
            else:
                rs = avg_gain / avg_loss
                rsi = 100 - (100 / (1 + rs))

            rsi_values.append(
                RSI(
                    timestamp=candles[i].timestamp,
                    ticker=candles[i].ticker,
                    interval=candles[i].interval,
                    window=window,
                    value=rsi,
                )
            )

        return rsi_values


class RSIStrategy(BaseModel):
    """
    A strategy for trading based on the Relative Strength Index (RSI) indicator.

    Attributes:
        buy_threshold: The RSI value below which to buy.
        sell_threshold: The RSI value above which to sell.
    """

    buy_threshold: float = Field(..., description="The RSI value below which to buy")
    sell_threshold: float = Field(..., description="The RSI value above which to sell")

    def analyze(self, rsi: RSI) -> Signal:
        """
        Analyze the RSI value and return a trading signal.

        Args:
            rsi: The RSI value to analyze.

        Returns:
            A trading signal indicating whether to buy, sell, or hold.
        """
        if rsi.value < self.buy_threshold:
            return Signal.BUY
        elif rsi.value > self.sell_threshold:
            return Signal.SELL
        return Signal.WAIT
