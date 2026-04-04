import logging
from pathlib import Path

import pandas as pd
import pygal
from pygal.style import Style

logger = logging.getLogger(__name__)

COIN_COLORS = {
    "BTC-USD": "#ff8c00",  # orange
    "ETH-USD": "#4a90d9",  # blue
}


def generate_chart(df: pd.DataFrame, coin: str, output_path: Path) -> None:
    """Generate an SVG line chart for the given price data.

    Args:
        df: DataFrame with 'date' and 'price' columns.
        coin: Coin pair name (e.g. "BTC-USD").
        output_path: Path to write the SVG file.
    """
    color = COIN_COLORS.get(coin, "#ff8c00")
    style = Style(
        background="#0d1117",
        plot_background="#0d1117",
        foreground="#c9d1d9",
        foreground_strong="#f0f6fc",
        foreground_subtle="#8b949e",
        colors=(color,),
        font_family="monospace",
    )

    chart = pygal.Line(
        title=f"7 Day Price — {coin}",
        x_title="Date",
        y_title="Price (USD)",
        width=800,
        height=300,
        show_legend=False,
        fill=True,
        style=style,
        css=[],
        js=[],
        dots_size=4,
        show_x_guides=False,
        show_y_guides=True,
    )

    dates = df["date"].tolist()
    prices = df["price"].tolist()

    chart.x_labels = dates
    chart.add(coin, prices)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    chart.render_to_file(str(output_path))
    logger.info("Generated chart: %s", output_path.name)
