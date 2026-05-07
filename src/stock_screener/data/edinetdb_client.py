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
        self.base_url = os.getenv("EDINETDB_BASE_URL", "https://edinetdb.jp/v1").rstrip("/")
        self.cache = JsonCache(get_cache_dir())

    def load_universe(self, use_sample: bool = False) -> list[tuple[Company, FinancialSeries]]:
        if use_sample or not self.api_key:
            return load_sample_universe()

        companies = self._get("/companies", params={"per_page": 5000, "include_nulls": "true"})
        return self._normalize_universe(companies)

    def load_dividend_universe(self, limit: int = 500, use_sample: bool = False) -> list[tuple[Company, FinancialSeries]]:
        if use_sample or not self.api_key:
            return load_sample_universe()

        params = {
            "dividend_yield_gte": 3,
            "payout_ratio_lte": 90,
            "equity_ratio_gte": 20,
            "sort": "dividend_yield",
            "order": "desc",
            "limit": min(limit, 500),
            "include_nulls": "true",
        }
        try:
            companies = self._get("/screener", params=params)
        except httpx.HTTPStatusError:
            companies = self._get("/rankings/dividend-yield", params={"limit": min(limit, 500)})
        return self._normalize_universe(companies)

    def _get(self, path: str, params: dict[str, Any] | None = None) -> Any:
        cache_key = f"{path}:{params or {}}"
        cached = self.cache.get(cache_key)
        if cached is not None:
            return cached

        headers = {"X-API-Key": self.api_key}
        with httpx.Client(timeout=30) as client:
            response = client.get(f"{self.base_url}{path}", params=params, headers=headers)
            response.raise_for_status()
            data = response.json()
        self.cache.set(cache_key, data)
        return data

    def _normalize_universe(self, payload: Any) -> list[tuple[Company, FinancialSeries]]:
        items = _extract_items(payload)
        universe: list[tuple[Company, FinancialSeries]] = []
        if not isinstance(items, list):
            return universe

        for item in items:
            company = Company(
                code=str(_first(item, "sec_code", "security_code", "code", "ticker", "securities_code") or ""),
                name=str(_first(item, "filer_name", "name", "company_name", "companyName") or ""),
                market=item.get("market"),
                sector=item.get("sector") or item.get("industry"),
                edinet_code=_first(item, "edinet_code", "edinetCode"),
                price=_to_float(_first(item, "price", "stock_price", "share_price", "current_price")),
            )
            snapshots = _extract_snapshots(item)
            universe.append((company, FinancialSeries(company_code=company.code, snapshots=snapshots)))
        return universe


def _extract_items(payload: Any) -> Any:
    if not isinstance(payload, dict):
        return payload
    for key in ("data", "results", "companies", "items", "rankings"):
        value = payload.get(key)
        if isinstance(value, list):
            return value
    return payload


def _extract_snapshots(item: dict[str, Any]) -> list[FinancialSnapshot]:
    raw = item.get("financials") or item.get("years") or item.get("snapshots") or []
    if isinstance(raw, dict):
        raw = list(raw.values())
    if not raw:
        raw = [item.get("latest_financial") or item.get("latest") or item]
    snapshots: list[FinancialSnapshot] = []
    for entry in raw:
        snapshots.append(
            FinancialSnapshot(
                fiscal_year=_to_int(_first(entry, "fiscal_year", "fiscalYear", "year")),
                revenue=_to_float(_first(entry, "revenue", "net_sales")),
                operating_income=_to_float(_first(entry, "operating_income", "operatingIncome")),
                net_income=_to_float(_first(entry, "net_income", "netIncome", "profit")),
                eps=_to_float(_first(entry, "eps", "adjusted_eps", "adjustedEps")),
                roe=_to_ratio(_first(entry, "roe", "roe_official", "roeOfficial")),
                equity_ratio=_to_ratio(_first(entry, "equity_ratio", "equity_ratio_official", "equityRatio")),
                operating_cf=_to_float(_first(entry, "operating_cf", "operating_cash_flow", "cf_operating", "cfOperating")),
                free_cf=_to_float(_first(entry, "free_cf", "free_cash_flow", "fcf")),
                dividend_per_share=_to_float(_first(entry, "dividend_per_share", "adjusted_dividend_per_share", "dps")),
                dividend_yield=_to_ratio(_first(entry, "dividend_yield", "dividendYield")),
                payout_ratio=_to_ratio(_first(entry, "payout_ratio", "payoutRatio")),
                per=_to_float(_first(entry, "per")),
                pbr=_to_float(_first(entry, "pbr")),
            )
        )
    return snapshots


def _first(item: dict[str, Any], *keys: str) -> Any:
    for key in keys:
        value = item.get(key)
        if value not in (None, ""):
            return value
    return None


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
