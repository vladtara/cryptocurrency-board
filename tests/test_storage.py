from datetime import date
from pathlib import Path

import pandas as pd
import pytest

from src.models import CoinPrice
from src.storage import (
    append_price,
    cleanup_zeros,
    compute_window_metrics,
    load_full_history,
    load_history,
    load_named_windows,
)


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


def test_load_named_windows_returns_requested_ranges(tmp_path: Path) -> None:
    filepath = tmp_path / "btc.csv"
    pd.DataFrame(
        {
            "date": [f"2026-01-{day:02d}" for day in range(10, 0, -1)],
            "price": [float(value) for value in range(10, 0, -1)],
            "change_24h": [0.0] * 10,
        }
    ).to_csv(filepath, index=False)

    windows = load_named_windows(filepath, {"7D": 7, "30D": 30})

    assert list(windows) == ["7D", "30D"]
    assert len(windows["7D"]) == 7
    assert len(windows["30D"]) == 10


def test_compute_window_metrics_returns_primary_metrics() -> None:
    df = pd.DataFrame(
        {
            "date": [
                "2026-04-05",
                "2026-04-04",
                "2026-04-03",
                "2026-04-02",
            ],
            "price": [110.0, 100.0, 105.0, 95.0],
            "change_24h": [0.0, 0.0, 0.0, 0.0],
        }
    )

    metrics = compute_window_metrics(df)

    assert metrics["min"] == 95.0
    assert metrics["max"] == 110.0
    assert metrics["avg"] == 102.5
    assert metrics["median"] == 102.5
    assert metrics["return_pct"] == pytest.approx(15.7894736842)
    assert metrics["volatility"] >= 0.0


def test_compute_window_metrics_supports_secondary_metrics() -> None:
    df = pd.DataFrame(
        {
            "date": [
                "2026-04-05",
                "2026-04-04",
                "2026-04-03",
                "2026-04-02",
            ],
            "price": [110.0, 100.0, 105.0, 95.0],
            "change_24h": [0.0, 0.0, 0.0, 0.0],
        }
    )

    metrics = compute_window_metrics(df)

    assert "range_pct" in metrics
    assert "drawdown_pct" in metrics
    assert "up_day_ratio" in metrics
    assert "current_streak" in metrics


def test_compute_window_metrics_handles_single_row() -> None:
    df = pd.DataFrame(
        {
            "date": ["2026-04-05"],
            "price": [110.0],
            "change_24h": [0.0],
        }
    )

    metrics = compute_window_metrics(df)

    assert metrics["min"] == 110.0
    assert metrics["max"] == 110.0
    assert metrics["avg"] == 110.0
    assert metrics["median"] == 110.0
    assert metrics["return_pct"] == 0.0
    assert metrics["volatility"] == 0.0
