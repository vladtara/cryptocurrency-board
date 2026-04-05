from datetime import date

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
