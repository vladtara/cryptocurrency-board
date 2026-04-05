# Multi-Window Dashboard Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Expand the README dashboard to show 7D, 30D, 90D, 180D, and 1Y statistics for BTC and ETH, plus representative multi-horizon charts.

**Architecture:** Keep the existing CSV-driven pipeline and extend it in place. Add reusable window and metric helpers in the storage layer, generalize chart generation to render named horizons, and update README rendering to consume structured per-window summary data instead of one flat 7-day stats block.

**Tech Stack:** Python 3.13, pandas, pygal, Jinja2, pytest, ruff, uv

---

## File Map

| File | Action | Responsibility |
|------|--------|---------------|
| `src/storage.py` | Modify | Load named windows and compute dashboard metrics |
| `src/charts.py` | Modify | Render charts for requested horizons and output paths |
| `src/readme.py` | Modify | Pass structured window and chart data into the template |
| `main.py` | Modify | Orchestrate multi-window metric computation and multi-chart generation |
| `templates/readme.md` | Modify | Render balanced multi-window dashboard sections |
| `tests/test_storage.py` | Modify | Add coverage for window loading and metric calculations |
| `tests/test_charts.py` | Modify | Add coverage for multi-horizon chart file generation |
| `tests/test_readme.py` | Modify | Add coverage for expanded README layout |

---

### Task 1: Add multi-window storage helpers and metrics

**Files:**
- Modify: `src/storage.py`
- Modify: `tests/test_storage.py`

- [ ] **Step 1: Write the failing tests for named windows and dashboard metrics**

Add these tests to `tests/test_storage.py`:

```python
from pathlib import Path

import pandas as pd

from src.storage import compute_window_metrics, load_named_windows


def test_load_named_windows_returns_requested_ranges(tmp_path: Path) -> None:
    csv_path = tmp_path / "btc.csv"
    pd.DataFrame(
        {
            "date": [f"2026-01-{day:02d}" for day in range(10, 0, -1)],
            "price": [float(value) for value in range(10, 0, -1)],
            "change_24h": [0.0] * 10,
        }
    ).to_csv(csv_path, index=False)

    windows = load_named_windows(
        csv_path,
        {"7D": 7, "30D": 30},
    )

    assert list(windows) == ["7D", "30D"]
    assert len(windows["7D"]) == 7
    assert len(windows["30D"]) == 10


def test_compute_window_metrics_returns_primary_metrics() -> None:
    df = pd.DataFrame(
        {
            "date": [
                "2026-04-05",
                "2026-04-04",
                "2026-04-03",
                "2026-04-02",
            ],
            "price": [110.0, 100.0, 105.0, 95.0],
            "change_24h": [0.0, 0.0, 0.0, 0.0],
        }
    )

    metrics = compute_window_metrics(df)

    assert metrics["min"] == 95.0
    assert metrics["max"] == 110.0
    assert metrics["avg"] == 102.5
    assert metrics["median"] == 102.5
    assert metrics["return_pct"] == pytest.approx(15.7894736842)
    assert metrics["volatility"] >= 0.0


def test_compute_window_metrics_supports_secondary_metrics() -> None:
    df = pd.DataFrame(
        {
            "date": [
                "2026-04-05",
                "2026-04-04",
                "2026-04-03",
                "2026-04-02",
            ],
            "price": [110.0, 100.0, 105.0, 95.0],
            "change_24h": [0.0, 0.0, 0.0, 0.0],
        }
    )

    metrics = compute_window_metrics(df)

    assert "range_pct" in metrics
    assert "drawdown_pct" in metrics
    assert "up_day_ratio" in metrics
    assert "current_streak" in metrics


def test_compute_window_metrics_handles_single_row() -> None:
    df = pd.DataFrame(
        {
            "date": ["2026-04-05"],
            "price": [110.0],
            "change_24h": [0.0],
        }
    )

    metrics = compute_window_metrics(df)

    assert metrics["min"] == 110.0
    assert metrics["max"] == 110.0
    assert metrics["avg"] == 110.0
    assert metrics["median"] == 110.0
    assert metrics["return_pct"] == 0.0
    assert metrics["volatility"] == 0.0
```

- [ ] **Step 2: Run the storage tests to verify they fail**

Run:

```bash
uv run pytest tests/test_storage.py -q
```

Expected:
- failure because `load_named_windows` does not exist
- failure because `compute_window_metrics` does not exist

- [ ] **Step 3: Implement the named window loader and metrics helpers**

Update `src/storage.py` to add these functions:

```python
def load_named_windows(
    filepath: Path,
    windows: dict[str, int],
) -> dict[str, pd.DataFrame]:
    """Load named history windows from newest rows in the CSV."""
    history = load_full_history(filepath)
    return {
        label: history.head(days).copy()
        for label, days in windows.items()
    }


def compute_window_metrics(df: pd.DataFrame) -> dict[str, float | str]:
    """Compute dashboard metrics for a history window."""
    prices = df["price"].astype(float)
    oldest = float(prices.iloc[-1])
    newest = float(prices.iloc[0])
    daily_returns = prices.pct_change(-1).dropna()

    peak = float("-inf")
    max_drawdown = 0.0
    for price in reversed(prices.tolist()):
        peak = max(peak, price)
        drawdown = 0.0 if peak == 0 else (peak - price) / peak * 100
        max_drawdown = max(max_drawdown, drawdown)

    diffs = prices.diff(-1).dropna()
    up_days = float((diffs > 0).sum())
    total_moves = float(len(diffs))

    streak_direction = "flat"
    streak_length = 0
    for move in diffs.tolist():
        direction = "up" if move > 0 else "down" if move < 0 else "flat"
        if streak_length == 0:
            streak_direction = direction
            streak_length = 1
            continue
        if direction == streak_direction:
            streak_length += 1
            continue
        break

    return {
        "min": float(prices.min()),
        "max": float(prices.max()),
        "avg": float(prices.mean()),
        "median": float(prices.median()),
        "return_pct": 0.0 if oldest == 0 else (newest - oldest) / oldest * 100,
        "volatility": 0.0 if daily_returns.empty else float(daily_returns.std() * 100),
        "range_pct": 0.0 if prices.min() == 0 else float((prices.max() - prices.min()) / prices.min() * 100),
        "drawdown_pct": float(max_drawdown),
        "up_day_ratio": 0.0 if total_moves == 0 else float(up_days / total_moves * 100),
        "current_streak": f"{streak_direction}:{streak_length}",
    }
```

- [ ] **Step 4: Run the storage tests to verify they pass**

Run:

```bash
uv run pytest tests/test_storage.py -q
```

Expected:
- all storage tests pass

- [ ] **Step 5: Commit the storage-layer work**

```bash
git add src/storage.py tests/test_storage.py
git commit -m "feat: add multi-window storage metrics"
```

---

### Task 2: Generalize chart generation for named horizons

**Files:**
- Modify: `src/charts.py`
- Modify: `tests/test_charts.py`

- [ ] **Step 1: Write the failing chart test for custom horizon output**

Add this test to `tests/test_charts.py`:

```python
def test_generate_chart_supports_custom_titles_and_horizons(tmp_path: Path) -> None:
    df = pd.DataFrame(
        {
            "date": ["2026-04-01", "2026-04-02", "2026-04-03"],
            "price": [65000.0, 66000.0, 67500.0],
        }
    )
    output = tmp_path / "btc-usd-30d.svg"

    generate_chart(df, "BTC-USD", output, horizon_label="30D")

    content = output.read_text()
    assert "30D Price" in content
    assert output.name == "btc-usd-30d.svg"
```

- [ ] **Step 2: Run the chart tests to verify the new test fails**

Run:

```bash
uv run pytest tests/test_charts.py -q
```

Expected:
- failure because `generate_chart` does not accept `horizon_label`

- [ ] **Step 3: Update chart generation to accept a horizon label**

Modify `src/charts.py`:

```python
def generate_chart(
    df: pd.DataFrame,
    coin: str,
    output_path: Path,
    horizon_label: str,
) -> None:
    """Generate an SVG line chart for the given price data."""
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
        title=f"{horizon_label} Price — {coin}",
        x_title="Date",
        y_title="Price (USD)",
        width=800,
        height=300,
        show_legend=False,
        fill=True,
        style=style,
        js=[],
        dots_size=4,
        show_x_guides=False,
        show_y_guides=True,
    )
```

Keep the current self-contained SVG sanitization logic unchanged.

- [ ] **Step 4: Run the chart tests to verify they pass**

Run:

```bash
uv run pytest tests/test_charts.py -q
```

Expected:
- all chart tests pass

- [ ] **Step 5: Commit the chart changes**

```bash
git add src/charts.py tests/test_charts.py
git commit -m "feat: support multi-horizon chart rendering"
```

---

### Task 3: Expand README rendering model

**Files:**
- Modify: `src/readme.py`
- Modify: `templates/readme.md`
- Modify: `tests/test_readme.py`

- [ ] **Step 1: Write failing README rendering tests for multi-window sections**

Add tests like these to `tests/test_readme.py`:

```python
def test_render_readme_includes_multi_window_headers() -> None:
    prices = {
        "bitcoin": CoinPrice(coin="bitcoin", symbol="BTC", price=67500.0, change_24h=1.2, date=date(2026, 4, 5)),
        "ethereum": CoinPrice(coin="ethereum", symbol="ETH", price=3450.0, change_24h=-0.8, date=date(2026, 4, 5)),
    }
    windows = {
        "7D": {
            "BTC": {"min": 1.0, "max": 2.0, "avg": 1.5, "median": 1.5, "return_pct": 10.0, "volatility": 3.0},
            "ETH": {"min": 1.0, "max": 2.0, "avg": 1.5, "median": 1.5, "return_pct": 10.0, "volatility": 3.0},
        },
        "30D": {
            "BTC": {"min": 1.0, "max": 2.0, "avg": 1.5, "median": 1.5, "return_pct": 10.0, "volatility": 3.0},
            "ETH": {"min": 1.0, "max": 2.0, "avg": 1.5, "median": 1.5, "return_pct": 10.0, "volatility": 3.0},
        },
    }
    charts = {
        "BTC": [{"label": "30D", "path": "./img/btc-usd-30d.svg"}],
        "ETH": [{"label": "30D", "path": "./img/eth-usd-30d.svg"}],
    }

    content = render_readme(prices, windows, charts)

    assert "## Multi-Window Summary" in content
    assert "### 7D" in content
    assert "### 30D" in content
    assert "./img/btc-usd-30d.svg" in content
    assert "./img/eth-usd-30d.svg" in content
```

- [ ] **Step 2: Run the README tests to verify they fail**

Run:

```bash
uv run pytest tests/test_readme.py -q
```

Expected:
- failure because `render_readme` does not accept `windows` and `charts`

- [ ] **Step 3: Update `src/readme.py` to accept structured summary data**

Modify the render function signature:

```python
def render_readme(
    prices: dict[str, CoinPrice],
    windows: dict[str, dict[str, dict[str, float | str]]],
    charts: dict[str, list[dict[str, str]]],
    template_dir: str = "./templates",
) -> str:
```

Convert windows to template-friendly namespaces:

```python
window_rows = {
    window_label: {
        symbol: SimpleNamespace(**metrics)
        for symbol, metrics in metrics_by_symbol.items()
    }
    for window_label, metrics_by_symbol in windows.items()
}
```

Pass `window_rows` and `charts` into the template render call.

- [ ] **Step 4: Replace the README template with the balanced multi-window layout**

Update `templates/readme.md` so it renders:
- `Market Overview`
- `Multi-Window Summary`
- one subsection per window (`### 7D`, `### 30D`, etc.)
- one table per window with:
  - Coin
  - Min
  - Max
  - Avg
  - Median
  - Return %
  - Volatility
- `BTC Charts`
- `ETH Charts`

Use this table row pattern:

```jinja2
| **BTC** | ${{ "{:,.2f}".format(window.BTC.min) }} | ${{ "{:,.2f}".format(window.BTC.max) }} | ${{ "{:,.2f}".format(window.BTC.avg) }} | ${{ "{:,.2f}".format(window.BTC.median) }} | {{ "{:+.1f}".format(window.BTC.return_pct) }}% | {{ "{:.2f}".format(window.BTC.volatility) }}% |
```

- [ ] **Step 5: Run the README tests to verify they pass**

Run:

```bash
uv run pytest tests/test_readme.py -q
```

Expected:
- all README tests pass

- [ ] **Step 6: Commit the rendering-layer changes**

```bash
git add src/readme.py templates/readme.md tests/test_readme.py
git commit -m "feat: render multi-window dashboard summary"
```

---

### Task 4: Update the main pipeline to build all windows and selected charts

**Files:**
- Modify: `main.py`

- [ ] **Step 1: Write the failing orchestration test or smoke assertion**

If `main.py` has no dedicated tests yet, add a focused smoke test to `tests/test_readme.py` or a new `tests/test_main.py` that asserts the new chart filenames and window labels appear in the rendered output when the pipeline inputs are prepared.

Use this target structure:

```python
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
```

- [ ] **Step 2: Run the target test to verify it fails**

Run:

```bash
uv run pytest tests/test_readme.py -q
```

Expected:
- failure because `main.py` still builds one 7D stats block and one chart per coin

- [ ] **Step 3: Update `main.py` to derive named windows and chart metadata**

Refactor the main loop to this shape:

```python
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
```

Inside `run()`:

```python
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
```

Then render:

```python
readme_content = render_readme(prices, window_stats, chart_paths)
```

- [ ] **Step 4: Run the focused test and then the full suite**

Run:

```bash
uv run pytest tests/test_readme.py -q
uv run pytest -q
```

Expected:
- focused test passes
- full suite passes

- [ ] **Step 5: Commit the pipeline changes**

```bash
git add main.py
git commit -m "feat: build multi-window dashboard artifacts"
```

---

### Task 5: Add secondary metrics to a deep-stats section

**Files:**
- Modify: `templates/readme.md`
- Modify: `tests/test_readme.py`

- [ ] **Step 1: Write the failing README test for deep stats**

Add a test asserting the README includes a secondary detail section with `Range %` and `Drawdown %`.

```python
assert "## Deep Stats" in content
assert "Range %" in content
assert "Drawdown %" in content
```

- [ ] **Step 2: Run the README tests to verify the new assertion fails**

Run:

```bash
uv run pytest tests/test_readme.py -q
```

Expected:
- failure because the deep stats section does not exist yet

- [ ] **Step 3: Add the secondary metric section to the template**

Below the chart sections, add:

```jinja2
## Deep Stats

### 1Y

| Coin | Range % | Drawdown % |
|------|---------|------------|
| **BTC** | {{ "{:.1f}".format(windows["1Y"]["BTC"].range_pct) }}% | {{ "{:.1f}".format(windows["1Y"]["BTC"].drawdown_pct) }}% |
| **ETH** | {{ "{:.1f}".format(windows["1Y"]["ETH"].range_pct) }}% | {{ "{:.1f}".format(windows["1Y"]["ETH"].drawdown_pct) }}% |
```

Keep the secondary metrics limited to avoid README sprawl.

- [ ] **Step 4: Run the README tests and full suite**

Run:

```bash
uv run pytest tests/test_readme.py -q
uv run pytest -q
```

Expected:
- all tests pass

- [ ] **Step 5: Commit the deep-stats section**

```bash
git add templates/readme.md tests/test_readme.py
git commit -m "feat: add secondary dashboard metrics"
```

---

### Task 6: Refresh generated artifacts and verify end-to-end output

**Files:**
- Modify: `README.md`
- Modify: `img/btc-usd-30d.svg`
- Modify: `img/btc-usd-180d.svg`
- Modify: `img/btc-usd-1y.svg`
- Modify: `img/eth-usd-30d.svg`
- Modify: `img/eth-usd-180d.svg`
- Modify: `img/eth-usd-1y.svg`

- [ ] **Step 1: Run the pipeline**

Run:

```bash
uv run python main.py
```

Expected:
- README regenerates successfully
- new chart SVGs are written under `img/`
- no logging exceptions

- [ ] **Step 2: Inspect the README output**

Check:

```bash
sed -n '1,260p' README.md
```

Expected:
- market overview still appears first
- all window headings appear
- BTC and ETH chart sections contain multi-horizon image paths
- deep stats section appears once

- [ ] **Step 3: Run the final verification suite**

Run:

```bash
uv run ruff check .
uv run pyright
uv run pytest -q
```

Expected:
- Ruff passes
- Pyright passes
- all tests pass

- [ ] **Step 4: Commit generated dashboard output**

```bash
git add README.md img/ main.py src/ templates/ tests/
git commit -m "feat: expand dashboard with multi-window analytics"
```

---

## Spec Coverage Check

- 7D, 30D, 90D, 180D, and 1Y summary windows: covered in Tasks 1, 3, and 4
- Primary metrics (`min`, `max`, `avg`, `median`, `return %`, `volatility`): covered in Task 1 and rendered in Task 3
- Secondary metrics (`range_pct`, `drawdown_pct`, `up_day_ratio`, `current_streak`): computed in Task 1, surfaced in Task 5
- Balanced README layout: covered in Task 3
- Representative horizon charts: covered in Tasks 2 and 4
- Graceful handling of insufficient history: covered in Task 1 and Task 4
- End-to-end pipeline and artifact refresh: covered in Task 6

## Placeholder Scan

No `TODO`, `TBD`, or deferred “implement later” placeholders remain in the plan. Each task includes exact files, explicit tests, concrete commands, and target code structure.

## Type Consistency Check

- Window metrics are represented consistently as `dict[str, float | str]`
- Window collections are represented consistently as `dict[str, dict[str, dict[str, float | str]]]`
- Chart metadata is represented consistently as `dict[str, list[dict[str, str]]]`
- `generate_chart(..., horizon_label=...)` is used consistently across the plan
