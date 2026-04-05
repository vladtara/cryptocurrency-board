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
