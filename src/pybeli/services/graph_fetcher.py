"""graph_fetcher.py"""

import yfinance as yf

from pybeli.models.candle import Candle, CandleInterval
from pybeli.models.graph import Graph

# Maps our CandleInterval enum values to the yfinance period lookback defaults.
# These can be overridden by the caller via the `period` argument.
_DEFAULT_PERIOD: dict[CandleInterval, str] = {
    CandleInterval.ONE_MINUTE: "7d",
    CandleInterval.FIVE_MINUTES: "60d",
    CandleInterval.FIFTEEN_MINUTES: "60d",
    CandleInterval.ONE_HOUR: "730d",
    CandleInterval.ONE_DAY: "max",
}


def fetch_graph(
    ticker: str,
    interval: CandleInterval,
    period: str | None = None,
) -> Graph:
    """
    Fetch OHLCV candles for a ticker and return a Graph.

    Args:
        ticker:   The ticker symbol (e.g. "AAPL", "BTC-USD").
        interval: The candle interval.
        period:   yfinance period string (e.g. "7d", "60d", "1y", "max").
                  Defaults to a sensible value per interval if not provided.

    Returns:
        A Graph populated with sorted, validated Candle objects.

    Raises:
        ValueError: If no data is returned for the given ticker/interval.
    """
    resolved_period = period or _DEFAULT_PERIOD[interval]

    df = yf.download(
        tickers=ticker,
        interval=interval.value,
        period=resolved_period,
        auto_adjust=True,
        progress=False,
        multi_level_column=False,
    )

    if df.empty:
        raise ValueError(
            f"No data returned for ticker='{ticker}' interval='{interval}' "
            f"period='{resolved_period}'"
        )

    candles = [
        Candle(
            ticker=ticker,
            interval=interval,
            timestamp=row.Index.to_pydatetime(),
            open=float(row.Open),
            high=float(row.High),
            low=float(row.Low),
            close=float(row.Close),
            volume=float(row.Volume),
        )
        for row in df.itertuples()
    ]

    return Graph(ticker=ticker, interval=interval, candles=candles)
