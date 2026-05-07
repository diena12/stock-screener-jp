from __future__ import annotations

from stock_screener.data.edinetdb_client import EdinetDbClient
from stock_screener.models.company import Company
from stock_screener.models.financials import FinancialSeries


class DataAgent:
    def __init__(self, client: EdinetDbClient | None = None) -> None:
        self.client = client or EdinetDbClient()

    def load_universe(self, use_sample: bool = False) -> list[tuple[Company, FinancialSeries]]:
        return self.client.load_universe(use_sample=use_sample)

    def load_dividend_universe(
        self,
        limit: int = 500,
        use_sample: bool = False,
    ) -> list[tuple[Company, FinancialSeries]]:
        return self.client.load_dividend_universe(limit=limit, use_sample=use_sample)
