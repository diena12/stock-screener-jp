from __future__ import annotations

from datetime import date
from pathlib import Path

from stock_screener.models.screening_result import ScreeningResult


def write_markdown(
    dividend_results: list[ScreeningResult],
    growth_results: list[ScreeningResult],
    path: Path,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        f"# 日本株スクリーニングレポート {date.today().isoformat()}",
        "",
        "このレポートは投資助言ではありません。調査候補を整理するための参考情報です。",
        "",
        "## 高配当・安定株候補",
        "",
    ]
    lines.extend(_table(dividend_results))
    lines.extend(["", "## 値上がり期待株候補", ""])
    lines.extend(_table(growth_results))
    path.write_text("\n".join(lines), encoding="utf-8")


def _table(results: list[ScreeningResult]) -> list[str]:
    if not results:
        return ["該当候補はありません。"]
    lines = [
        "|順位|コード|銘柄|株価|100株金額|スコア|リスク|理由|注意点|",
        "|---:|---|---|---:|---:|---:|---:|---|---|",
    ]
    for index, result in enumerate(results, start=1):
        row = result.to_row()
        lines.append(
            "|{rank}|{code}|{name}|{price}|{lot_price}|{score}|{risk_score}|{reasons}|{warnings}|".format(
                rank=index,
                code=row["code"],
                name=row["name"],
                price=_fmt(row["price"]),
                lot_price=_fmt(row["lot_price"]),
                score=row["score"],
                risk_score=row["risk_score"],
                reasons=row["reasons"],
                warnings=row["warnings"],
            )
        )
    return lines


def _fmt(value: object) -> str:
    if value is None:
        return "-"
    if isinstance(value, float):
        return f"{value:,.0f}"
    return str(value)
