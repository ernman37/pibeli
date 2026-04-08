"""test_graph.py"""

from datetime import datetime, timedelta

import pytest

from pybeli.models.candle import Candle, CandleInterval
from pybeli.models.graph import Graph

T1 = datetime(2024, 1, 1, 9, 0)
T2 = datetime(2024, 1, 1, 9, 1)
T3 = datetime(2024, 1, 1, 9, 2)


def make_candle(ticker: str, interval: CandleInterval, timestamp: datetime) -> Candle:
    return Candle(
        ticker=ticker,
        open=100.0,
        high=110.0,
        low=90.0,
        close=105.0,
        volume=500.0,
        interval=interval,
        timestamp=timestamp,
    )


def test_duplicate_candles_removed() -> None:
    candles = [
        make_candle("AAPL", CandleInterval.ONE_MINUTE, T1),
        make_candle("AAPL", CandleInterval.ONE_MINUTE, T1),
        make_candle("AAPL", CandleInterval.ONE_MINUTE, T2),
    ]
    graph = Graph(ticker="AAPL", interval=CandleInterval.ONE_MINUTE, candles=candles)
    assert len(graph.candles) == 2
    assert graph.candles[0].timestamp == T1
    assert graph.candles[1].timestamp == T2


def test_candles_are_sorted_by_timestamp() -> None:
    candles = [
        make_candle("AAPL", CandleInterval.ONE_MINUTE, T3),
        make_candle("AAPL", CandleInterval.ONE_MINUTE, T1),
        make_candle("AAPL", CandleInterval.ONE_MINUTE, T2),
    ]
    graph = Graph(ticker="AAPL", interval=CandleInterval.ONE_MINUTE, candles=candles)
    timestamps = [c.timestamp for c in graph.candles]
    assert timestamps == sorted(timestamps)


def test_mismatched_ticker_raises() -> None:
    candles = [
        make_candle("AAPL", CandleInterval.ONE_MINUTE, T1),
        make_candle("TSLA", CandleInterval.ONE_MINUTE, T2),
    ]
    with pytest.raises(ValueError, match="ticker='AAPL'"):
        Graph(ticker="AAPL", interval=CandleInterval.ONE_MINUTE, candles=candles)


def test_mismatched_interval_raises() -> None:
    candles = [
        make_candle("AAPL", CandleInterval.ONE_MINUTE, T1),
        make_candle("AAPL", CandleInterval.ONE_HOUR, T2),
    ]
    with pytest.raises(ValueError, match="interval='1m'"):
        Graph(ticker="AAPL", interval=CandleInterval.ONE_MINUTE, candles=candles)


def test_add_candle_tail() -> None:
    graph = Graph(ticker="AAPL", interval=CandleInterval.ONE_MINUTE, candles=[])
    candle = make_candle("AAPL", CandleInterval.ONE_MINUTE, T1)
    graph.add_candle(candle)
    assert candle in graph
    assert graph[-1] == candle


def test_add_candle_head() -> None:
    graph = Graph(ticker="AAPL", interval=CandleInterval.ONE_MINUTE, candles=[])
    candle = make_candle("AAPL", CandleInterval.ONE_MINUTE, T1)
    graph.add_candle(candle)
    assert candle in graph
    assert graph[0] == candle


def test_add_candle_middle() -> None:
    graph = Graph(ticker="AAPL", interval=CandleInterval.ONE_MINUTE, candles=[])
    candle1 = make_candle("AAPL", CandleInterval.ONE_MINUTE, T1)
    candle2 = make_candle("AAPL", CandleInterval.ONE_MINUTE, T2)
    graph.add_candle(candle1)
    graph.add_candle(candle2)
    candle3 = make_candle("AAPL", CandleInterval.ONE_MINUTE, T1 + timedelta(seconds=30))
    graph.add_candle(candle3)
    assert candle3 in graph
    assert graph[1] == candle3


def test_add_candle_different_interval() -> None:
    graph = Graph(ticker="AAPL", interval=CandleInterval.ONE_MINUTE, candles=[])
    candle = make_candle("AAPL", CandleInterval.ONE_HOUR, T1)
    with pytest.raises(
        ValueError, match="Candle interval '1h' does not match graph interval '1m'"
    ):
        graph.add_candle(candle)


def test_add_candle_different_ticker() -> None:
    graph = Graph(ticker="AAPL", interval=CandleInterval.ONE_MINUTE, candles=[])
    candle = make_candle("TSLA", CandleInterval.ONE_MINUTE, T1)
    with pytest.raises(
        ValueError, match="Candle ticker 'TSLA' does not match graph ticker 'AAPL'"
    ):
        graph.add_candle(candle)


def test_add_duplicate_candle() -> None:
    graph = Graph(ticker="AAPL", interval=CandleInterval.ONE_MINUTE, candles=[])
    candle = make_candle("AAPL", CandleInterval.ONE_MINUTE, T1)
    graph.add_candle(candle)
    with pytest.raises(
        ValueError, match=f"Candle with timestamp '{T1}' already exists"
    ):
        graph.add_candle(candle)


def test_remove_candle() -> None:
    graph = Graph(ticker="AAPL", interval=CandleInterval.ONE_MINUTE, candles=[])
    candle = make_candle("AAPL", CandleInterval.ONE_MINUTE, T1)
    graph.add_candle(candle)
    graph.remove_candle(candle)
    assert candle not in graph


def test_get_candle_by_timestamp() -> None:
    graph = Graph(ticker="AAPL", interval=CandleInterval.ONE_MINUTE, candles=[])
    candle = make_candle("AAPL", CandleInterval.ONE_MINUTE, T1)
    graph.add_candle(candle)
    assert graph.get_candle_by_timestamp(T1) == candle
    assert graph.get_candle_by_timestamp(T2) is None


def test_get_candles_in_range() -> None:
    graph = Graph(ticker="AAPL", interval=CandleInterval.ONE_MINUTE, candles=[])
    candle1 = make_candle("AAPL", CandleInterval.ONE_MINUTE, T1)
    candle2 = make_candle("AAPL", CandleInterval.ONE_MINUTE, T2)
    candle3 = make_candle("AAPL", CandleInterval.ONE_MINUTE, T3)
    graph.add_candle(candle1)
    graph.add_candle(candle2)
    graph.add_candle(candle3)
    assert graph.get_candles_in_range(T1, T2) == [candle1, candle2]
    assert graph.get_candles_in_range(T1, T1) == [candle1]
    assert graph.get_candles_in_range(T2, T2) == [candle2]
    assert graph.get_candles_in_range(T1, T3) == [candle1, candle2, candle3]


def test_get_candles_before() -> None:
    graph = Graph(ticker="AAPL", interval=CandleInterval.ONE_MINUTE, candles=[])
    candle1 = make_candle("AAPL", CandleInterval.ONE_MINUTE, T1)
    candle2 = make_candle("AAPL", CandleInterval.ONE_MINUTE, T2)
    candle3 = make_candle("AAPL", CandleInterval.ONE_MINUTE, T3)
    graph.add_candle(candle1)
    graph.add_candle(candle2)
    graph.add_candle(candle3)
    assert graph.get_candles_before(T1) == []
    assert graph.get_candles_before(T2) == [candle1]
    assert graph.get_candles_before(T3) == [candle1, candle2]


def test_get_candles_after() -> None:
    graph = Graph(ticker="AAPL", interval=CandleInterval.ONE_MINUTE, candles=[])
    candle1 = make_candle("AAPL", CandleInterval.ONE_MINUTE, T1)
    candle2 = make_candle("AAPL", CandleInterval.ONE_MINUTE, T2)
    candle3 = make_candle("AAPL", CandleInterval.ONE_MINUTE, T3)
    graph.add_candle(candle1)
    graph.add_candle(candle2)
    graph.add_candle(candle3)
    assert graph.get_candles_after(T3) == []
    assert graph.get_candles_after(T2) == [candle3]
    assert graph.get_candles_after(T1) == [candle2, candle3]


def test_trim() -> None:
    graph = Graph(ticker="AAPL", interval=CandleInterval.ONE_MINUTE, candles=[])
    candle1 = make_candle("AAPL", CandleInterval.ONE_MINUTE, T1)
    candle2 = make_candle("AAPL", CandleInterval.ONE_MINUTE, T2)
    candle3 = make_candle("AAPL", CandleInterval.ONE_MINUTE, T3)
    graph.add_candle(candle1)
    graph.add_candle(candle2)
    graph.add_candle(candle3)
    graph.trim(2)
    assert len(graph) == 2
    assert graph[0] == candle2
    assert graph[1] == candle3


def test_contains() -> None:
    graph = Graph(ticker="AAPL", interval=CandleInterval.ONE_MINUTE, candles=[])
    candle1 = make_candle("AAPL", CandleInterval.ONE_MINUTE, T1)
    candle2 = make_candle("AAPL", CandleInterval.ONE_MINUTE, T2)
    graph.add_candle(candle1)
    graph.add_candle(candle2)
    assert candle1 in graph
    assert candle2 in graph
    assert make_candle("AAPL", CandleInterval.ONE_MINUTE, T3) not in graph


def test_len() -> None:
    graph = Graph(ticker="AAPL", interval=CandleInterval.ONE_MINUTE, candles=[])
    candle1 = make_candle("AAPL", CandleInterval.ONE_MINUTE, T1)
    candle2 = make_candle("AAPL", CandleInterval.ONE_MINUTE, T2)
    graph.add_candle(candle1)
    graph.add_candle(candle2)
    assert len(graph) == 2


def test_getitem() -> None:
    graph = Graph(ticker="AAPL", interval=CandleInterval.ONE_MINUTE, candles=[])
    candle1 = make_candle("AAPL", CandleInterval.ONE_MINUTE, T1)
    candle2 = make_candle("AAPL", CandleInterval.ONE_MINUTE, T2)
    graph.add_candle(candle1)
    graph.add_candle(candle2)
    assert graph[0] == candle1
    assert graph[1] == candle2
