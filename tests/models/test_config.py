from pathlib import Path

from pybeli.models.candle import CandleInterval
from pybeli.models.config import Config
from pybeli.models.period import Period

test_config_file = Path(__file__).parent.parent / "files/config.yaml"


def test_from_file():
    config = Config.from_file(test_config_file)
    assert config.tickers == ["AAPL", "MSFT", "BTC-USD"]
    assert config.intervals == [
        CandleInterval.ONE_MINUTE,
        CandleInterval.FIVE_MINUTES,
        CandleInterval.FIFTEEN_MINUTES,
    ]
    assert config.period == Period.ONE_MONTH
    assert config.indicators == [{"name": "RSI", "period": 14}]
