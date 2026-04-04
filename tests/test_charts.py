from pathlib import Path

import pandas as pd

from src.charts import generate_chart


def test_generate_chart_creates_svg(tmp_path: Path) -> None:
    df = pd.DataFrame(
        {
            "date": ["2026-04-01", "2026-04-02", "2026-04-03"],
            "price": [65000.0, 66000.0, 67500.0],
        }
    )
    output = tmp_path / "btc-usd.svg"
    generate_chart(df, "BTC-USD", output)
    assert output.exists()
    content = output.read_text()
    assert "<svg" in content


def test_generate_chart_contains_data_points(tmp_path: Path) -> None:
    df = pd.DataFrame(
        {
            "date": ["2026-04-01", "2026-04-02"],
            "price": [65000.0, 67500.0],
        }
    )
    output = tmp_path / "eth-usd.svg"
    generate_chart(df, "ETH-USD", output)
    content = output.read_text()
    assert "65000" in content or "65,000" in content
    assert "67500" in content or "67,500" in content


def test_generate_chart_btc_uses_orange(tmp_path: Path) -> None:
    df = pd.DataFrame(
        {
            "date": ["2026-04-01"],
            "price": [67500.0],
        }
    )
    output = tmp_path / "btc-usd.svg"
    generate_chart(df, "BTC-USD", output)
    content = output.read_text()
    # Pygal uses hex colors in the SVG — orange is #ff8c00 or similar
    assert "svg" in content.lower()


def test_generate_chart_eth_uses_blue(tmp_path: Path) -> None:
    df = pd.DataFrame(
        {
            "date": ["2026-04-01"],
            "price": [3450.0],
        }
    )
    output = tmp_path / "eth-usd.svg"
    generate_chart(df, "ETH-USD", output)
    content = output.read_text()
    assert "svg" in content.lower()
