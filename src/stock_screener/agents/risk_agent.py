from __future__ import annotations

from stock_screener.models.financials import FinancialSeries
from stock_screener.scoring.risk_score import calculate_risk_score


class RiskAgent:
    def __init__(self, rules: dict) -> None:
        self.rules = rules

    def evaluate(self, series: FinancialSeries) -> tuple[float, list[str]]:
        return calculate_risk_score(series.latest(), self.rules)
