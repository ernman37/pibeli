"""utils.py."""

from datetime import datetime

from pybeli.models.candle import Candle, CandleInterval
from pybeli.models.graph import Graph
from pybeli.models.stock import Stock

DEFAULT_TICKER = "TEST"
DEFAULT_INTERVAL = CandleInterval.ONE_MINUTE


def create_datetime(
    year: int = 2026,
    month: int = 1,
    day: int = 1,
    hour: int = 0,
    minute: int = 0,
    second: int = 0,
) -> datetime:
    """create_datetime.

    Creates a datetime object.

    Args:
        year (int): The year of the datetime.
        month (int): The month of the datetime.
        day (int): The day of the datetime.
        hour (int): The hour of the datetime.
        minute (int): The minute of the datetime.
        second (int): The second of the datetime.

    Returns:
        datetime: The created datetime object.
    """
    return datetime(year, month, day, hour, minute, second)


def create_candle(
    ticker: str = DEFAULT_TICKER,
    interval: CandleInterval = DEFAULT_INTERVAL,
    timestamp: datetime = datetime(2026, 1, 1, 0, 0),
    open: float = 0.5,
    high: float = 1.0,
    low: float = 0.1,
    close: float = 0.75,
    volume: int = 100,
) -> Candle:
    """create_candle.

    Creates a Candle object with the given parameters.

    Args:
        ticker (str): The ticker symbol for the asset.
        interval (CandleInterval): The time interval for the candle.
        timestamp (int): The timestamp for the candle.
        open (float): The opening price.
        high (float): The highest price.
        low (float): The lowest price.
        close (float): The closing price.
        volume (float): The trading volume.

    Returns:
        Candle: The created Candle object.
    """
    return Candle(
        ticker=ticker,
        interval=interval,
        timestamp=timestamp,
        open=open,
        high=high,
        low=low,
        close=close,
        volume=volume,
    )


def create_graph(
    ticker: str = DEFAULT_TICKER,
    interval: CandleInterval = DEFAULT_INTERVAL,
    candles: list[Candle] = None,
) -> Graph:
    """create_graph.

    Creates a Graph object with the given parameters.

    Args:
        ticker (str): The ticker symbol for the asset.
        interval (CandleInterval): The time interval for the graph.
        candles (list[Candle]): The list of candles for the graph.

    Returns:
        Graph: The created Graph object.
    """
    if candles is None:
        candles = list[Candle]()
    return Graph(
        ticker=ticker,
        interval=interval,
        candles=candles,
    )


def create_stock(
    ticker: str = DEFAULT_TICKER, graphs: dict[CandleInterval, Graph] = None
) -> Stock:
    """create_stock.

    Creates a stock with specified ticker and graphs

    Args:
        ticker (str): The ticker symbol for the stock.
        graphs (dict[CandleInterval, Graph]): The graphs for the stock.

    Returns:
        Stock: The created Stock object.
    """
    if graphs is None:
        graphs = dict[CandleInterval, Graph]()
    return Stock(
        ticker=ticker,
        graphs=graphs,
    )
