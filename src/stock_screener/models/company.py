from __future__ import annotations

from pydantic import BaseModel, Field


class Company(BaseModel):
    code: str
    name: str
    market: str | None = None
    sector: str | None = None
    edinet_code: str | None = None
    price: float | None = None
    lot_size: int = 100

    @property
    def lot_price(self) -> float | None:
        if self.price is None:
            return None
        return self.price * self.lot_size

    def display_code(self) -> str:
        return self.code or self.edinet_code or "-"
