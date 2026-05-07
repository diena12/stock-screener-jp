from __future__ import annotations

from pydantic import BaseModel

from stock_screener.models.company import Company
from stock_screener.models.financials import FinancialSnapshot


class ScreeningResult(BaseModel):
    company: Company
    latest: FinancialSnapshot | None
    score: float
    risk_score: float
    reasons: list[str]
    warnings: list[str]

    def to_row(self) -> dict[str, object]:
        latest = self.latest or FinancialSnapshot()
        return {
            "code": self.company.display_code(),
            "name": self.company.name,
            "market": self.company.market,
            "sector": self.company.sector,
            "price": self.company.price,
            "lot_price": self.company.lot_price,
            "score": round(self.score, 2),
            "risk_score": round(self.risk_score, 2),
            "dividend_yield": latest.dividend_yield,
            "payout_ratio": latest.payout_ratio,
            "roe": latest.roe,
            "equity_ratio": latest.equity_ratio,
            "per": latest.per,
            "operating_cf": latest.operating_cf,
            "free_cf": latest.free_cf,
            "reasons": " / ".join(self.reasons),
            "warnings": " / ".join(self.warnings),
        }
