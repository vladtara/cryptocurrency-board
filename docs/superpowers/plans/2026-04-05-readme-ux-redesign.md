# README UX Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Restructure the generated README so every horizon is a self-contained dashboard section with its own table and matching charts, while keeping the lower BTC/ETH chart sections and deep stats.

**Architecture:** Keep the existing render contract intact and extend the pipeline chart metadata so it also generates `90D` charts. Implement the UX change in `main.py`, `templates/readme.md`, and `tests/test_readme.py` by replacing the current weekly-plus-extended split with five repeated dashboard sections: `7D`, `30D`, `90D`, `180D`, and `1Y`.

**Tech Stack:** Python 3.13, Jinja2, pytest, ruff, pyright, uv

---

## File Map

| File | Action | Responsibility |
|------|--------|---------------|
| `main.py` | Modify | Generate `90D` chart metadata and artifact paths in addition to existing horizons |
| `templates/readme.md` | Modify | Render one dashboard section per horizon with table plus BTC/ETH charts |
| `tests/test_readme.py` | Modify | Verify section layout, per-horizon chart placement, and pipeline chart generation |

---

### Task 1: Extend pipeline chart generation to include 90D

**Files:**
- Modify: `main.py`
- Modify: `tests/test_readme.py`

- [ ] **Step 1: Write the failing pipeline test update**

Update the pipeline smoke test in `tests/test_readme.py` so it expects `90D` chart generation and `90D` chart metadata.

Replace the current rendered output assertions with:

```python
    assert "## 7-Day Dashboard" in rendered
    assert "## 30D Dashboard" in rendered
    assert "## 90D Dashboard" in rendered
    assert "## 180D Dashboard" in rendered
    assert "## 1Y Dashboard" in rendered
```

Add expected chart paths in rendered output:

```python
    assert "./img/btc-usd-90d.svg" in rendered
    assert "./img/eth-usd-90d.svg" in rendered
```

Add expected `generate_chart` calls:

```python
        {
            "coin": "BTC-USD",
            "path": "./img/btc-usd-90d.svg",
            "horizon_label": "90D",
            "rows": "2",
        },
```

```python
        {
            "coin": "ETH-USD",
            "path": "./img/eth-usd-90d.svg",
            "horizon_label": "90D",
            "rows": "2",
        },
```

Update the chart-label assertion to:

```python
    assert {call["horizon_label"] for call in chart_calls} == {
        "7D",
        "30D",
        "90D",
        "180D",
        "1Y",
    }
```

Update the expected `captured["charts"]` payload to include `90D` for both BTC and ETH.

- [ ] **Step 2: Run the README tests to verify they fail**

Run:

```bash
uv run pytest tests/test_readme.py -q
```

Expected:
- failure because `main.py` does not currently generate `90D` chart metadata
- failure because the template does not currently render `90D` as a dashboard section

- [ ] **Step 3: Update `main.py` to generate 90D chart metadata**

Modify `CHART_WINDOWS` in `main.py` to include `90D`:

```python
CHART_WINDOWS = {
    "7D": 7,
    "30D": 30,
    "90D": 90,
    "180D": 180,
    "1Y": 365,
}
```

Keep the existing loop shape so `generate_chart(...)` and `chart_paths` automatically include `90D`.

- [ ] **Step 4: Run the README tests to verify the pipeline change is enough for test progress**

Run:

```bash
uv run pytest tests/test_readme.py -q
```

Expected:
- fewer failures, but template-structure assertions still fail until Task 2 is complete

- [ ] **Step 5: Commit the pipeline chart update**

```bash
git add main.py tests/test_readme.py
git commit -m "feat: add ninety-day dashboard charts"
```

---

### Task 2: Replace the README structure with one dashboard section per horizon

**Files:**
- Modify: `templates/readme.md`
- Modify: `tests/test_readme.py`

- [ ] **Step 1: Write the failing structure tests for per-horizon sections**

Add or update README rendering tests in `tests/test_readme.py` to verify:

```python
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
```

```python
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
```

```python
def test_render_readme_keeps_lower_chart_sections() -> None:
    prices = _sample_prices()
    windows = _sample_windows()
    charts = _sample_charts()

    content = render_readme(prices, windows, charts)

    assert "## BTC Charts" in content
    assert "## ETH Charts" in content
    assert content.index("## 1Y Dashboard") < content.index("## BTC Charts")
```

- [ ] **Step 2: Expand the sample chart fixture**

Update `_sample_charts()` in `tests/test_readme.py` so it contains all horizons:

```python
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
```

- [ ] **Step 3: Update the sample windows fixture**

Extend `_sample_windows()` in `tests/test_readme.py` to include `90D` and `180D`, preserving the existing `7D`, `30D`, and `1Y` shapes:

```python
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
```

```python
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
```

- [ ] **Step 4: Update the template to render one section per horizon**

Replace the current `7-Day Dashboard` plus `Extended Windows` structure in `templates/readme.md` with explicit dashboard sections:

```jinja2
## 7-Day Dashboard
{% if "7D" in window_rows %}
| Coin | Min | Max | Avg | Median | Return % | Volatility |
|------|-----|-----|-----|--------|----------|------------|
| **BTC** | ${{ "{:,.2f}".format(window_rows["7D"].BTC.min) }} | ${{ "{:,.2f}".format(window_rows["7D"].BTC.max) }} | ${{ "{:,.2f}".format(window_rows["7D"].BTC.avg) }} | ${{ "{:,.2f}".format(window_rows["7D"].BTC.median) }} | {{ "{:+.1f}".format(window_rows["7D"].BTC.return_pct) }}% | {{ "{:.2f}".format(window_rows["7D"].BTC.volatility) }}% |
| **ETH** | ${{ "{:,.2f}".format(window_rows["7D"].ETH.min) }} | ${{ "{:,.2f}".format(window_rows["7D"].ETH.max) }} | ${{ "{:,.2f}".format(window_rows["7D"].ETH.avg) }} | ${{ "{:,.2f}".format(window_rows["7D"].ETH.median) }} | {{ "{:+.1f}".format(window_rows["7D"].ETH.return_pct) }}% | {{ "{:.2f}".format(window_rows["7D"].ETH.volatility) }}% |

![BTC 7D chart](./img/btc-usd-7d.svg)

![ETH 7D chart](./img/eth-usd-7d.svg)
{% endif %}
```

Repeat the same pattern for:

- `## 30D Dashboard` using `window_rows["30D"]`
- `## 90D Dashboard` using `window_rows["90D"]`
- `## 180D Dashboard` using `window_rows["180D"]`
- `## 1Y Dashboard` using `window_rows["1Y"]`

with matching chart paths:

- `./img/btc-usd-30d.svg`
- `./img/eth-usd-30d.svg`
- `./img/btc-usd-90d.svg`
- `./img/eth-usd-90d.svg`
- `./img/btc-usd-180d.svg`
- `./img/eth-usd-180d.svg`
- `./img/btc-usd-1y.svg`
- `./img/eth-usd-1y.svg`

Keep the lower `## BTC Charts`, `## ETH Charts`, and guarded `## Deep Stats` sections after the dashboard sections.

- [ ] **Step 5: Run the README tests to verify they pass**

Run:

```bash
uv run pytest tests/test_readme.py -q
```

Expected:
- all README tests pass

- [ ] **Step 6: Commit the template and test redesign**

```bash
git add templates/readme.md tests/test_readme.py
git commit -m "feat: render per-window dashboard sections"
```

---

### Task 3: Refresh generated artifacts and run final verification

**Files:**
- Modify: `README.md`
- Modify: `data/btc-usd.csv`
- Modify: `data/eth-usd.csv`
- Create/Modify: `img/btc-usd-7d.svg`
- Create/Modify: `img/btc-usd-30d.svg`
- Create/Modify: `img/btc-usd-90d.svg`
- Create/Modify: `img/btc-usd-180d.svg`
- Create/Modify: `img/btc-usd-1y.svg`
- Create/Modify: `img/eth-usd-7d.svg`
- Create/Modify: `img/eth-usd-30d.svg`
- Create/Modify: `img/eth-usd-90d.svg`
- Create/Modify: `img/eth-usd-180d.svg`
- Create/Modify: `img/eth-usd-1y.svg`

- [ ] **Step 1: Run the pipeline**

Run:

```bash
set -a && source .env && set +a && uv run python main.py
```

Expected:
- `README.md` regenerates successfully
- `btc-usd-90d.svg` and `eth-usd-90d.svg` are created
- all existing horizon charts are refreshed

- [ ] **Step 2: Inspect the rendered README**

Run:

```bash
sed -n '1,260p' README.md
```

Expected:
- `Market Overview` appears first
- `7-Day Dashboard`, `30D Dashboard`, `90D Dashboard`, `180D Dashboard`, and `1Y Dashboard` all appear
- each dashboard section contains its matching BTC and ETH chart
- lower `BTC Charts` and `ETH Charts` sections still appear

- [ ] **Step 3: Run final verification**

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

- [ ] **Step 4: Commit the refreshed output**

```bash
git add README.md data/btc-usd.csv data/eth-usd.csv img/ main.py templates/readme.md tests/test_readme.py
git commit -m "feat: embed per-window charts in README dashboards"
```

---

## Spec Coverage Check

- every horizon gets its own section with table plus charts: covered in Task 2
- `90D` chart generation added: covered in Task 1
- lower `BTC Charts` and `ETH Charts` remain: covered in Task 2
- `Deep Stats` remains unchanged: preserved in Task 2
- regenerated README and chart artifacts: covered in Task 3

## Placeholder Scan

No `TODO`, `TBD`, or vague implementation steps remain.

## Type Consistency Check

- `window_rows` remains the template input for metrics
- `charts` remains the template input for chart metadata
- horizon labels `7D`, `30D`, `90D`, `180D`, `1Y` are used consistently in tests, template, and pipeline
