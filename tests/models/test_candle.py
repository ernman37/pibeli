"""test_candle.py"""

from datetime import datetime

from pybeli.models.candle import Candle, CandleInterval


def test_candle_model_constructor():
    candle = Candle(
        ticker="AAPL",
        open=150.0,
        high=155.0,
        low=149.0,
        close=154.0,
        volume=1000.0,
        interval=CandleInterval.ONE_MINUTE,
        timestamp=datetime.now(),
    )
    assert candle.ticker == "AAPL"
    assert candle.open == 150.0
    assert candle.high == 155.0
    assert candle.low == 149.0
    assert candle.close == 154.0
    assert candle.volume == 1000.0
    assert candle.interval == CandleInterval.ONE_MINUTE
    assert candle.timestamp is not None
