from __future__ import annotations

import os
from typing import Any

import httpx

from stock_screener.config import get_cache_dir, load_environment
from stock_screener.data.cache import JsonCache
from stock_screener.data.sample_data import load_sample_universe
from stock_screener.models.company import Company
from stock_screener.models.financials import FinancialSeries, FinancialSnapshot


class EdinetDbClient:
    def __init__(self) -> None:
        load_environment()
        self.api_key = os.getenv("EDINETDB_API_KEY")
        self.base_url = os.getenv("EDINETDB_BASE_URL", "https://edinetdb.jp/api/v1").rstrip("/")
        self.cache = JsonCache(get_cache_dir())

    def load_universe(self, use_sample: bool = False) -> list[tuple[Company, FinancialSeries]]:
        if use_sample or not self.api_key:
            return load_sample_universe()

        rankings = self._get("/ranking", params={"type": "market_cap", "limit": 4000})
        return self._normalize_universe(rankings)

    def _get(self, path: str, params: dict[str, Any] | None = None) -> Any:
        cache_key = f"{path}:{params or {}}"
        cached = self.cache.get(cache_key)
        if cached is not None:
            return cached

        headers = {"Authorization": f"Bearer {self.api_key}"}
        with httpx.Client(timeout=30) as client:
            response = client.get(f"{self.base_url}{path}", params=params, headers=headers)
            response.raise_for_status()
            data = response.json()
        self.cache.set(cache_key, data)
        return data

    def _normalize_universe(self, payload: Any) -> list[tuple[Company, FinancialSeries]]:
        items = payload.get("data", payload) if isinstance(payload, dict) else payload
        universe: list[tuple[Company, FinancialSeries]] = []
        if not isinstance(items, list):
            return universe

        for item in items:
            company = Company(
                code=str(item.get("code") or item.get("ticker") or item.get("securities_code") or ""),
                name=str(item.get("name") or item.get("company_name") or ""),
                market=item.get("market"),
                sector=item.get("sector") or item.get("industry"),
                edinet_code=item.get("edinet_code"),
                price=_to_float(item.get("price") or item.get("stock_price")),
            )
            snapshots = _extract_snapshots(item)
            universe.append((company, FinancialSeries(company_code=company.code, snapshots=snapshots)))
        return universe


def _extract_snapshots(item: dict[str, Any]) -> list[FinancialSnapshot]:
    raw = item.get("financials") or item.get("years") or item.get("snapshots") or []
    if isinstance(raw, dict):
        raw = list(raw.values())
    snapshots: list[FinancialSnapshot] = []
    for entry in raw:
        snapshots.append(
            FinancialSnapshot(
                fiscal_year=_to_int(entry.get("fiscal_year") or entry.get("year")),
                revenue=_to_float(entry.get("revenue") or entry.get("net_sales")),
                operating_income=_to_float(entry.get("operating_income")),
                net_income=_to_float(entry.get("net_income") or entry.get("profit")),
                eps=_to_float(entry.get("eps")),
                roe=_to_ratio(entry.get("roe")),
                equity_ratio=_to_ratio(entry.get("equity_ratio")),
                operating_cf=_to_float(entry.get("operating_cf") or entry.get("operating_cash_flow")),
                free_cf=_to_float(entry.get("free_cf") or entry.get("free_cash_flow")),
                dividend_per_share=_to_float(entry.get("dividend_per_share") or entry.get("dps")),
                dividend_yield=_to_ratio(entry.get("dividend_yield")),
                payout_ratio=_to_ratio(entry.get("payout_ratio")),
                per=_to_float(entry.get("per")),
                pbr=_to_float(entry.get("pbr")),
            )
        )
    return snapshots


def _to_float(value: Any) -> float | None:
    if value in (None, ""):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _to_int(value: Any) -> int | None:
    number = _to_float(value)
    return int(number) if number is not None else None


def _to_ratio(value: Any) -> float | None:
    number = _to_float(value)
    if number is None:
        return None
    return number / 100 if number > 1 else number
