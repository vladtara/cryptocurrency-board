# README UX Redesign Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Restructure the generated README so the 7-day dashboard is the primary analytics block, while longer-horizon windows remain available in a secondary section.

**Architecture:** Keep the existing render contract intact, but extend the pipeline so chart metadata also includes `7D`. Implement the UX change by rendering the `7D` table and `7D` charts together in a dedicated dashboard section, keeping `30D`, `90D`, `180D`, and `1Y` in `Extended Windows`, and keeping the lower BTC/ETH chart sections limited to longer horizons.

**Tech Stack:** Python 3.13, Jinja2, pytest, uv

---

## File Map

| File | Action | Responsibility |
|------|--------|---------------|
| `main.py` | Modify | Generate `7D` chart metadata and artifacts |
| `templates/readme.md` | Modify | Reorder the README and place 7D charts under the weekly dashboard |
| `tests/test_readme.py` | Modify | Verify new section structure, 7D chart placement, and longer-horizon chart filtering |

---

### Task 1: Redesign the README template structure

**Files:**
- Modify: `templates/readme.md`
- Modify: `tests/test_readme.py`

- [ ] **Step 1: Write the failing README structure tests**

Update `tests/test_readme.py` to replace the old multi-window structure assertions with these checks:

```python
def test_render_readme_promotes_seven_day_dashboard() -> None:
    prices = _sample_prices()
    windows = _sample_windows()
    charts = _sample_charts()

    content = render_readme(prices, windows, charts)

    assert "## 7-Day Dashboard" in content
    assert "## Extended Windows" in content
    assert "## Multi-Window Summary" not in content
    assert content.index("## 7-Day Dashboard") < content.index("## Extended Windows")
```

```python
def test_render_readme_places_seven_day_metrics_only_in_dashboard() -> None:
    prices = _sample_prices()
    windows = _sample_windows()
    charts = _sample_charts()

    content = render_readme(prices, windows, charts)

    assert "## 7-Day Dashboard" in content
    assert "### 7D" not in content
    assert "### 30D" in content
    assert "### 1Y" in content
```

```python
def test_render_readme_keeps_existing_sections_after_extended_windows() -> None:
    prices = _sample_prices()
    windows = _sample_windows()
    charts = _sample_charts()

    content = render_readme(prices, windows, charts)

    assert content.index("## Extended Windows") < content.index("## BTC Charts")
    assert content.index("## BTC Charts") < content.index("## ETH Charts")
    assert content.index("## ETH Charts") < content.index("## Deep Stats")
```

- [ ] **Step 2: Run the README tests to verify they fail**

Run:

```bash
uv run pytest tests/test_readme.py -q
```

Expected:
- failure because the template still renders `## Multi-Window Summary`
- failure because `### 7D` still appears inside the general multi-window loop

- [ ] **Step 3: Update the README template to match the approved UX**

Modify `templates/readme.md` so it renders these sections in this order:

```jinja2
## Market Overview
```

```jinja2
## 7-Day Dashboard

{% if "7D" in window_rows %}
| Coin | Min | Max | Avg | Median | Return % | Volatility |
|------|-----|-----|-----|--------|----------|------------|
| **BTC** | ${{ "{:,.2f}".format(window_rows["7D"].BTC.min) }} | ${{ "{:,.2f}".format(window_rows["7D"].BTC.max) }} | ${{ "{:,.2f}".format(window_rows["7D"].BTC.avg) }} | ${{ "{:,.2f}".format(window_rows["7D"].BTC.median) }} | {{ "{:+.1f}".format(window_rows["7D"].BTC.return_pct) }}% | {{ "{:.2f}".format(window_rows["7D"].BTC.volatility) }}% |
| **ETH** | ${{ "{:,.2f}".format(window_rows["7D"].ETH.min) }} | ${{ "{:,.2f}".format(window_rows["7D"].ETH.max) }} | ${{ "{:,.2f}".format(window_rows["7D"].ETH.avg) }} | ${{ "{:,.2f}".format(window_rows["7D"].ETH.median) }} | {{ "{:+.1f}".format(window_rows["7D"].ETH.return_pct) }}% | {{ "{:.2f}".format(window_rows["7D"].ETH.volatility) }}% |
{% endif %}
```

```jinja2
## Extended Windows

{% for window_label, window in window_rows.items() %}
{% if window_label != "7D" %}
### {{ window_label }}

| Coin | Min | Max | Avg | Median | Return % | Volatility |
|------|-----|-----|-----|--------|----------|------------|
| **BTC** | ${{ "{:,.2f}".format(window.BTC.min) }} | ${{ "{:,.2f}".format(window.BTC.max) }} | ${{ "{:,.2f}".format(window.BTC.avg) }} | ${{ "{:,.2f}".format(window.BTC.median) }} | {{ "{:+.1f}".format(window.BTC.return_pct) }}% | {{ "{:.2f}".format(window.BTC.volatility) }}% |
| **ETH** | ${{ "{:,.2f}".format(window.ETH.min) }} | ${{ "{:,.2f}".format(window.ETH.max) }} | ${{ "{:,.2f}".format(window.ETH.avg) }} | ${{ "{:,.2f}".format(window.ETH.median) }} | {{ "{:+.1f}".format(window.ETH.return_pct) }}% | {{ "{:.2f}".format(window.ETH.volatility) }}% |
{% endif %}
{% endfor %}
```

Keep the existing `BTC Charts`, `ETH Charts`, and guarded `Deep Stats` sections after `Extended Windows`.

- [ ] **Step 4: Run the README tests to verify they pass**

Run:

```bash
uv run pytest tests/test_readme.py -q
```

Expected:
- all README tests pass

- [ ] **Step 5: Run the full suite and lint/type checks**

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

- [ ] **Step 6: Commit the UX redesign**

```bash
git add templates/readme.md tests/test_readme.py
git commit -m "feat: promote seven-day dashboard in README"
```

---

## Spec Coverage Check

- `Market Overview` stays first: covered in Task 1, Step 3
- `7-Day Dashboard` becomes the main analytics section: covered in Task 1, Steps 1 and 3
- `Extended Windows` contains only `30D`, `90D`, `180D`, `1Y`: covered in Task 1, Steps 1 and 3
- charts stay below summary tables: covered in Task 1, Steps 1 and 3
- `Deep Stats` remains last and guarded: covered in Task 1, Steps 1 and 3
- no pipeline/data-source changes: preserved by file scope in Task 1

## Placeholder Scan

No `TODO`, `TBD`, deferred placeholders, or vague “handle appropriately” steps remain.

## Type Consistency Check

- `render_readme(prices, windows, charts)` contract remains unchanged
- template input name stays `window_rows`
- `7D`, `30D`, `90D`, `180D`, and `1Y` labels are used consistently throughout the plan
