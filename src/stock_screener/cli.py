from __future__ import annotations

import argparse
from pathlib import Path

from rich.console import Console
from rich.table import Table

from stock_screener.agents.data_agent import DataAgent
from stock_screener.agents.dividend_agent import DividendAgent
from stock_screener.agents.growth_agent import GrowthAgent
from stock_screener.agents.report_agent import ReportAgent
from stock_screener.agents.risk_agent import RiskAgent
from stock_screener.config import get_output_dir, load_rules
from stock_screener.models.screening_result import ScreeningResult


console = Console()


def main() -> None:
    parser = argparse.ArgumentParser(description="Japanese stock screener CLI")
    parser.add_argument("mode", choices=["dividend", "growth", "all"], help="screening mode")
    parser.add_argument("--top", type=int, default=30, help="number of results")
    parser.add_argument("--sample", action="store_true", help="use bundled sample data")
    parser.add_argument("--output-dir", type=Path, default=None, help="output directory")
    args = parser.parse_args()

    data_agent = DataAgent()

    risk_agent = RiskAgent(load_rules("risk_rules"))
    dividend_agent = DividendAgent(load_rules("dividend_rules"), risk_agent)
    growth_agent = GrowthAgent(load_rules("growth_rules"), risk_agent)
    report_agent = ReportAgent(args.output_dir or get_output_dir())

    dividend_results: list[ScreeningResult] = []
    growth_results: list[ScreeningResult] = []

    if args.mode in ("dividend", "all"):
        dividend_universe = data_agent.load_dividend_universe(limit=max(args.top * 10, 100), use_sample=args.sample)
        dividend_results = dividend_agent.screen(dividend_universe, args.top)
        path = report_agent.write_dividend(dividend_results)
        _print_results("Dividend candidates", dividend_results)
        console.print(f"[green]CSV written:[/green] {path}")

    if args.mode in ("growth", "all"):
        universe = data_agent.load_universe(use_sample=args.sample)
        growth_results = growth_agent.screen(universe, args.top)
        path = report_agent.write_growth(growth_results)
        _print_results("Growth candidates", growth_results)
        console.print(f"[green]CSV written:[/green] {path}")

    if args.mode == "all":
        path = report_agent.write_report(dividend_results, growth_results)
        console.print(f"[green]Report written:[/green] {path}")


def _print_results(title: str, results: list[ScreeningResult]) -> None:
    table = Table(title=title)
    table.add_column("Rank", justify="right")
    table.add_column("Code")
    table.add_column("Name")
    table.add_column("Lot", justify="right")
    table.add_column("Score", justify="right")
    table.add_column("Risk", justify="right")
    table.add_column("Reasons")

    for index, result in enumerate(results[:20], start=1):
        row = result.to_row()
        lot_price = row["lot_price"]
        table.add_row(
            str(index),
            str(row["code"]),
            str(row["name"]),
            f"{lot_price:,.0f}" if isinstance(lot_price, float) else "-",
            str(row["score"]),
            str(row["risk_score"]),
            str(row["reasons"]),
        )
    console.print(table)


if __name__ == "__main__":
    main()
