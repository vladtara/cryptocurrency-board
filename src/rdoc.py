import logging
from datetime import UTC, datetime
from types import SimpleNamespace

from jinja2 import Environment, FileSystemLoader

from src.models import CoinPrice

logger = logging.getLogger(__name__)


def render_readme(
    prices: dict[str, CoinPrice],
    windows: dict[str, dict[str, dict[str, float | str]]],
    charts: dict[str, list[dict[str, str]]],
    template_dir: str = "./templates",
) -> str:
    """Render the README markdown content.

    Args:
        prices: Mapping of coin identifiers to current prices.
        windows: Mapping of window labels to per-coin summary statistics.
        charts: Mapping of coin symbols to chart metadata.
        template_dir: Directory containing the README template.

    Returns:
        Rendered README content.
    """
    environment = Environment(loader=FileSystemLoader(template_dir))
    template = environment.get_template("readme.md")
    coins = [prices["bitcoin"], prices["ethereum"]]
    updated_at = datetime.now(UTC).strftime("%Y-%m-%d %H:%M")
    window_rows = {
        window_label: {
            symbol: SimpleNamespace(**metrics)
            for symbol, metrics in metrics_by_symbol.items()
        }
        for window_label, metrics_by_symbol in windows.items()
    }
    content = template.render(
        coins=coins,
        charts=charts,
        window_rows=window_rows,
        updated_at=updated_at,
    )
    logger.info("Rendered README.md")
    return content
