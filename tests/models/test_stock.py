"""test_stock.py."""

import pytest
from utils import DEFAULT_TICKER, create_candle, create_graph, create_stock

from pybeli.models.candle import CandleInterval


def test_stock_creation() -> None:
    stock = create_stock()
    assert stock.ticker == DEFAULT_TICKER
    assert stock.graphs == {}


def test_stock_with_graphs_creation() -> None:
    stock = create_stock()
    stock.add_graph(CandleInterval.ONE_MINUTE, create_graph())
    assert len(stock.graphs) == 1


def test_stock_get_graph() -> None:
    stock = create_stock()
    candles = [create_candle()]
    stock.add_graph(CandleInterval.ONE_MINUTE, create_graph(candles=candles))
    graph = stock.get_graph(CandleInterval.ONE_MINUTE)
    assert graph is not None
    assert graph.candles == candles
    assert stock.get_graph(CandleInterval.FIVE_MINUTES) is None


def test_stock_add_graph() -> None:
    stock = create_stock()
    stock.add_graph(CandleInterval.ONE_MINUTE, create_graph(candles=[create_candle()]))
    assert len(stock.graphs) == 1
    assert stock.get_graph(CandleInterval.ONE_MINUTE) is not None


def test_stock_add_graph_mismatch_ticker() -> None:
    stock = create_stock()
    candles = [create_candle(ticker="BAD")]
    with pytest.raises(ValueError):
        stock.add_graph(
            CandleInterval.ONE_MINUTE,
            create_graph(ticker="BAD", candles=candles),
        )


def test_stock_add_graph_mismatch_interval() -> None:
    stock = create_stock()
    candles = [create_candle()]
    with pytest.raises(ValueError):
        stock.add_graph(
            CandleInterval.FIVE_MINUTES,
            create_graph(candles=candles),  # graph interval is ONE_MINUTE
        )


def test_stock_remove_graph() -> None:
    stock = create_stock()
    stock.add_graph(CandleInterval.ONE_MINUTE, create_graph(candles=[create_candle()]))
    stock.remove_graph(CandleInterval.ONE_MINUTE)
    assert stock.get_graph(CandleInterval.ONE_MINUTE) is None


def test_stock_remove_graph_not_present_does_not_raise() -> None:
    stock = create_stock()
    stock.remove_graph(CandleInterval.ONE_MINUTE)  # should silently do nothing


def test_stock_add_candle_to_existing_graph() -> None:
    stock = create_stock()
    stock.add_graph(CandleInterval.ONE_MINUTE, create_graph(candles=[create_candle()]))
    new_candle = create_candle(timestamp=create_candle().timestamp.replace(minute=1))
    stock.add_candle_to_graph(CandleInterval.ONE_MINUTE, new_candle)
    graph = stock.get_graph(CandleInterval.ONE_MINUTE)
    assert graph is not None
    assert len(graph) == 2


def test_stock_add_candle_creates_graph_if_missing() -> None:
    stock = create_stock()
    candle = create_candle()
    stock.add_candle_to_graph(CandleInterval.ONE_MINUTE, candle)
    graph = stock.get_graph(CandleInterval.ONE_MINUTE)
    assert graph is not None
    assert len(graph) == 1


def test_stock_remove_candle_from_graph() -> None:
    stock = create_stock()
    candle = create_candle()
    stock.add_graph(CandleInterval.ONE_MINUTE, create_graph(candles=[candle]))
    stock.remove_candle_from_graph(CandleInterval.ONE_MINUTE, candle)
    graph = stock.get_graph(CandleInterval.ONE_MINUTE)
    assert graph is not None
    assert len(graph) == 0


def test_stock_remove_candle_from_missing_graph_does_not_raise() -> None:
    stock = create_stock()
    stock.remove_candle_from_graph(CandleInterval.ONE_MINUTE, create_candle())


def test_stock_trim_graphs() -> None:
    from datetime import timedelta

    stock = create_stock()
    base = create_candle()
    candles = [
        create_candle(timestamp=base.timestamp + timedelta(minutes=i)) for i in range(5)
    ]
    stock.add_graph(CandleInterval.ONE_MINUTE, create_graph(candles=candles))
    stock.trim_graphs(3)
    graph = stock.get_graph(CandleInterval.ONE_MINUTE)
    assert graph is not None
    assert len(graph) == 3


def test_stock_trim_graph_specific_interval() -> None:
    from datetime import timedelta

    stock = create_stock()
    base = create_candle()
    candles = [
        create_candle(timestamp=base.timestamp + timedelta(minutes=i)) for i in range(4)
    ]
    stock.add_graph(CandleInterval.ONE_MINUTE, create_graph(candles=candles))
    stock.trim_graph(CandleInterval.ONE_MINUTE, 2)
    graph = stock.get_graph(CandleInterval.ONE_MINUTE)
    assert graph is not None
    assert len(graph) == 2


def test_stock_trim_graph_missing_interval_does_not_raise() -> None:
    stock = create_stock()
    stock.trim_graph(CandleInterval.ONE_MINUTE, 5)


def test_stock_construction_raises_on_mismatched_graph_ticker() -> None:
    graph = create_graph(ticker="BAD", candles=[create_candle(ticker="BAD")])
    with pytest.raises(ValueError, match="does not match stock ticker"):
        create_stock(graphs={CandleInterval.ONE_MINUTE: graph})


def test_stock_construction_raises_on_mismatched_graph_interval() -> None:
    graph = create_graph(candles=[create_candle()])
    with pytest.raises(ValueError, match="does not match expected interval"):
        create_stock(
            graphs={CandleInterval.FIVE_MINUTES: graph}
        )  # key says FIVE_MINUTES
