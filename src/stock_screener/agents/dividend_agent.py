from __future__ import annotations

from stock_screener.agents.risk_agent import RiskAgent
from stock_screener.models.company import Company
from stock_screener.models.financials import FinancialSeries
from stock_screener.models.screening_result import ScreeningResult
from stock_screener.scoring.dividend_score import calculate_dividend_score


class DividendAgent:
    def __init__(self, rules: dict, risk_agent: RiskAgent) -> None:
        self.rules = rules
        self.risk_agent = risk_agent

    def screen(self, universe: list[tuple[Company, FinancialSeries]], top: int) -> list[ScreeningResult]:
        results: list[ScreeningResult] = []
        filters = self.rules.get("filters", {})
        for company, series in universe:
            latest = series.latest()
            if not self._passes_filters(company, latest):
                continue
            score, reasons = calculate_dividend_score(series, self.rules)
            risk_score, warnings = self.risk_agent.evaluate(series)
            adjusted_score = max(0.0, score - (risk_score * 0.35))
            results.append(
                ScreeningResult(
                    company=company,
                    latest=latest,
                    score=adjusted_score,
                    risk_score=risk_score,
                    reasons=reasons,
                    warnings=warnings,
                )
            )
        return sorted(results, key=lambda item: item.score, reverse=True)[:top]

    def _passes_filters(self, company: Company, latest) -> bool:
        filters = self.rules.get("filters", {})
        max_lot_price = filters.get("max_lot_price", 500000)
        if company.lot_price is not None and company.lot_price > max_lot_price:
            return False
        if latest is None:
            return False
        min_yield = filters.get("min_dividend_yield")
        if min_yield is not None and (latest.dividend_yield is None or latest.dividend_yield < min_yield):
            return False
        min_equity = filters.get("min_equity_ratio")
        if min_equity is not None and latest.equity_ratio is not None and latest.equity_ratio < min_equity:
            return False
        if filters.get("require_positive_operating_cf") and latest.operating_cf is not None and latest.operating_cf <= 0:
            return False
        return True
