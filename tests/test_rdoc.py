import asyncio
from datetime import date
from pathlib import Path

import pandas as pd
import pytest

import main as pipeline
from src.models import CoinPrice
from src.rdoc import render_readme


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
        "90D": {
            "BTC": {
                "min": 10.0,
                "max": 20.0,
                "avg": 15.0,
                "median": 14.0,
                "return_pct": 8.0,
                "volatility": 4.0,
            },
            "ETH": {
                "min": 30.0,
                "max": 40.0,
                "avg": 35.0,
                "median": 34.0,
                "return_pct": -2.0,
                "volatility": 5.0,
            },
        },
        "180D": {
            "BTC": {
                "min": 50.0,
                "max": 60.0,
                "avg": 55.0,
                "median": 54.0,
                "return_pct": 12.0,
                "volatility": 6.0,
            },
            "ETH": {
                "min": 70.0,
                "max": 80.0,
                "avg": 75.0,
                "median": 74.0,
                "return_pct": 1.0,
                "volatility": 7.0,
            },
        },
        "1Y": {
            "BTC": {
                "min": 1.0,
                "max": 2.0,
                "avg": 1.5,
                "median": 1.5,
                "return_pct": 10.0,
                "volatility": 3.0,
                "range_pct": 12.3,
                "drawdown_pct": 4.5,
            },
            "ETH": {
                "min": 1.0,
                "max": 2.0,
                "avg": 1.5,
                "median": 1.5,
                "return_pct": 10.0,
                "volatility": 3.0,
                "range_pct": 9.8,
                "drawdown_pct": 3.2,
            },
        },
    }


def _sample_charts() -> dict[str, list[dict[str, str]]]:
    return {
        "BTC": [
            {"label": "7D", "path": "./img/btc-usd-7d.svg"},
            {"label": "30D", "path": "./img/btc-usd-30d.svg"},
            {"label": "90D", "path": "./img/btc-usd-90d.svg"},
            {"label": "180D", "path": "./img/btc-usd-180d.svg"},
            {"label": "1Y", "path": "./img/btc-usd-1y.svg"},
        ],
        "ETH": [
            {"label": "7D", "path": "./img/eth-usd-7d.svg"},
            {"label": "30D", "path": "./img/eth-usd-30d.svg"},
            {"label": "90D", "path": "./img/eth-usd-90d.svg"},
            {"label": "180D", "path": "./img/eth-usd-180d.svg"},
            {"label": "1Y", "path": "./img/eth-usd-1y.svg"},
        ],
    }


def test_render_readme_contains_prices() -> None:
    prices = _sample_prices()
    windows = _sample_windows()
    charts = _sample_charts()

    content = render_readme(prices, windows, charts)

    assert "$67,500.00" in content
    assert "$3,450.00" in content


def test_render_readme_uses_per_horizon_dashboard_sections() -> None:
    prices = _sample_prices()
    windows = _sample_windows()
    charts = _sample_charts()

    content = render_readme(prices, windows, charts)

    assert "## 7-Day Dashboard" in content
    assert "## 30D Dashboard" in content
    assert "## 90D Dashboard" in content
    assert "## 180D Dashboard" in content
    assert "## 1Y Dashboard" in content
    assert "## Extended Windows" not in content
    assert "./img/btc-usd-7d.svg" in content
    assert "./img/eth-usd-7d.svg" in content


def test_render_readme_places_matching_charts_inside_each_dashboard() -> None:
    prices = _sample_prices()
    windows = _sample_windows()
    charts = _sample_charts()

    content = render_readme(prices, windows, charts)

    assert "./img/btc-usd-7d.svg" in content
    assert "./img/eth-usd-7d.svg" in content
    assert "./img/btc-usd-30d.svg" in content
    assert "./img/eth-usd-30d.svg" in content
    assert "./img/btc-usd-90d.svg" in content
    assert "./img/eth-usd-90d.svg" in content
    assert "./img/btc-usd-180d.svg" in content
    assert "./img/eth-usd-180d.svg" in content
    assert "./img/btc-usd-1y.svg" in content
    assert "./img/eth-usd-1y.svg" in content


def test_render_readme_keeps_lower_chart_sections() -> None:
    prices = _sample_prices()
    windows = _sample_windows()
    charts = _sample_charts()

    content = render_readme(prices, windows, charts)
    assert "## 1Y Dashboard" in content


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
    assert "## 7-Day Dashboard" in content
    assert "## 30D Dashboard" in content
    assert "./img/btc-usd-7d.svg" in content
    assert "./img/eth-usd-7d.svg" in content


def test_render_readme_contains_deep_stats() -> None:
    prices = _sample_prices()
    windows = _sample_windows()
    charts = _sample_charts()

    content = render_readme(prices, windows, charts)

    assert "## Deep Stats" in content
    assert "### 1Y" in content
    assert "| **BTC** | 12.3% | 4.5% |" in content
    assert "| **ETH** | 9.8% | 3.2% |" in content


def test_render_readme_omits_deep_stats_without_1y() -> None:
    prices = _sample_prices()
    windows = {
        label: metrics for label, metrics in _sample_windows().items() if label != "1Y"
    }
    charts = _sample_charts()

    content = render_readme(prices, windows, charts)

    assert "## Deep Stats" not in content
    assert "### 1Y" not in content


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
    chart_calls: list[dict[str, str]] = []
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
        chart_calls.append(
            {
                "coin": coin,
                "path": f"./{output_path.as_posix()}",
                "horizon_label": horizon_label,
                "rows": str(len(df)),
            }
        )

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
    assert "## 7-Day Dashboard" in rendered
    assert "## 30D Dashboard" in rendered
    assert "## 90D Dashboard" in rendered
    assert "## 180D Dashboard" in rendered
    assert "## 1Y Dashboard" in rendered
    assert "./img/btc-usd-7d.svg" in rendered
    assert "./img/eth-usd-7d.svg" in rendered
    assert "./img/btc-usd-30d.svg" in rendered
    assert "./img/btc-usd-90d.svg" in rendered
    assert "./img/btc-usd-180d.svg" in rendered
    assert "./img/btc-usd-1y.svg" in rendered
    assert "./img/eth-usd-30d.svg" in rendered
    assert "./img/eth-usd-90d.svg" in rendered
    assert "./img/eth-usd-180d.svg" in rendered
    assert "./img/eth-usd-1y.svg" in rendered
    assert chart_calls == [
        {
            "coin": "BTC-USD",
            "path": "./img/btc-usd-7d.svg",
            "horizon_label": "7D",
            "rows": "2",
        },
        {
            "coin": "BTC-USD",
            "path": "./img/btc-usd-30d.svg",
            "horizon_label": "30D",
            "rows": "2",
        },
        {
            "coin": "BTC-USD",
            "path": "./img/btc-usd-90d.svg",
            "horizon_label": "90D",
            "rows": "2",
        },
        {
            "coin": "BTC-USD",
            "path": "./img/btc-usd-180d.svg",
            "horizon_label": "180D",
            "rows": "2",
        },
        {
            "coin": "BTC-USD",
            "path": "./img/btc-usd-1y.svg",
            "horizon_label": "1Y",
            "rows": "2",
        },
        {
            "coin": "ETH-USD",
            "path": "./img/eth-usd-7d.svg",
            "horizon_label": "7D",
            "rows": "2",
        },
        {
            "coin": "ETH-USD",
            "path": "./img/eth-usd-30d.svg",
            "horizon_label": "30D",
            "rows": "2",
        },
        {
            "coin": "ETH-USD",
            "path": "./img/eth-usd-90d.svg",
            "horizon_label": "90D",
            "rows": "2",
        },
        {
            "coin": "ETH-USD",
            "path": "./img/eth-usd-180d.svg",
            "horizon_label": "180D",
            "rows": "2",
        },
        {
            "coin": "ETH-USD",
            "path": "./img/eth-usd-1y.svg",
            "horizon_label": "1Y",
            "rows": "2",
        },
    ]
    assert {call["horizon_label"] for call in chart_calls} == {
        "7D",
        "30D",
        "90D",
        "180D",
        "1Y",
    }
    assert {call["path"] for call in chart_calls} == {
        "./img/btc-usd-7d.svg",
        "./img/btc-usd-30d.svg",
        "./img/btc-usd-90d.svg",
        "./img/btc-usd-180d.svg",
        "./img/btc-usd-1y.svg",
        "./img/eth-usd-7d.svg",
        "./img/eth-usd-30d.svg",
        "./img/eth-usd-90d.svg",
        "./img/eth-usd-180d.svg",
        "./img/eth-usd-1y.svg",
    }
    assert captured["window_labels"] == list(windows)
    assert set(captured["windows"]) == set(windows)
    assert set(captured["windows"]["7D"]) == {"BTC", "ETH"}
    assert captured["charts"] == {
        "BTC": [
            {"label": "7D", "path": "./img/btc-usd-7d.svg"},
            {"label": "30D", "path": "./img/btc-usd-30d.svg"},
            {"label": "90D", "path": "./img/btc-usd-90d.svg"},
            {"label": "180D", "path": "./img/btc-usd-180d.svg"},
            {"label": "1Y", "path": "./img/btc-usd-1y.svg"},
        ],
        "ETH": [
            {"label": "7D", "path": "./img/eth-usd-7d.svg"},
            {"label": "30D", "path": "./img/eth-usd-30d.svg"},
            {"label": "90D", "path": "./img/eth-usd-90d.svg"},
            {"label": "180D", "path": "./img/eth-usd-180d.svg"},
            {"label": "1Y", "path": "./img/eth-usd-1y.svg"},
        ],
    }
