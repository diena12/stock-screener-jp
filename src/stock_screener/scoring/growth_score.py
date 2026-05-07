from __future__ import annotations

from stock_screener.models.financials import FinancialSeries
from stock_screener.scoring.common import inverse_threshold_score, ratio_score


def _cagr(first: float | None, last: float | None, years: int) -> float | None:
    if first is None or last is None or first <= 0 or last <= 0 or years <= 0:
        return None
    return (last / first) ** (1 / years) - 1


def calculate_growth_score(series: FinancialSeries, rules: dict) -> tuple[float, list[str]]:
    latest = series.latest()
    ordered = sorted(series.snapshots, key=lambda item: item.fiscal_year or 0)
    if latest is None or len(ordered) < 2:
        return 0.0, ["成長評価に必要な時系列データ不足"]

    first = ordered[0]
    years = max(len(ordered) - 1, 1)
    thresholds = rules.get("thresholds", {})
    weights = rules.get("weights", {})
    score = 0.0
    reasons: list[str] = []

    revenue_cagr = _cagr(first.revenue, latest.revenue, years)
    revenue_score = ratio_score(revenue_cagr, thresholds.get("ideal_revenue_cagr", 0.12))
    score += revenue_score * weights.get("revenue_growth", 25)
    if revenue_score >= 0.6:
        reasons.append("売上成長率が良好")

    profit_cagr = _cagr(first.operating_income, latest.operating_income, years)
    profit_score = ratio_score(profit_cagr, thresholds.get("ideal_profit_cagr", 0.15))
    score += profit_score * weights.get("profit_growth", 25)
    if profit_score >= 0.6:
        reasons.append("営業利益成長率が良好")

    roe_score = ratio_score(latest.roe, thresholds.get("ideal_roe", 0.15))
    score += roe_score * weights.get("capital_efficiency", 20)
    if roe_score >= 0.7:
        reasons.append("ROEが高い")

    margin_score = 0.0
    if first.revenue and latest.revenue and first.operating_income is not None and latest.operating_income is not None:
        first_margin = first.operating_income / first.revenue
        latest_margin = latest.operating_income / latest.revenue
        if latest_margin > first_margin:
            margin_score = 1.0
            reasons.append("営業利益率が改善")
    score += margin_score * weights.get("margin_trend", 10)

    cf_score = 0.0
    if latest.operating_cf is not None and latest.operating_cf > 0:
        cf_score += 0.5
    if latest.free_cf is not None and latest.free_cf > 0:
        cf_score += 0.5
    score += cf_score * weights.get("cashflow_quality", 10)

    valuation_score = inverse_threshold_score(
        latest.per,
        thresholds.get("expensive_per", 45) / 2,
        thresholds.get("expensive_per", 45),
    )
    score += valuation_score * weights.get("valuation_discipline", 10)

    return min(score, 100.0), reasons
