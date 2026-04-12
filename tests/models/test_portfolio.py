from datetime import datetime

import pytest

from pybeli.models.portfolio import Portfolio
from pybeli.models.signal import Signal
from pybeli.models.trade import Trade


def test_portfolio():
    portfolio = Portfolio(
        starting_balance=10000,
        trades=[
            Trade(
                ticker="AAPL",
                quantity=10,
                price=150,
                trade_type=Signal.BUY,
                timestamp=datetime.now(),
            ),
            Trade(
                ticker="AAPL",
                quantity=5,
                price=155,
                trade_type=Signal.SELL,
                timestamp=datetime.now(),
            ),
            Trade(
                ticker="GOOGL",
                quantity=8,
                price=2800,
                trade_type=Signal.BUY,
                timestamp=datetime.now(),
            ),
        ],
    )

    total_bought = (10 * 150) + (8 * 2800)
    total_sold = 5 * 155
    total_profit = total_sold - total_bought

    assert portfolio.total_bought == total_bought
    assert portfolio.total_sold == total_sold
    assert portfolio.total_profit == total_profit
    assert portfolio.total_trades == 3
    assert portfolio.available_funds == 10000 - total_bought + total_sold


def test_portfolio_validator():
    with pytest.raises(ValueError):
        Portfolio(
            starting_balance=10000,
            trades=[
                Trade(
                    ticker="AAPL",
                    quantity=5,
                    price=155,
                    trade_type=Signal.SELL,
                    timestamp=datetime.now(),
                ),
            ],
        )


def test_is_holding():
    portfolio = Portfolio(
        starting_balance=10000,
        trades=[
            Trade(
                ticker="AAPL",
                quantity=10,
                price=150,
                trade_type=Signal.BUY,
                timestamp=datetime.now(),
            ),
        ],
    )

    assert portfolio.is_holding("AAPL")
    assert not portfolio.is_holding("GOOGL")


def test_holding():
    portfolio = Portfolio(
        starting_balance=10000,
        trades=[
            Trade(
                ticker="AAPL",
                quantity=10,
                price=150,
                trade_type=Signal.BUY,
                timestamp=datetime.now(),
            ),
            Trade(
                ticker="AAPL",
                quantity=5,
                price=155,
                trade_type=Signal.SELL,
                timestamp=datetime.now(),
            ),
            Trade(
                ticker="GOOGL",
                quantity=8,
                price=2800,
                trade_type=Signal.BUY,
                timestamp=datetime.now(),
            ),
        ],
    )

    assert portfolio.holding("AAPL") == 5
    assert portfolio.holding("GOOGL") == 8
    assert portfolio.holding("MSFT") == 0


def test_add_trade():
    portfolio = Portfolio(
        starting_balance=10000,
        trades=[
            Trade(
                ticker="AAPL",
                quantity=10,
                price=150,
                trade_type=Signal.BUY,
                timestamp=datetime.now(),
            ),
        ],
    )

    portfolio.add_trade(
        Trade(
            ticker="GOOGL",
            quantity=8,
            price=2800,
            trade_type=Signal.BUY,
            timestamp=datetime.now(),
        )
    )

    assert portfolio.holding("AAPL") == 10
    assert portfolio.holding("GOOGL") == 8
    assert portfolio.holding("MSFT") == 0

    portfolio.add_trade(
        Trade(
            ticker="AAPL",
            quantity=5,
            price=155,
            trade_type=Signal.SELL,
            timestamp=datetime.now(),
        )
    )

    assert portfolio.holding("AAPL") == 5
    assert portfolio.holding("GOOGL") == 8
    assert portfolio.holding("MSFT") == 0


def test_add_trade_raises():
    portfolio = Portfolio(
        starting_balance=10000,
        trades=[
            Trade(
                ticker="AAPL",
                quantity=10,
                price=150,
                trade_type=Signal.BUY,
                timestamp=datetime.now(),
            ),
        ],
    )

    with pytest.raises(ValueError):
        portfolio.add_trade(
            Trade(
                ticker="AAPL",
                quantity=100,
                price=155,
                trade_type=Signal.SELL,
                timestamp=datetime.now(),
            )
        )
