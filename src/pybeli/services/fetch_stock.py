"""fetch_stock.py"""

from datetime import datetime

from yfinance import download

from pybeli.models.candle import Candle, CandleInterval
from pybeli.models.graph import Graph
from pybeli.models.period import Period
from pybeli.models.stock import Stock


def fetch_stocks(
    tickers: list[str], intervals: list[CandleInterval], period: Period
) -> list[Stock]:
    """
    Fetch multiple stocks.

    Args:
        tickers: A list of stock tickers to fetch.
        intervals: A list of candle intervals to fetch.
        period: The period to fetch the stocks for.

    Returns:
        A list of Stock objects.

    Raises:
        ValueError: If any of the tickers are invalid or
            if the intervals or period are not supported.
    """
    stocks: list[Stock] = []
    for stock in tickers:
        stocks.append(fetch_stock(stock, intervals, period))
    return stocks


def fetch_stock(ticker: str, intervals: list[CandleInterval], period: Period) -> Stock:
    """
    Fetch a single stock.

    Args:
        ticker: The stock ticker to fetch.
        intervals: A list of candle intervals to fetch.
        period: The period to fetch the stock for.

    Returns:
        A Stock object.
    """
    graphs: dict[CandleInterval, Graph] = {}
    for interval in intervals:
        graphs[interval] = fetch_graph(ticker, interval, period)
    return Stock(ticker=ticker, graphs=graphs)


def fetch_graph(ticker: str, interval: CandleInterval, period: Period) -> Graph:
    """
    Fetch a single graph for a stock.

    Args:
        ticker: The stock ticker to fetch.
        interval: The candle interval to fetch.
        period: The period to fetch the graph for.

    Returns:
        A Graph object.
    """
    candles: list[Candle] = fetch_candles(ticker, interval, period)
    return Graph(ticker=ticker, interval=interval, candles=candles)


def fetch_candles(
    ticker: str, interval: CandleInterval, period: Period
) -> list[Candle]:
    """
    Fetch candles for a stock.

    Args:
        ticker: The stock ticker to fetch.
        interval: The candle interval to fetch.
        period: The period to fetch the candles for.

    Returns:
        A list of Candle objects.
    """
    data = download(ticker, period=period.value, interval=interval.value)
    candles: list[Candle] = []
    for index, row in data.iterrows():
        timestamp = datetime.fromisoformat(str(index))
        open = row["Open"].item()
        high = row["High"].item()
        low = row["Low"].item()
        close = row["Close"].item()
        volume = row["Volume"].item()
        candles.append(
            Candle(
                ticker=ticker,
                open=open,
                high=high,
                low=low,
                close=close,
                volume=volume,
                interval=interval,
                timestamp=timestamp,
            )
        )
    return candles
