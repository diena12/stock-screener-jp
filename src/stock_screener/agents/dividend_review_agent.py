from __future__ import annotations

from stock_screener.agents.risk_agent import RiskAgent
from stock_screener.agents.price_agent import PriceAgent
from stock_screener.data.edinetdb_client import EdinetDbClient
from stock_screener.models.financials import FinancialSeries
from stock_screener.models.screening_result import ScreeningResult
from stock_screener.scoring.dividend_score import calculate_dividend_score


class DividendReviewAgent:
    def __init__(
        self,
        rules: dict,
        risk_agent: RiskAgent,
        client: EdinetDbClient | None = None,
        price_agent: PriceAgent | None = None,
    ) -> None:
        self.rules = rules
        self.risk_agent = risk_agent
        self.client = client or EdinetDbClient()
        self.price_agent = price_agent or PriceAgent()

    def review(self, results: list[ScreeningResult], max_reviews: int, use_price: bool = True) -> list[ScreeningResult]:
        reviewed: list[ScreeningResult] = []
        for result in results[:max_reviews]:
            series = self._load_review_series(result)
            price_warnings = []
            if use_price:
                price_warnings = self.price_agent.enrich_company_series(result.company, series)
                if self._exceeds_lot_limit(result):
                    continue
            score, reasons = calculate_dividend_score(series, self.rules)
            risk_score, warnings = self.risk_agent.evaluate(series)
            warnings.extend(price_warnings)
            if len(series.snapshots) < 3:
                warnings.append("limited dividend history for review")
                score *= 0.85
            adjusted_score = max(0.0, score - (risk_score * 0.35))
            reviewed.append(
                ScreeningResult(
                    company=result.company,
                    latest=series.latest(),
                    score=adjusted_score,
                    risk_score=risk_score,
                    reasons=reasons,
                    warnings=warnings,
                )
            )
        return sorted(reviewed, key=lambda item: item.score, reverse=True)

    def _exceeds_lot_limit(self, result: ScreeningResult) -> bool:
        max_lot_price = self.rules.get("filters", {}).get("max_lot_price", 500000)
        lot_price = result.company.lot_price
        return lot_price is not None and lot_price > max_lot_price

    def _load_review_series(self, result: ScreeningResult) -> FinancialSeries:
        edinet_code = result.company.edinet_code
        if not edinet_code:
            return FinancialSeries(company_code=result.company.code, snapshots=[result.latest] if result.latest else [])
        series = self.client.load_financial_series(edinet_code, years=6)
        if series is None or not series.snapshots:
            return FinancialSeries(company_code=result.company.code, snapshots=[result.latest] if result.latest else [])
        self._merge_latest_metrics(series, result)
        return series

    def _merge_latest_metrics(self, series: FinancialSeries, result: ScreeningResult) -> None:
        source = result.latest
        target = series.latest()
        if source is None or target is None:
            return
        for field in (
            "dividend_yield",
            "payout_ratio",
            "equity_ratio",
            "roe",
            "per",
            "pbr",
        ):
            if getattr(target, field) is None:
                setattr(target, field, getattr(source, field))
