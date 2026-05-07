from __future__ import annotations

from statistics import pstdev

from stock_screener.models.financials import FinancialSeries, FinancialSnapshot
from stock_screener.scoring.common import clamp, inverse_threshold_score, ratio_score


def calculate_dividend_score(series: FinancialSeries, rules: dict) -> tuple[float, list[str]]:
    latest = series.latest()
    if latest is None:
        return 0.0, ["financial data is missing"]

    weights = rules.get("weights", {})
    thresholds = rules.get("thresholds", {})
    score = 0.0
    reasons: list[str] = []

    yield_score = ratio_score(latest.dividend_yield, 0.05)
    score += yield_score * weights.get("dividend_yield", 15)
    if yield_score >= 0.6:
        reasons.append("dividend yield is above the target level")

    payout_score = inverse_threshold_score(
        latest.payout_ratio,
        thresholds.get("ideal_payout_ratio", 0.6),
        thresholds.get("risky_payout_ratio", 0.8),
    )
    score += payout_score * weights.get("payout_safety", 18)
    if payout_score >= 0.7:
        reasons.append("payout ratio is not excessive")

    equity_score = ratio_score(latest.equity_ratio, thresholds.get("ideal_equity_ratio", 0.45))
    roe_score = ratio_score(latest.roe, thresholds.get("ideal_roe", 0.08))
    financial_health = (equity_score + roe_score) / 2
    score += financial_health * weights.get("financial_health", 15)
    if financial_health >= 0.75:
        reasons.append("financial health is relatively strong")

    cf_score = _cashflow_score(latest)
    score += cf_score * weights.get("cashflow_quality", 12)
    if cf_score >= 0.75:
        reasons.append("operating cash flow and free cash flow are positive")

    profit_score = _profit_stability_score(series)
    score += profit_score * weights.get("profit_stability", 10)
    if profit_score >= 0.65:
        reasons.append("profit volatility is relatively low")

    continuity_score = _dividend_continuity_score(series)
    score += continuity_score * weights.get("dividend_continuity", 18)
    if continuity_score >= 0.8:
        reasons.append("dividend record is continuous")

    stability_score = _dividend_stability_score(series)
    score += stability_score * weights.get("dividend_stability", 7)
    if stability_score >= 0.7:
        reasons.append("dividend cuts are limited")

    price_score = _price_stability_score(series, thresholds)
    score += price_score * weights.get("price_stability", 5)
    if price_score >= 0.7:
        reasons.append("share price range is relatively stable")

    valuation_score = inverse_threshold_score(latest.per, 15, 35)
    score += valuation_score * weights.get("valuation_margin", 0)

    return min(score, 100.0), reasons


def _cashflow_score(latest: FinancialSnapshot) -> float:
    score = 0.0
    if latest.operating_cf is not None and latest.operating_cf > 0:
        score += 0.5
    if latest.free_cf is not None and latest.free_cf > 0:
        score += 0.5
    return score


def _profit_stability_score(series: FinancialSeries) -> float:
    profits = [
        item.net_income
        for item in series.snapshots
        if item.net_income is not None and item.net_income > 0
    ]
    if len(profits) >= 3:
        mean_profit = sum(profits) / len(profits)
        volatility = pstdev(profits) / mean_profit if mean_profit else 1
        return max(0.0, 1 - min(volatility, 1))
    if profits:
        return 0.4
    return 0.0


def _dividend_continuity_score(series: FinancialSeries) -> float:
    dividends = _ordered_dividends(series)
    if not dividends:
        return 0.0
    positive_years = sum(1 for value in dividends if value and value > 0)
    return positive_years / len(dividends)


def _dividend_stability_score(series: FinancialSeries) -> float:
    dividends = [value for value in _ordered_dividends(series) if value is not None]
    if not dividends:
        return 0.0
    cuts = 0
    for previous, current in zip(dividends, dividends[1:]):
        if previous > 0 and current < previous:
            cuts += 1
    cut_penalty = cuts / max(len(dividends) - 1, 1)

    positive = [value for value in dividends if value > 0]
    if len(positive) >= 3:
        mean_dividend = sum(positive) / len(positive)
        volatility = pstdev(positive) / mean_dividend if mean_dividend else 1
    else:
        volatility = 0.5
    return clamp(1 - (cut_penalty * 0.7) - (min(volatility, 1) * 0.3))


def _price_stability_score(series: FinancialSeries, thresholds: dict) -> float:
    range_ratios: list[float] = []
    for item in series.snapshots:
        high = item.highest_share_price
        low = item.lowest_share_price
        if high is None or low is None or high <= 0 or low <= 0 or high < low:
            continue
        midpoint = (high + low) / 2
        if midpoint > 0:
            range_ratios.append((high - low) / midpoint)
    if not range_ratios:
        return 0.0

    average_range_ratio = sum(range_ratios) / len(range_ratios)
    return inverse_threshold_score(
        average_range_ratio,
        thresholds.get("ideal_price_range_ratio", 0.25),
        thresholds.get("risky_price_range_ratio", 0.7),
    )


def _ordered_dividends(series: FinancialSeries) -> list[float | None]:
    snapshots = sorted(series.snapshots, key=lambda item: item.fiscal_year or 0)
    return [item.dividend_per_share for item in snapshots]
