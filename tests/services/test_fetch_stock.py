from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any

import pytest

from pybeli.models.candle import CandleInterval
from pybeli.models.period import Period
from pybeli.services import fetch_stock as sut


@dataclass(frozen=True)
class _FakeScalar:
    value: Any

    def item(self) -> Any:
        return self.value


class _FakeDataFrame:
    def __init__(self, items: list[tuple[object, dict[str, Any]]]) -> None:
        self._items = items

    def iterrows(self):
        yield from self._items


def test_fetch_candles_builds_candle_objects(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_download(*_args: object, **_kwargs: object) -> _FakeDataFrame:
        return _FakeDataFrame(
            [
                (
                    "2024-01-01 09:30:00",
                    {
                        "Open": _FakeScalar(1.0),
                        "High": _FakeScalar(2.0),
                        "Low": _FakeScalar(0.5),
                        "Close": _FakeScalar(1.5),
                        "Volume": _FakeScalar(123),
                    },
                ),
                (
                    "2024-01-01 09:31:00",
                    {
                        "Open": _FakeScalar(10.0),
                        "High": _FakeScalar(20.0),
                        "Low": _FakeScalar(5.0),
                        "Close": _FakeScalar(15.0),
                        "Volume": _FakeScalar(456),
                    },
                ),
            ]
        )

    monkeypatch.setattr(sut, "download", fake_download)

    candles = sut.fetch_candles(
        ticker="AAPL",
        interval=CandleInterval.ONE_MINUTE,
        period=Period.ONE_DAY,
    )

    assert len(candles) == 2
    first = candles[0]
    assert first.ticker == "AAPL"
    assert first.interval == CandleInterval.ONE_MINUTE
    assert first.timestamp == datetime.fromisoformat("2024-01-01 09:30:00")
    assert first.open == 1.0
    assert first.high == 2.0
    assert first.low == 0.5
    assert first.close == 1.5
    assert first.volume == 123


def test_fetch_candles_empty_dataframe_returns_empty_list(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(sut, "download", lambda *_a, **_k: _FakeDataFrame([]))
    assert (
        sut.fetch_candles(
            ticker="AAPL",
            interval=CandleInterval.ONE_MINUTE,
            period=Period.ONE_DAY,
        )
        == []
    )


def test_fetch_graph_calls_fetch_candles_and_wraps_into_graph(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[tuple[str, CandleInterval, Period]] = []

    def fake_fetch_candles(
        ticker: str, interval: CandleInterval, period: Period
    ) -> list[object]:
        calls.append((ticker, interval, period))
        return []

    monkeypatch.setattr(sut, "fetch_candles", fake_fetch_candles)

    graph = sut.fetch_graph(
        ticker="MSFT",
        interval=CandleInterval.FIVE_MINUTES,
        period=Period.ONE_DAY,
    )

    assert calls == [("MSFT", CandleInterval.FIVE_MINUTES, Period.ONE_DAY)]
    assert graph.ticker == "MSFT"
    assert graph.interval == CandleInterval.FIVE_MINUTES
    assert graph.candles == []


def test_fetch_stock_creates_graphs_for_all_intervals(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[tuple[str, CandleInterval, Period]] = []

    def fake_fetch_graph(ticker: str, interval: CandleInterval, period: Period):
        calls.append((ticker, interval, period))
        return sut.Graph(ticker=ticker, interval=interval, candles=[])

    monkeypatch.setattr(sut, "fetch_graph", fake_fetch_graph)

    intervals = [CandleInterval.ONE_MINUTE, CandleInterval.FIVE_MINUTES]
    stock = sut.fetch_stock("TSLA", intervals=intervals, period=Period.ONE_DAY)

    assert stock.ticker == "TSLA"
    assert list(stock.graphs.keys()) == intervals
    assert calls == [
        ("TSLA", CandleInterval.ONE_MINUTE, Period.ONE_DAY),
        ("TSLA", CandleInterval.FIVE_MINUTES, Period.ONE_DAY),
    ]


def test_fetch_stocks_maps_each_ticker_to_fetch_stock(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[tuple[str, list[CandleInterval], Period]] = []

    def fake_fetch_stock(ticker: str, intervals: list[CandleInterval], period: Period):
        calls.append((ticker, intervals, period))
        return sut.Stock(ticker=ticker, graphs={})

    monkeypatch.setattr(sut, "fetch_stock", fake_fetch_stock)

    intervals = [CandleInterval.ONE_MINUTE]
    stocks = sut.fetch_stocks(
        tickers=["AAPL", "MSFT"],
        intervals=intervals,
        period=Period.ONE_DAY,
    )

    assert [s.ticker for s in stocks] == ["AAPL", "MSFT"]
    assert calls == [
        ("AAPL", intervals, Period.ONE_DAY),
        ("MSFT", intervals, Period.ONE_DAY),
    ]
