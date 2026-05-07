from __future__ import annotations

from stock_screener.agents.risk_agent import RiskAgent
from stock_screener.models.company import Company
from stock_screener.models.financials import FinancialSeries
from stock_screener.models.screening_result import ScreeningResult
from stock_screener.scoring.growth_score import calculate_growth_score


class GrowthAgent:
    def __init__(self, rules: dict, risk_agent: RiskAgent) -> None:
        self.rules = rules
        self.risk_agent = risk_agent

    def screen(self, universe: list[tuple[Company, FinancialSeries]], top: int) -> list[ScreeningResult]:
        results: list[ScreeningResult] = []
        for company, series in universe:
            latest = series.latest()
            if not self._passes_filters(company, latest, series):
                continue
            score, reasons = calculate_growth_score(series, self.rules)
            risk_score, warnings = self.risk_agent.evaluate(series)
            adjusted_score = max(0.0, score - (risk_score * 0.25))
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

    def _passes_filters(self, company: Company, latest, series: FinancialSeries) -> bool:
        filters = self.rules.get("filters", {})
        max_lot_price = filters.get("max_lot_price", 500000)
        if company.lot_price is not None and company.lot_price > max_lot_price:
            return False
        if latest is None:
            return False
        min_roe = filters.get("min_roe")
        if min_roe is not None and latest.roe is not None and latest.roe < min_roe:
            return False
        if len(series.snapshots) < 2:
            return False
        return True
