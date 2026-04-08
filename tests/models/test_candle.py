"""test_candle.py"""

from datetime import datetime, timedelta

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


def test_candle_equality() -> None:
    now = datetime.now()
    candle1 = Candle(
        ticker="AAPL",
        open=150.0,
        high=155.0,
        low=149.0,
        close=154.0,
        volume=1000.0,
        interval=CandleInterval.ONE_MINUTE,
        timestamp=now,
    )
    candle2 = Candle(
        ticker="AAPL",
        open=150.0,
        high=155.0,
        low=149.0,
        close=154.0,
        volume=1000.0,
        interval=CandleInterval.ONE_MINUTE,
        timestamp=now,
    )
    candle3 = Candle(
        ticker="AAPL",
        open=150.0,
        high=155.0,
        low=149.0,
        close=154.0,
        volume=1000.0,
        interval=CandleInterval.ONE_MINUTE,
        timestamp=now + timedelta(minutes=1),
    )
    assert candle1 == candle2
    assert candle1 != candle3
    assert candle1 != object()


def test_candle_hash() -> None:
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
    assert isinstance(hash(candle), int)
    assert hash(candle) == hash((candle.ticker, candle.interval, candle.timestamp))
