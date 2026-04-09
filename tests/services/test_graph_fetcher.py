"""test_graph_fetcher.py"""

from collections.abc import Iterator
from datetime import UTC, datetime
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest

from pybeli.models.candle import CandleInterval
from pybeli.models.graph import Graph
from pybeli.services.graph_fetcher import fetch_graph


def _make_df(rows: list[dict[str, float]], timestamps: list[datetime]) -> pd.DataFrame:
    """Build a minimal OHLCV DataFrame matching yfinance output."""
    df = pd.DataFrame(rows, index=pd.DatetimeIndex(timestamps))
    df.index.name = "Datetime"
    return df


T1 = datetime(2024, 1, 1, 9, 0, tzinfo=UTC)
T2 = datetime(2024, 1, 1, 9, 1, tzinfo=UTC)
T3 = datetime(2024, 1, 1, 9, 2, tzinfo=UTC)

_ROW = {"Open": 100.0, "High": 110.0, "Low": 90.0, "Close": 105.0, "Volume": 500.0}


@pytest.fixture()
def mock_download() -> Iterator[MagicMock]:
    with patch("pybeli.services.graph_fetcher.yf.download") as mock:
        yield mock


def test_returns_graph(mock_download: MagicMock) -> None:
    mock_download.return_value = _make_df([_ROW, _ROW], [T1, T2])
    graph = fetch_graph("AAPL", CandleInterval.ONE_MINUTE)
    assert isinstance(graph, Graph)
    assert graph.ticker == "AAPL"
    assert graph.interval == CandleInterval.ONE_MINUTE


def test_candle_count_matches_rows(mock_download: MagicMock) -> None:
    mock_download.return_value = _make_df([_ROW, _ROW, _ROW], [T1, T2, T3])
    graph = fetch_graph("AAPL", CandleInterval.ONE_MINUTE)
    assert len(graph) == 3


def test_candle_fields_mapped_correctly(mock_download: MagicMock) -> None:
    mock_download.return_value = _make_df([_ROW], [T1])
    graph = fetch_graph("AAPL", CandleInterval.ONE_MINUTE)
    candle = graph[0]
    assert candle.ticker == "AAPL"
    assert candle.interval == CandleInterval.ONE_MINUTE
    assert candle.open == 100.0
    assert candle.high == 110.0
    assert candle.low == 90.0
    assert candle.close == 105.0
    assert candle.volume == 500.0
    assert candle.timestamp == T1


def test_candles_are_sorted_by_timestamp(mock_download: MagicMock) -> None:
    # Return rows in reverse order — fetcher must sort them
    mock_download.return_value = _make_df([_ROW, _ROW, _ROW], [T3, T1, T2])
    graph = fetch_graph("AAPL", CandleInterval.ONE_MINUTE)
    timestamps = [c.timestamp for c in graph.candles]
    assert timestamps == sorted(timestamps)


def test_default_period_used_when_not_provided(mock_download: MagicMock) -> None:
    mock_download.return_value = _make_df([_ROW], [T1])
    fetch_graph("AAPL", CandleInterval.ONE_MINUTE)
    _, kwargs = mock_download.call_args
    assert kwargs["period"] == "7d"


def test_custom_period_is_passed_through(mock_download: MagicMock) -> None:
    mock_download.return_value = _make_df([_ROW], [T1])
    fetch_graph("AAPL", CandleInterval.ONE_DAY, period="1y")
    _, kwargs = mock_download.call_args
    assert kwargs["period"] == "1y"


def test_correct_interval_value_passed_to_yfinance(mock_download: MagicMock) -> None:
    mock_download.return_value = _make_df([_ROW], [T1])
    fetch_graph("AAPL", CandleInterval.FIVE_MINUTES)
    _, kwargs = mock_download.call_args
    assert kwargs["interval"] == "5m"


def test_empty_dataframe_raises_value_error(mock_download: MagicMock) -> None:
    mock_download.return_value = pd.DataFrame()
    with pytest.raises(ValueError, match="No data returned for ticker='INVALID'"):
        fetch_graph("INVALID", CandleInterval.ONE_DAY)


def test_crypto_ticker_works(mock_download: MagicMock) -> None:
    mock_download.return_value = _make_df([_ROW], [T1])
    graph = fetch_graph("BTC-USD", CandleInterval.ONE_HOUR)
    assert graph.ticker == "BTC-USD"
    assert graph[0].ticker == "BTC-USD"
