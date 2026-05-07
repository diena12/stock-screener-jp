from __future__ import annotations


def clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


def ratio_score(value: float | None, target: float) -> float:
    if value is None or target <= 0:
        return 0.0
    return clamp(value / target)


def inverse_threshold_score(value: float | None, ideal: float, risky: float) -> float:
    if value is None:
        return 0.0
    if value <= ideal:
        return 1.0
    if value >= risky:
        return 0.0
    return clamp(1 - ((value - ideal) / (risky - ideal)))
