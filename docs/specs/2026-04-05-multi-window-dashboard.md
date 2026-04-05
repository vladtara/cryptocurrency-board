# Multi-Window Dashboard Expansion

## Overview

Expand the README dashboard beyond the current 7-day view to support 30-day, 90-day, 180-day, and 1-year analysis while keeping the page readable in GitHub markdown.

The design direction is a balanced layout:
- Keep the current market overview at the top
- Add a shared multi-window summary section
- Keep separate BTC and ETH chart sections
- Show deeper statistics without turning the README into a research report

## Goals

1. Surface longer-term trends directly in the README
2. Preserve readability on GitHub desktop and mobile
3. Reuse the existing CSV history instead of introducing a database or new storage layer
4. Add richer statistics that are useful, not noisy
5. Keep implementation incremental and testable

## Scope

### In Scope

- Add summary windows for:
  - 7D
  - 30D
  - 90D
  - 180D
  - 1Y
- Compute metrics for each coin and window
- Update README rendering and template structure
- Generate additional charts or chart groupings as needed for the new sections
- Add tests for metric computation and README rendering

### Out of Scope

- Interactive charts
- External analytics services
- Intraday price tracking
- More than BTC and ETH
- Financial advice or predictive modeling

## Data Model

The CSV source remains the same:

`date,price,change_24h`

The current pipeline already keeps full history, which is sufficient for all requested windows. The implementation should derive each time window by reading the same CSV and slicing the latest `N` rows.

Required window sizes:
- 7 days
- 30 days
- 90 days
- 180 days
- 365 days

If a file contains fewer rows than the requested window, the system should compute stats on available rows and render the result normally. No section should fail solely because full historical depth is not yet available.

## Statistics

### Primary Metrics

These should appear by default in the main multi-window summary:

- `min`
- `max`
- `avg`
- `median`
- `return_pct`
- `volatility`

Definitions:

- `min`: minimum price in the selected window
- `max`: maximum price in the selected window
- `avg`: arithmetic mean of prices in the window
- `median`: median of prices in the window
- `return_pct`: percent change from oldest price in the window to newest price in the window
- `volatility`: standard deviation of daily returns within the window, rendered as a percentage

### Secondary Metrics

These should be supported as implementation-ready helpers even if they do not all appear in the first main summary table:

- `range_pct`
- `drawdown_pct`
- `up_day_ratio`
- `current_streak`

Definitions:

- `range_pct`: `(max - min) / min * 100`
- `drawdown_pct`: drop from the peak price within the window to the lowest subsequent price in the same window
- `up_day_ratio`: percentage of day-over-day price moves that are positive
- `current_streak`: consecutive up or down days ending at the most recent row

Recommendation:
- Show `range_pct` and `drawdown_pct` in a secondary detail section if space allows
- Keep `up_day_ratio` and `current_streak` available for future README expansion or tests

## README Layout

### Section Order

1. `Market Overview`
2. `Multi-Window Summary`
3. `BTC Charts`
4. `ETH Charts`
5. `Extended Notes` or `Deep Stats` if needed

### Market Overview

Preserve the current top summary table:

- Coin
- Price (USD)
- 24h Change

This remains the entry point and should not become crowded with longer-horizon statistics.

### Multi-Window Summary

Add a new summary section comparing BTC and ETH across windows.

Recommended structure:

- One subsection per time window
- Inside each subsection, one row for BTC and one row for ETH
- Columns:
  - Coin
  - Min
  - Max
  - Avg
  - Median
  - Return %
  - Volatility

Rationale:
- A single giant table with all windows as grouped columns is harder to read in markdown
- Window-first subsections are easier to scan on GitHub and mobile
- This still matches the selected “balanced” layout

### Chart Sections

Keep separate chart sections for BTC and ETH.

Recommended chart strategy:
- Continue showing a prominent short-term chart for each coin
- Add additional charts for medium and long horizons in a controlled way

Default recommendation:
- BTC:
  - 30D chart
  - 180D chart
  - 1Y chart
- ETH:
  - 30D chart
  - 180D chart
  - 1Y chart

Do not render five charts per coin in the README by default. That is too long. Instead:
- Use the summary tables for all five windows
- Use charts for representative horizons:
  - short (`30D`)
  - medium (`180D`)
  - long (`1Y`)

If a 7D chart is still desired, it can replace 30D or be retained as the “short” chart, but the default design should avoid more than three charts per coin.

## Chart Generation

The chart generation layer should be generalized so it can render a requested window rather than only a fixed 7-day slice.

Recommended output naming:

- `img/btc-usd-30d.svg`
- `img/btc-usd-180d.svg`
- `img/btc-usd-1y.svg`
- `img/eth-usd-30d.svg`
- `img/eth-usd-180d.svg`
- `img/eth-usd-1y.svg`

Chart style should remain visually consistent with the current SVG design:
- dark background
- BTC orange
- ETH blue
- self-contained SVG compatible with GitHub README rendering

## Application Flow Changes

### Main Orchestration

`main.py` should change from computing one stat block and one chart per coin to:

- load full history per coin
- derive the required time windows
- compute metric bundles per window
- render multiple charts for selected horizons
- pass structured summary data into README rendering

### Storage Helpers

`src/storage.py` should expose window-oriented loading in a way that avoids repeated ad hoc slicing in `main.py`.

Acceptable options:
- keep `load_history(filepath, days=N)` and call it for each window
- add a helper that returns a mapping of named windows to data frames

Recommendation:
- add a helper returning named windows so the orchestration code stays clear and less repetitive

## Rendering Model

`src/readme.py` should stop assuming a single flat stats mapping keyed only by coin symbol.

Recommended render context:

- `coins`
- `updated_at`
- `windows`

Where `windows` is shaped conceptually like:

```python
{
    "7D": {
        "BTC": {...metrics...},
        "ETH": {...metrics...},
    },
    "30D": {
        "BTC": {...metrics...},
        "ETH": {...metrics...},
    },
}
```

And chart metadata is passed separately, for example:

```python
{
    "BTC": [
        {"label": "30D", "path": "./img/btc-usd-30d.svg"},
        {"label": "180D", "path": "./img/btc-usd-180d.svg"},
        {"label": "1Y", "path": "./img/btc-usd-1y.svg"},
    ],
    "ETH": [...],
}
```

## Error Handling

- If a window has insufficient history, render available stats from the rows that exist
- If a chart cannot be generated due to empty data, omit that chart and log a warning
- README generation should not fail because one longer window is not yet populated in a newer repository

## Testing Strategy

### Unit Tests

- metric computation for each primary metric
- edge cases:
  - one-row windows
  - flat price series
  - only up days
  - only down days
  - insufficient history

### Rendering Tests

- README template renders all target window headers
- README includes representative chart paths
- formatting of percentages and currency values remains stable

### Chart Tests

- requested window-specific charts are generated to the expected file paths
- SVG remains self-contained and styled

## Tradeoffs

### Chosen Direction

Balanced sections.

Why:
- clearer than a giant matrix table
- shorter than a coin-first deep-dive dashboard
- keeps the README homepage useful as a quick scan

### Rejected Alternative: One Mega Table

Not chosen because:
- hard to read in markdown
- poor mobile scanning
- grouped columns become visually noisy

### Rejected Alternative: Full Per-Coin Analytics Report

Not chosen because:
- too long for a repository homepage
- duplicates structural elements for BTC and ETH
- makes summary comparison slower

## Success Criteria

- README shows 7D, 30D, 90D, 180D, and 1Y stats for BTC and ETH
- Main summary includes min, max, avg, median, return %, and volatility
- Charts show short, medium, and long horizons without bloating the page
- Output remains readable in GitHub markdown
- Existing pipeline still runs in CI and Docker
- Tests cover the new metric and rendering behavior
