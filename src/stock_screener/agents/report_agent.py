from __future__ import annotations

from datetime import date
from pathlib import Path

from stock_screener.models.screening_result import ScreeningResult
from stock_screener.reports.csv import write_csv
from stock_screener.reports.markdown import write_markdown


class ReportAgent:
    def __init__(self, output_dir: Path) -> None:
        self.output_dir = output_dir

    def write_dividend(self, results: list[ScreeningResult]) -> Path:
        path = self.output_dir / f"dividend_{date.today().isoformat()}.csv"
        write_csv(results, path)
        return path

    def write_growth(self, results: list[ScreeningResult]) -> Path:
        path = self.output_dir / f"growth_{date.today().isoformat()}.csv"
        write_csv(results, path)
        return path

    def write_report(
        self,
        dividend_results: list[ScreeningResult],
        growth_results: list[ScreeningResult],
    ) -> Path:
        path = self.output_dir / f"report_{date.today().isoformat()}.md"
        write_markdown(dividend_results, growth_results, path)
        return path
