import logging
from datetime import datetime, timezone
from types import SimpleNamespace
from typing import Any

from jinja2 import Environment, FileSystemLoader

from src.models import CoinPrice

logger = logging.getLogger(__name__)


def render_readme(
    prices: dict[str, CoinPrice],
    stats: dict[str, dict[str, float]],
    template_dir: str = "./templates",
) -> str:
    """Render the README markdown content.

    Args:
        prices: Mapping of coin identifiers to current prices.
        stats: Mapping of coin symbols to summary statistics.
        template_dir: Directory containing the README template.

    Returns:
        Rendered README content.
    """
    environment = Environment(loader=FileSystemLoader(template_dir))
    template = environment.get_template("readme.md")
    coins = [prices["bitcoin"], prices["ethereum"]]
    updated_at = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M")
    summary_stats = {
        symbol: SimpleNamespace(**values) for symbol, values in stats.items()
    }
    content = template.render(
        coins=coins,
        stats=summary_stats,
        updated_at=updated_at,
    )
    logger.info("Rendered README.md")
    return content
