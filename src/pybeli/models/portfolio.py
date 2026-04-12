from pydantic import BaseModel, Field, model_validator

from pybeli.models.signal import Signal
from pybeli.models.trade import Trade


class Portfolio(BaseModel):
    """
    Represents a user's portfolio of trades and balance.

    Attributes:
        starting_balance (float): The initial balance of the portfolio.
        trades (list[Trade]): The list of trades in the portfolio.
    """

    starting_balance: float = Field(
        ..., description="The initial balance of the portfolio"
    )
    trades: list[Trade] = Field(..., description="The list of trades in the portfolio")
    holdings: dict[str, float] = Field(
        default_factory=dict, description="The current holdings in the portfolio"
    )

    @model_validator(mode="after")
    def validate_trades(self) -> "Portfolio":
        """
        Validates the trades in the portfolio to ensure that the holdings are
            consistent with the trades.

        Returns:
            Portfolio: The validated portfolio.
        """
        holdings: dict[str, float] = {}
        for trade in self.trades:
            if trade.trade_type == Signal.BUY:
                holdings[trade.ticker] = holdings.get(trade.ticker, 0) + trade.quantity
            elif trade.trade_type == Signal.SELL:
                holdings[trade.ticker] = holdings.get(trade.ticker, 0) - trade.quantity
                if holdings[trade.ticker] < 0:
                    raise ValueError(
                        f"Cannot sell more {trade.ticker} than currently held"
                    )
        self.holdings = holdings
        return self

    def is_holding(self, ticker: str) -> bool:
        """
        Checks if the portfolio is currently holding a specific stock.

        Args:
            ticker (str): The stock ticker symbol to check.

        Returns:
            bool: True if the portfolio is holding the stock, False otherwise.
        """
        return self.holdings.get(ticker, 0) > 0

    def holding(self, ticker: str) -> float:
        """
        Returns the quantity of a specific stock currently held in the portfolio.

        Args:
            ticker (str): The stock ticker symbol to check.

        Returns:
            float: The quantity of the stock currently held in the portfolio.
        """
        return self.holdings.get(ticker, 0)

    def add_trade(self, trade: Trade) -> None:
        """
        Adds a trade to the portfolio and updates the holdings accordingly.

        Args:
            trade (Trade): The trade to add to the portfolio.
        """
        self.trades.append(trade)
        holdings = self.holdings.get(trade.ticker, 0)
        if trade.trade_type == Signal.BUY:
            holdings += trade.quantity
        elif trade.trade_type == Signal.SELL:
            holdings -= trade.quantity
        if holdings < 0:
            raise ValueError(f"Cannot sell more {trade.ticker} than currently held")
        self.holdings[trade.ticker] = holdings

    @property
    def total_bought(self) -> float:
        """
        Calculates the total amount bought in the portfolio.

        Returns:
            float: The total amount bought in the portfolio.
        """
        return sum(
            trade.amount for trade in self.trades if trade.trade_type == Signal.BUY
        )

    @property
    def total_sold(self) -> float:
        """
        Calculates the total amount sold in the portfolio.

        Returns:
            float: The total amount sold in the portfolio.
        """
        return sum(
            trade.amount for trade in self.trades if trade.trade_type == Signal.SELL
        )

    @property
    def total_profit(self) -> float:
        """
        Calculates the total profit from the trades in the portfolio.

        Returns:
            float: The total profit from the trades in the portfolio.
        """
        return self.total_sold - self.total_bought

    @property
    def total_trades(self) -> int:
        """
        Calculates the total number of trades in the portfolio.

        Returns:
            int: The total number of trades in the portfolio.
        """
        return len(self.trades)

    @property
    def available_funds(self) -> float:
        """
        Calculates the available funds in the portfolio (cash on hand).

        This is the starting balance minus all buys plus all sells.

        Returns:
            float: The available funds in the portfolio.
        """
        return self.starting_balance - self.total_bought + self.total_sold
