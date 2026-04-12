"""config.py"""

from pathlib import Path

from pydantic import BaseModel, Field
from yaml import safe_load

from pybeli.models.candle import CandleInterval
from pybeli.models.period import Period


class Config(BaseModel):
    """
    Configuration settings for the application.
    """

    tickers: list[str] = Field(..., description="The stock tickers to fetch data for")
    intervals: list[CandleInterval] = Field(
        ..., description="The time intervals for the application"
    )
    period: Period = Field(..., description="The period for the RSI calculation")
    indicators: list[dict[str, str | int | float]] = Field(
        ..., description="The technical indicators to use"
    )

    @staticmethod
    def from_file(path: Path) -> "Config":
        with path.open("r") as f:
            config_data = safe_load(f) or {}
        return Config.model_validate(config_data)
