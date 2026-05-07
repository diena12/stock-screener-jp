from __future__ import annotations

from pydantic import BaseModel


class FinancialSnapshot(BaseModel):
    fiscal_year: int | None = None
    revenue: float | None = None
    operating_income: float | None = None
    net_income: float | None = None
    eps: float | None = None
    roe: float | None = None
    equity_ratio: float | None = None
    operating_cf: float | None = None
    free_cf: float | None = None
    dividend_per_share: float | None = None
    dividend_yield: float | None = None
    payout_ratio: float | None = None
    per: float | None = None
    pbr: float | None = None
    highest_share_price: float | None = None
    lowest_share_price: float | None = None


class FinancialSeries(BaseModel):
    company_code: str
    snapshots: list[FinancialSnapshot]

    def latest(self) -> FinancialSnapshot | None:
        if not self.snapshots:
            return None
        return sorted(
            self.snapshots,
            key=lambda item: item.fiscal_year or 0,
            reverse=True,
        )[0]
