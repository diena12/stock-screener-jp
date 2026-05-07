from __future__ import annotations

from stock_screener.models.financials import FinancialSeries


class QualityAgent:
    def evaluate_notes(self, series: FinancialSeries) -> list[str]:
        latest = series.latest()
        if latest is None:
            return ["財務品質を評価できません"]

        notes: list[str] = []
        if latest.roe is not None and latest.roe >= 0.1:
            notes.append("資本効率が一定水準以上")
        if latest.equity_ratio is not None and latest.equity_ratio >= 0.4:
            notes.append("自己資本比率が厚い")
        if latest.operating_cf is not None and latest.operating_cf > 0:
            notes.append("営業CFがプラス")
        if latest.free_cf is not None and latest.free_cf > 0:
            notes.append("FCFがプラス")
        return notes
