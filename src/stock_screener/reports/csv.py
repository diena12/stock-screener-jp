from __future__ import annotations

from pathlib import Path

import pandas as pd

from stock_screener.models.screening_result import ScreeningResult


def write_csv(results: list[ScreeningResult], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = [result.to_row() for result in results]
    pd.DataFrame(rows).to_csv(path, index=False, encoding="utf-8-sig")
