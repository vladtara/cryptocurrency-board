import logging
from pathlib import Path

import pandas as pd

from src.models import CoinPrice

logger = logging.getLogger(__name__)
CSV_COLUMNS = pd.Index(["date", "price", "change_24h"])


def append_price(coin_price: CoinPrice, filepath: Path) -> None:
    """Append a price entry to the top of a CSV file."""
    new_row = pd.DataFrame(
        [
            {
                "date": coin_price.date.isoformat(),
                "price": coin_price.price,
                "change_24h": coin_price.change_24h,
            }
        ]
    )
    if filepath.exists():
        existing = pd.read_csv(filepath)
        df = pd.concat([new_row, existing], ignore_index=True)
    else:
        df = new_row
    df.to_csv(filepath, index=False)
    logger.info("Wrote 1 row to %s", filepath.name)


def load_history(filepath: Path, days: int = 7) -> pd.DataFrame:
    """Load the last N days from a CSV file."""
    if not filepath.exists():
        return pd.DataFrame(columns=CSV_COLUMNS)
    df = pd.read_csv(filepath)
    if "change_24h" not in df.columns:
        df["change_24h"] = float("nan")
    return df.head(days)


def load_full_history(filepath: Path) -> pd.DataFrame:
    """Load all rows from a CSV file."""
    if not filepath.exists():
        return pd.DataFrame(columns=CSV_COLUMNS)
    df = pd.read_csv(filepath)
    if "change_24h" not in df.columns:
        df["change_24h"] = float("nan")
    return df


def load_named_windows(
    filepath: Path,
    windows: dict[str, int],
) -> dict[str, pd.DataFrame]:
    """Load named history windows from newest rows in a CSV."""
    history = load_full_history(filepath)
    if not history.empty and "date" in history.columns:
        history = history.sort_values("date", ascending=False, kind="stable").reset_index(drop=True)
    return {label: history.head(days).copy() for label, days in windows.items()}


def compute_window_metrics(df: pd.DataFrame) -> dict[str, float | str]:
    """Compute dashboard metrics for a history window."""
    prices = df["price"].astype(float)
    if prices.empty:
        return {
            "min": 0.0,
            "max": 0.0,
            "avg": 0.0,
            "median": 0.0,
            "return_pct": 0.0,
            "volatility": 0.0,
            "range_pct": 0.0,
            "drawdown_pct": 0.0,
            "up_day_ratio": 0.0,
            "current_streak": "flat:0",
        }

    oldest = float(prices.iloc[-1])
    newest = float(prices.iloc[0])
    daily_returns = prices.pct_change(-1).dropna()

    peak = float("-inf")
    max_drawdown = 0.0
    for price in reversed(prices.tolist()):
        peak = max(peak, price)
        drawdown = 0.0 if peak == 0 else (peak - price) / peak * 100
        max_drawdown = max(max_drawdown, drawdown)

    diffs = prices.diff(-1).dropna()
    up_days = float((diffs > 0).sum())
    total_moves = float(len(diffs))

    streak_direction = "flat"
    streak_length = 0
    for move in diffs.tolist():
        direction = "up" if move > 0 else "down" if move < 0 else "flat"
        if streak_length == 0:
            streak_direction = direction
            streak_length = 1
            continue
        if direction == streak_direction:
            streak_length += 1
            continue
        break

    price_min = float(prices.min())
    price_max = float(prices.max())

    return {
        "min": price_min,
        "max": price_max,
        "avg": float(prices.mean()),
        "median": float(prices.median()),
        "return_pct": 0.0 if oldest == 0 else (newest - oldest) / oldest * 100,
        "volatility": 0.0 if daily_returns.empty else float(daily_returns.std() * 100),
        "range_pct": 0.0 if price_min == 0 else float((price_max - price_min) / price_min * 100),
        "drawdown_pct": float(max_drawdown),
        "up_day_ratio": 0.0 if total_moves == 0 else float(up_days / total_moves * 100),
        "current_streak": f"{streak_direction}:{streak_length}",
    }


def cleanup_zeros(filepath: Path) -> None:
    """Remove rows with price == 0.0 from a CSV file."""
    if not filepath.exists():
        return
    df = pd.read_csv(filepath)
    before = len(df)
    df = df[df["price"] != 0.0]
    df.to_csv(filepath, index=False)
    removed = before - len(df)
    if removed:
        logger.info("Removed %d zero-price rows from %s", removed, filepath.name)
