from __future__ import annotations

from statistics import pstdev

from stock_screener.models.financials import FinancialSeries
from stock_screener.scoring.common import inverse_threshold_score, ratio_score


def calculate_dividend_score(series: FinancialSeries, rules: dict) -> tuple[float, list[str]]:
    latest = series.latest()
    if latest is None:
        return 0.0, ["財務データなし"]

    weights = rules.get("weights", {})
    thresholds = rules.get("thresholds", {})
    score = 0.0
    reasons: list[str] = []

    dividend_yield_score = ratio_score(latest.dividend_yield, 0.05)
    score += dividend_yield_score * weights.get("dividend_yield", 25)
    if dividend_yield_score >= 0.6:
        reasons.append("配当利回りが一定水準以上")

    payout_score = inverse_threshold_score(
        latest.payout_ratio,
        thresholds.get("ideal_payout_ratio", 0.6),
        thresholds.get("risky_payout_ratio", 0.8),
    )
    score += payout_score * weights.get("payout_safety", 20)
    if payout_score >= 0.7:
        reasons.append("配当性向に過度な無理がない")

    equity_score = ratio_score(latest.equity_ratio, thresholds.get("ideal_equity_ratio", 0.45))
    roe_score = ratio_score(latest.roe, thresholds.get("ideal_roe", 0.08))
    score += ((equity_score + roe_score) / 2) * weights.get("financial_health", 20)
    if equity_score >= 0.8:
        reasons.append("自己資本比率が比較的高い")

    cf_score = 0.0
    if latest.operating_cf is not None and latest.operating_cf > 0:
        cf_score += 0.5
    if latest.free_cf is not None and latest.free_cf > 0:
        cf_score += 0.5
    score += cf_score * weights.get("cashflow_quality", 15)
    if cf_score >= 0.5:
        reasons.append("キャッシュフローがプラス")

    profits = [
        item.net_income
        for item in series.snapshots
        if item.net_income is not None and item.net_income > 0
    ]
    stability = 0.0
    if len(profits) >= 3:
        mean_profit = sum(profits) / len(profits)
        volatility = pstdev(profits) / mean_profit if mean_profit else 1
        stability = max(0.0, 1 - min(volatility, 1))
    elif profits:
        stability = 0.4
    score += stability * weights.get("profit_stability", 10)
    if stability >= 0.6:
        reasons.append("利益の振れが比較的小さい")

    per_score = inverse_threshold_score(latest.per, 15, 35)
    score += per_score * weights.get("valuation_margin", 10)

    return min(score, 100.0), reasons
