from __future__ import annotations

import math

import pytest
from utils import create_candle, create_datetime

from pybeli.models.candle import Candle
from pybeli.models.rsi import RSI, RSIStrategy
from pybeli.models.signal import Signal


def _candles_from_closes(
    closes: list[float],
    *,
    ticker: str = "TEST",
) -> list[Candle]:
    candles: list[Candle] = []
    for i, close in enumerate(closes):
        candles.append(
            create_candle(
                ticker=ticker,
                timestamp=create_datetime(minute=i),
                close=close,
            )
        )
    return candles


def test_calculate_raises_when_not_enough_candles() -> None:
    candles = _candles_from_closes([1.0, 2.0])
    with pytest.raises(ValueError, match="Not enough candles to calculate RSI"):
        RSI.calculate(candles, window=14)


def test_calculate_all_gains_produces_100_rsi() -> None:
    candles = _candles_from_closes([float(i) for i in range(1, 17)])

    window = 14
    values = RSI.calculate(candles, window=window)

    assert len(values) == len(candles) - window

    first = values[0]
    assert first.ticker == "TEST"
    assert first.window == window
    assert first.timestamp == candles[window].timestamp
    assert first.value == 100.0

    assert all(v.value == 100.0 for v in values)


def test_calculate_mixed_changes_matches_expected_rsi() -> None:
    closes = [
        10,
        11,
        12,
        11,
        13,
        12,
        14,
    ]
    candles = _candles_from_closes([float(x) for x in closes], ticker="ABC")

    window = 3
    values = RSI.calculate(candles, window=window)

    assert len(values) == len(candles) - window

    changes = [candles[i].close - candles[i - 1].close for i in range(1, window + 1)]
    gains = [max(c, 0.0) for c in changes]
    losses = [max(-c, 0.0) for c in changes]

    avg_gain = sum(gains) / window
    avg_loss = sum(losses) / window
    rs = avg_gain / avg_loss
    expected = 100 - (100 / (1 + rs))

    first = values[0]
    assert first.ticker == "ABC"
    assert first.window == window
    assert first.timestamp == candles[window].timestamp
    assert math.isclose(first.value, expected, rel_tol=0, abs_tol=1e-12)


def test_analyze_buy_signal() -> None:
    strategy = RSIStrategy(buy_threshold=30, sell_threshold=70)
    datetime = create_datetime(minute=0)
    ticker = "TEST"
    rsi = RSI(value=25, timestamp=datetime, ticker=ticker, interval="1d", window=14)
    signal = strategy.analyze(rsi)
    assert signal == Signal.BUY
    rsi = RSI(value=75, timestamp=datetime, ticker=ticker, interval="1d", window=14)
    signal = strategy.analyze(rsi)
    assert signal == Signal.SELL
    rsi = RSI(value=50, timestamp=datetime, ticker=ticker, interval="1d", window=14)
    signal = strategy.analyze(rsi)
    assert signal == Signal.WAIT
