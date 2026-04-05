import asyncio
from datetime import date
from pathlib import Path

import pandas as pd
import pytest

import main as pipeline
from src.models import CoinPrice
from src.readme import render_readme


def _sample_prices() -> dict[str, CoinPrice]:
    return {
        "bitcoin": CoinPrice(
            coin="bitcoin",
            symbol="BTC",
            price=67500.0,
            change_24h=1.2,
            date=date(2026, 4, 5),
        ),
        "ethereum": CoinPrice(
            coin="ethereum",
            symbol="ETH",
            price=3450.0,
            change_24h=-0.8,
            date=date(2026, 4, 5),
        ),
    }


def _sample_windows() -> dict[str, dict[str, dict[str, float | str]]]:
    return {
        "7D": {
            "BTC": {
                "min": 1.0,
                "max": 2.0,
                "avg": 1.5,
                "median": 1.5,
                "return_pct": 10.0,
                "volatility": 3.0,
            },
            "ETH": {
                "min": 1.0,
                "max": 2.0,
                "avg": 1.5,
                "median": 1.5,
                "return_pct": 10.0,
                "volatility": 3.0,
            },
        },
        "30D": {
            "BTC": {
                "min": 1.0,
                "max": 2.0,
                "avg": 1.5,
                "median": 1.5,
                "return_pct": 10.0,
                "volatility": 3.0,
            },
            "ETH": {
                "min": 1.0,
                "max": 2.0,
                "avg": 1.5,
                "median": 1.5,
                "return_pct": 10.0,
                "volatility": 3.0,
            },
        },
    }


def _sample_charts() -> dict[str, list[dict[str, str]]]:
    return {
        "BTC": [{"label": "30D", "path": "./img/btc-usd-30d.svg"}],
        "ETH": [{"label": "30D", "path": "./img/eth-usd-30d.svg"}],
    }


def test_render_readme_contains_prices() -> None:
    prices = _sample_prices()
    windows = _sample_windows()
    charts = _sample_charts()

    content = render_readme(prices, windows, charts)

    assert "$67,500.00" in content
    assert "$3,450.00" in content


def test_render_readme_includes_multi_window_headers() -> None:
    prices = _sample_prices()
    windows = _sample_windows()
    charts = _sample_charts()

    content = render_readme(prices, windows, charts)

    assert "## Multi-Window Summary" in content
    assert "### 7D" in content
    assert "### 30D" in content
    assert "./img/btc-usd-30d.svg" in content
    assert "./img/eth-usd-30d.svg" in content


def test_render_readme_shows_positive_change() -> None:
    prices = {
        "bitcoin": CoinPrice(
            coin="bitcoin",
            symbol="BTC",
            price=67500.0,
            change_24h=1.2,
            date=date(2026, 4, 5),
        ),
        "ethereum": CoinPrice(
            coin="ethereum",
            symbol="ETH",
            price=3450.0,
            change_24h=-0.8,
            date=date(2026, 4, 5),
        ),
    }
    windows = _sample_windows()
    charts = _sample_charts()

    content = render_readme(prices, windows, charts)

    assert "▲" in content


def test_render_readme_shows_negative_change() -> None:
    prices = _sample_prices()
    windows = _sample_windows()
    charts = _sample_charts()

    content = render_readme(prices, windows, charts)

    assert "▼" in content


def test_render_readme_contains_summary_stats() -> None:
    prices = _sample_prices()
    windows = _sample_windows()
    charts = _sample_charts()

    content = render_readme(prices, windows, charts)

    assert "$1.00" in content
    assert "$2.00" in content
    assert "+10.0%" in content
    assert "Multi-Window Summary" in content


def test_render_readme_contains_timestamp() -> None:
    prices = _sample_prices()
    windows = _sample_windows()
    charts = _sample_charts()

    content = render_readme(prices, windows, charts)

    assert "Last updated:" in content


def test_run_builds_named_windows_and_selected_charts(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    windows = {
        "7D": 7,
        "30D": 30,
        "90D": 90,
        "180D": 180,
        "1Y": 365,
    }
    captured: dict[str, object] = {}
    real_template_dir = Path(__file__).resolve().parents[1] / "templates"
    history = pd.DataFrame(
        {
            "date": ["2026-04-05", "2026-04-04"],
            "price": [100.0, 90.0],
            "change_24h": [1.0, -1.0],
        }
    )

    async def fake_fetch_prices(api_key: str) -> dict[str, CoinPrice]:
        assert api_key == "test-key"
        return _sample_prices()

    def fake_cleanup_zeros(filepath: Path) -> None:
        del filepath

    def fake_append_price(coin_price: CoinPrice, filepath: Path) -> None:
        del coin_price, filepath

    def fake_load_named_windows(
        filepath: Path,
        requested_windows: dict[str, int],
    ) -> dict[str, pd.DataFrame]:
        del filepath
        captured["window_labels"] = list(requested_windows)
        return {label: history.copy() for label in requested_windows}

    def fake_generate_chart(
        df: pd.DataFrame,
        coin: str,
        output_path: Path,
        horizon_label: str = "7D",
    ) -> None:
        del df, coin, output_path, horizon_label

    def fake_render_readme(
        prices: dict[str, CoinPrice],
        window_stats: dict[str, dict[str, dict[str, float | str]]],
        chart_paths: dict[str, list[dict[str, str]]],
        _template_dir: str = "./templates",
    ) -> str:
        del _template_dir
        captured["prices"] = prices
        captured["windows"] = window_stats
        captured["charts"] = chart_paths
        rendered = render_readme(
            prices,
            window_stats,
            chart_paths,
            str(real_template_dir),
        )
        captured["rendered"] = rendered
        return rendered

    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("COINGECKO_API_KEY", "test-key")
    monkeypatch.setattr(pipeline, "fetch_prices", fake_fetch_prices)
    monkeypatch.setattr(pipeline, "cleanup_zeros", fake_cleanup_zeros)
    monkeypatch.setattr(pipeline, "append_price", fake_append_price)
    monkeypatch.setattr(pipeline, "load_named_windows", fake_load_named_windows)
    monkeypatch.setattr(pipeline, "generate_chart", fake_generate_chart)
    monkeypatch.setattr(pipeline, "render_readme", fake_render_readme)

    asyncio.run(pipeline.run())

    rendered = captured["rendered"]
    assert "### 7D" in rendered
    assert "### 30D" in rendered
    assert "### 90D" in rendered
    assert "### 180D" in rendered
    assert "### 1Y" in rendered
    assert "./img/btc-usd-30d.svg" in rendered
    assert "./img/btc-usd-180d.svg" in rendered
    assert "./img/btc-usd-1y.svg" in rendered
    assert "./img/eth-usd-30d.svg" in rendered
    assert "./img/eth-usd-180d.svg" in rendered
    assert "./img/eth-usd-1y.svg" in rendered
    assert captured["window_labels"] == list(windows)
    assert set(captured["windows"]) == set(windows)
    assert set(captured["windows"]["7D"]) == {"BTC", "ETH"}
    assert captured["charts"] == {
        "BTC": [
            {"label": "30D", "path": "./img/btc-usd-30d.svg"},
            {"label": "180D", "path": "./img/btc-usd-180d.svg"},
            {"label": "1Y", "path": "./img/btc-usd-1y.svg"},
        ],
        "ETH": [
            {"label": "30D", "path": "./img/eth-usd-30d.svg"},
            {"label": "180D", "path": "./img/eth-usd-180d.svg"},
            {"label": "1Y", "path": "./img/eth-usd-1y.svg"},
        ],
    }
