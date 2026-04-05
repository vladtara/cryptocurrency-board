import asyncio
import logging
import os
from pathlib import Path

from src.api import fetch_prices
from src.charts import generate_chart
from src.models import FetchError
from src.readme import render_readme
from src.storage import (
    append_price,
    cleanup_zeros,
    compute_window_metrics,
    load_named_windows,
)

DATA_DIR = Path("data")
IMG_DIR = Path("img")
COIN_SLUGS = {
    "bitcoin": "btc-usd",
    "ethereum": "eth-usd",
}
WINDOWS = {
    "7D": 7,
    "30D": 30,
    "90D": 90,
    "180D": 180,
    "1Y": 365,
}
CHART_WINDOWS = {
    "30D": 30,
    "180D": 180,
    "1Y": 365,
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


async def run() -> None:
    """Fetch prices, update local artifacts, and render the README."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    IMG_DIR.mkdir(parents=True, exist_ok=True)

    api_key = os.getenv("COINGECKO_API_KEY")
    if not api_key:
        raise RuntimeError("COINGECKO_API_KEY environment variable is required")

    prices = await fetch_prices(api_key)
    window_stats: dict[str, dict[str, dict[str, float | str]]] = {
        label: {} for label in WINDOWS
    }
    chart_paths: dict[str, list[dict[str, str]]] = {"BTC": [], "ETH": []}

    for coin_id, coin_price in prices.items():
        slug = COIN_SLUGS[coin_id]
        csv_path = DATA_DIR / f"{slug}.csv"
        pair = slug.upper()

        cleanup_zeros(csv_path)
        append_price(coin_price, csv_path)
        cleanup_zeros(csv_path)

        windows = load_named_windows(csv_path, WINDOWS)
        for label, history in windows.items():
            window_stats[label][coin_price.symbol] = compute_window_metrics(history)

        for label, days in CHART_WINDOWS.items():
            history = windows[label]
            if history.empty:
                continue
            svg_path = IMG_DIR / f"{slug}-{label.lower()}.svg"
            generate_chart(history, pair, svg_path, horizon_label=label)
            chart_paths[coin_price.symbol].append(
                {"label": label, "path": f"./{svg_path.as_posix()}"}
            )

    readme_content = render_readme(prices, window_stats, chart_paths)
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
