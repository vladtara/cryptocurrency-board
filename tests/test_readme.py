from datetime import date

from src.models import CoinPrice
from src.readme import render_readme


def test_render_readme_contains_prices() -> None:
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
    stats = {
        "BTC": {"high": 68000.0, "low": 65000.0, "avg": 66000.0},
        "ETH": {"high": 3500.0, "low": 3300.0, "avg": 3400.0},
    }

    content = render_readme(prices, stats)

    assert "$67,500.00" in content
    assert "$3,450.00" in content


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
    stats = {
        "BTC": {"high": 68000.0, "low": 65000.0, "avg": 66000.0},
        "ETH": {"high": 3500.0, "low": 3300.0, "avg": 3400.0},
    }

    content = render_readme(prices, stats)

    assert "▲" in content


def test_render_readme_shows_negative_change() -> None:
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
    stats = {
        "BTC": {"high": 68000.0, "low": 65000.0, "avg": 66000.0},
        "ETH": {"high": 3500.0, "low": 3300.0, "avg": 3400.0},
    }

    content = render_readme(prices, stats)

    assert "▼" in content


def test_render_readme_contains_summary_stats() -> None:
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
    stats = {
        "BTC": {"high": 68000.0, "low": 65000.0, "avg": 66000.0},
        "ETH": {"high": 3500.0, "low": 3300.0, "avg": 3400.0},
    }

    content = render_readme(prices, stats)

    assert "$68,000.00" in content
    assert "$65,000.00" in content
    assert "7-Day Summary" in content


def test_render_readme_contains_timestamp() -> None:
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
    stats = {
        "BTC": {"high": 68000.0, "low": 65000.0, "avg": 66000.0},
        "ETH": {"high": 3500.0, "low": 3300.0, "avg": 3400.0},
    }

    content = render_readme(prices, stats)

    assert "Last updated:" in content
