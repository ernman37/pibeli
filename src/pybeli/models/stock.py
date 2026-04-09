"""stock.py"""

from pydantic import BaseModel, Field, model_validator

from pybeli.models.candle import Candle, CandleInterval
from pybeli.models.graph import Graph


class Stock(BaseModel):
    """Stock.

    Represents a stock with its associated candle graphs.

    Attributes:
        ticker (str): The ticker symbol of the stock.
        graphs (dict[CandleInterval, Graph]): A mapping of candle intervals to
            their corresponding graph data.
    """

    ticker: str = Field(..., description="The ticker symbol of the stock")
    graphs: dict[CandleInterval, Graph] = Field(
        default_factory=dict,
        description="A mapping of candle intervals to their corresponding graph data",
    )

    @model_validator(mode="after")
    def validate_graphs(self) -> "Stock":
        """validate_graphs.

        Validates the graphs in the stock.

        Returns:
            Stock: The validated stock.

        Raises:
            ValueError: If any graph does not match the stock's ticker or interval.
        """
        for interval, graph in self.graphs.items():
            if graph.ticker != self.ticker:
                raise ValueError(
                    f"Graph ticker '{graph.ticker}' "
                    f"does not match stock ticker '{self.ticker}'"
                )
            if graph.interval != interval:
                raise ValueError(
                    f"Graph interval '{graph.interval}' "
                    f"does not match expected interval '{interval}'"
                )
        return self

    def get_graph(self, interval: CandleInterval) -> Graph | None:
        """get_graph.

        Retrieves the graph for a specific candle interval.

        Args:
            interval (CandleInterval): The candle interval for
                which to retrieve the graph.

        Returns:
            Graph | None: The graph for the specified candle interval,
                or None if not found.
        """
        return self.graphs.get(interval)

    def add_graph(self, interval: CandleInterval, graph: Graph) -> None:
        """add_graph.

        Adds graph to the stock.

        Args:
            interval (CandleInterval): The candle interval for the graph.
            graph (Graph): The graph to add.
        """
        if graph.ticker != self.ticker:
            raise ValueError(
                f"Graph ticker '{graph.ticker}' "
                f"does not match stock ticker '{self.ticker}'"
            )
        if interval != graph.interval:
            raise ValueError(
                f"Graph interval '{graph.interval}' "
                f"does not match expected interval '{interval}'"
            )
        self.graphs[interval] = graph

    def remove_graph(self, interval: CandleInterval) -> None:
        """remove_graph.

        Removes the graph for a specific candle interval.

        Args:
            interval (CandleInterval): The candle interval for
                which to remove the graph.
        """
        self.graphs.pop(interval, None)

    def add_candle_to_graph(self, interval: CandleInterval, candle: Candle) -> None:
        """add_candle_to_graph.

        Adds a candle to the graph for a specific candle interval.

        Args:
            interval (CandleInterval): The candle interval for which to add the candle.
            candle (Candle): The candle to add.
        """
        graph = self.get_graph(interval)
        if graph is None:
            graph = Graph(ticker=self.ticker, interval=interval, candles=[])
            self.add_graph(interval, graph)
        graph.add_candle(candle)

    def remove_candle_from_graph(
        self, interval: CandleInterval, candle: Candle
    ) -> None:
        """remove_candle_from_graph.

        Removes a candle from the graph for a specific candle interval.

        Args:
            interval (CandleInterval): The candle interval for
                which to remove the candle.
            candle (Candle): The candle to remove.
        """
        graph = self.get_graph(interval)
        if graph:
            graph.remove_candle(candle)

    def trim_graphs(self, count: int) -> None:
        """trim_graphs.

        Trims the candles in all graphs to the specified count.

        Args:
            count (int): The number of candles to keep.
        """
        for graph in self.graphs.values():
            graph.trim(count)

    def trim_graph(self, interval: CandleInterval, count: int) -> None:
        """trim_graph.

        Trims the candles in the graph for a specific candle
            interval to the specified count.

        Args:
            interval (CandleInterval): The candle interval for which to trim the graph.
            count (int): The number of candles to keep.
        """
        graph = self.get_graph(interval)
        if graph:
            graph.trim(count)
