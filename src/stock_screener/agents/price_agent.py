from __future__ import annotations

import csv
import os
from datetime import date, timedelta
from io import StringIO

import httpx

from stock_screener.config import get_cache_dir, load_environment
from stock_screener.data.cache import JsonCache
from stock_screener.models.company import Company
from stock_screener.models.financials import FinancialSeries, FinancialSnapshot


class PriceAgent:
    def __init__(self) -> None:
        load_environment()
        self.base_url = os.getenv("STOOQ_BASE_URL", "https://stooq.com/q/d/l/").rstrip("/")
        self.cache = JsonCache(get_cache_dir() / "prices", ttl_hours=12)

    def enrich_company_series(self, company: Company, series: FinancialSeries, lookback_days: int = 370) -> list[str]:
        warnings: list[str] = []
        prices = self._fetch_daily_prices(company.code, lookback_days=lookback_days)
        if not prices:
            warnings.append("price data is missing")
            return warnings

        latest_close = prices[-1]["close"]
        highs = [row["high"] for row in prices if row["high"] is not None]
        lows = [row["low"] for row in prices if row["low"] is not None]

        company.price = latest_close
        latest = series.latest()
        if latest is None:
            latest = FinancialSnapshot()
            series.snapshots.append(latest)
        latest.highest_share_price = max(highs) if highs else None
        latest.lowest_share_price = min(lows) if lows else None
        return warnings

    def _fetch_daily_prices(self, code: str, lookback_days: int) -> list[dict[str, float | None]]:
        symbol = _to_stooq_symbol(code)
        if not symbol:
            return []

        end = date.today()
        start = end - timedelta(days=lookback_days)
        cache_key = f"stooq:{symbol}:{start:%Y%m%d}:{end:%Y%m%d}"
        cached = self.cache.get(cache_key)
        if cached is not None:
            return cached

        params = {
            "s": symbol,
            "d1": f"{start:%Y%m%d}",
            "d2": f"{end:%Y%m%d}",
            "i": "d",
        }
        try:
            with httpx.Client(timeout=20) as client:
                response = client.get(self.base_url + "/", params=params)
                response.raise_for_status()
        except httpx.HTTPError:
            return []

        rows = _parse_stooq_csv(response.text)
        self.cache.set(cache_key, rows)
        return rows


def _to_stooq_symbol(code: str) -> str | None:
    normalized = "".join(ch for ch in str(code) if ch.isdigit())
    if len(normalized) == 5 and normalized.endswith("0"):
        normalized = normalized[:-1]
    if len(normalized) != 4:
        return None
    return f"{normalized}.jp"


def _parse_stooq_csv(text: str) -> list[dict[str, float | None]]:
    if not text.strip() or "No data" in text:
        return []
    reader = csv.DictReader(StringIO(text.strip()))
    rows: list[dict[str, float | None]] = []
    for row in reader:
        lowered = {key.lower(): value for key, value in row.items() if key}
        close = _to_float(lowered.get("close"))
        if close is None:
            continue
        rows.append(
            {
                "open": _to_float(lowered.get("open")),
                "high": _to_float(lowered.get("high")),
                "low": _to_float(lowered.get("low")),
                "close": close,
                "volume": _to_float(lowered.get("volume")),
            }
        )
    return rows


def _to_float(value: str | None) -> float | None:
    if value in (None, "", "N/D"):
        return None
    try:
        return float(value)
    except ValueError:
        return None
