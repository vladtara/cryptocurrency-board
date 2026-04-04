import asyncio
import logging
import os
from pathlib import Path

import pandas as pd

from src.api import fetch_prices
from src.charts import generate_chart
from src.models import FetchError
from src.readme import render_readme
from src.storage import append_price, cleanup_zeros, load_history

DATA_DIR = Path("data")
IMG_DIR = Path("img")
COIN_SLUGS = {
    "bitcoin": "btc-usd",
    "ethereum": "eth-usd",
}

logger = logging.getLogger(__name__)


def configure_logging() -> None:
    """Configure INFO-level logging for command-line execution."""
    root_logger = logging.getLogger()
    if not root_logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(
            logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s")
        )
        root_logger.addHandler(handler)
    root_logger.setLevel(logging.INFO)


def compute_stats(df: pd.DataFrame) -> dict[str, float]:
    """Compute summary statistics for a coin history DataFrame."""
    prices = df["price"].astype(float)
    return {
        "high": float(prices.max()),
        "low": float(prices.min()),
        "avg": float(prices.mean()),
    }


async def run() -> None:
    """Fetch prices, update local artifacts, and render the README."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    IMG_DIR.mkdir(parents=True, exist_ok=True)

    api_key = os.getenv("COINGECKO_API_KEY")
    if not api_key:
        raise RuntimeError("COINGECKO_API_KEY environment variable is required")

    prices = await fetch_prices(api_key)
    stats: dict[str, dict[str, float]] = {}

    for coin_id, coin_price in prices.items():
        slug = COIN_SLUGS[coin_id]
        csv_path = DATA_DIR / f"{slug}.csv"
        svg_path = IMG_DIR / f"{slug}.svg"
        pair = slug.upper()

        cleanup_zeros(csv_path)
        append_price(coin_price, csv_path)
        cleanup_zeros(csv_path)

        history = load_history(csv_path, days=7)
        stats[coin_price.symbol] = compute_stats(history)
        generate_chart(history, pair, svg_path)

    readme_content = render_readme(prices, stats)
    Path("README.md").write_text(readme_content, encoding="utf-8")
    logger.info("Wrote README.md")


def main() -> None:
    """Run the async pipeline and exit non-zero on expected failures."""
    configure_logging()
    try:
        asyncio.run(run())
    except FetchError as error:
        logger.error("Price fetch failed: %s", error)
        raise SystemExit(1) from error
    except RuntimeError as error:
        logger.error("%s", error)
        raise SystemExit(1) from error


if __name__ == "__main__":
    main()
