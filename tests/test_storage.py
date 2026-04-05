from datetime import date
from pathlib import Path

import pandas as pd

from src.models import CoinPrice
from src.storage import append_price, cleanup_zeros, load_full_history, load_history


def test_append_price_creates_file(tmp_path: Path) -> None:
    filepath = tmp_path / "test.csv"
    price = CoinPrice(
        coin="bitcoin",
        symbol="BTC",
        price=67500.0,
        change_24h=1.2,
        date=date(2026, 4, 5),
    )
    append_price(price, filepath)
    assert filepath.exists()
    df = pd.read_csv(filepath)
    assert len(df) == 1
    assert df.iloc[0]["price"] == 67500.0
    assert df.iloc[0]["change_24h"] == 1.2


def test_append_price_prepends_to_existing(tmp_path: Path) -> None:
    filepath = tmp_path / "test.csv"
    old = CoinPrice(
        coin="bitcoin",
        symbol="BTC",
        price=60000.0,
        change_24h=-0.5,
        date=date(2026, 4, 4),
    )
    new = CoinPrice(
        coin="bitcoin",
        symbol="BTC",
        price=67500.0,
        change_24h=1.2,
        date=date(2026, 4, 5),
    )
    append_price(old, filepath)
    append_price(new, filepath)
    df = pd.read_csv(filepath)
    assert len(df) == 2
    assert df.iloc[0]["date"] == "2026-04-05"
    assert df.iloc[1]["date"] == "2026-04-04"


def test_load_history_returns_last_n_days(tmp_path: Path) -> None:
    filepath = tmp_path / "test.csv"
    for i in range(10):
        price = CoinPrice(
            coin="bitcoin",
            symbol="BTC",
            price=60000.0 + i * 1000,
            change_24h=0.1 * i,
            date=date(2026, 4, 1 + i),
        )
        append_price(price, filepath)
    df = load_history(filepath, days=7)
    assert len(df) == 7


def test_load_history_missing_file(tmp_path: Path) -> None:
    filepath = tmp_path / "missing.csv"
    df = load_history(filepath)
    assert len(df) == 0


def test_load_full_history(tmp_path: Path) -> None:
    filepath = tmp_path / "test.csv"
    for i in range(10):
        price = CoinPrice(
            coin="bitcoin",
            symbol="BTC",
            price=60000.0 + i * 1000,
            change_24h=0.1 * i,
            date=date(2026, 4, 1 + i),
        )
        append_price(price, filepath)
    df = load_full_history(filepath)
    assert len(df) == 10


def test_cleanup_zeros(tmp_path: Path) -> None:
    filepath = tmp_path / "test.csv"
    df = pd.DataFrame(
        {
            "date": ["2026-04-01", "2026-04-02", "2026-04-03"],
            "price": [67500.0, 0.0, 68000.0],
        }
    )
    df.to_csv(filepath, index=False)
    cleanup_zeros(filepath)
    result = pd.read_csv(filepath)
    assert len(result) == 2
    assert 0.0 not in result["price"].values


def test_load_history_backward_compat_no_change_24h(tmp_path: Path) -> None:
    filepath = tmp_path / "test.csv"
    df = pd.DataFrame(
        {
            "date": ["2026-04-05", "2026-04-04"],
            "price": [67500.0, 66000.0],
        }
    )
    df.to_csv(filepath, index=False)
    result = load_history(filepath, days=7)
    assert "change_24h" in result.columns
    assert pd.isna(result.iloc[0]["change_24h"])
