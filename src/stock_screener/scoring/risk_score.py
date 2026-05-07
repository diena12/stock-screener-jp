from __future__ import annotations

from stock_screener.models.financials import FinancialSnapshot


def calculate_risk_score(latest: FinancialSnapshot | None, rules: dict) -> tuple[float, list[str]]:
    if latest is None:
        return 100.0, ["財務データが取得できませんでした"]

    penalties = rules.get("risk_penalties", {})
    thresholds = rules.get("thresholds", {})
    score = 0.0
    warnings: list[str] = []

    if latest.net_income is not None and latest.net_income < 0:
        score += penalties.get("negative_net_income", 25)
        warnings.append("直近純利益が赤字")

    if latest.operating_cf is not None and latest.operating_cf < 0:
        score += penalties.get("negative_operating_cf", 20)
        warnings.append("営業CFがマイナス")

    high_payout = thresholds.get("high_payout_ratio", 0.9)
    if latest.payout_ratio is not None and latest.payout_ratio > high_payout:
        score += penalties.get("high_payout_ratio", 15)
        warnings.append("配当性向が高い")

    low_equity = thresholds.get("low_equity_ratio", 0.25)
    if latest.equity_ratio is not None and latest.equity_ratio < low_equity:
        score += penalties.get("low_equity_ratio", 15)
        warnings.append("自己資本比率が低い")

    missing = [
        latest.roe,
        latest.equity_ratio,
        latest.operating_cf,
        latest.free_cf,
    ].count(None)
    if missing:
        score += penalties.get("missing_key_data", 10) * min(missing / 4, 1)
        warnings.append("重要指標に欠損あり")

    return min(score, 100.0), warnings
