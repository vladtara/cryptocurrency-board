# README UX Redesign Spec

Date: 2026-04-05
Project: `cryptocurrency-board`
Scope: Reorganize the generated README so every time horizon is rendered as a self-contained dashboard section, with the 7-day view still appearing first.

## Goal

Make the README easier to scan by giving each time horizon one predictable pattern: heading, table, and matching charts. The current README has the right data, but readers still need to jump between summary tables and lower chart sections. The redesign should make every horizon self-contained while keeping the lower per-coin chart sections and deep stats available below.

## User Problem

The current README answers too many questions at once in the same place:

- current spot price
- short-term weekly behavior
- medium-term windows
- long-term windows

That makes the README feel dense and makes the 7-day dashboard hard to find even though it is likely the default view most readers care about.

## Design Decision

Use this section order:

1. `## Market Overview`
2. `## 7-Day Dashboard`
3. `## 30D Dashboard`
4. `## 90D Dashboard`
5. `## 180D Dashboard`
6. `## 1Y Dashboard`
7. `## BTC Charts`
8. `## ETH Charts`
9. `## Deep Stats`

This keeps the current price snapshot first, then presents every horizon with the same reading pattern, while leaving the lower chart sections as secondary reference blocks.

## Section Behavior

### Market Overview

Keep the existing compact price table:

- coin
- current price
- 24h change

This stays at the top because it is the fastest high-level summary.

### Dashboard Sections

Create one dashboard section for each horizon:

- `7-Day Dashboard`
- `30D Dashboard`
- `90D Dashboard`
- `180D Dashboard`
- `1Y Dashboard`

Each section should contain:

- one compact BTC/ETH metrics table
- one BTC chart for the same horizon
- one ETH chart for the same horizon

The metrics table in every dashboard section should use the same columns:

- Coin
- Min
- Max
- Avg
- Median
- Return %
- Volatility

Mapping:

- `7D` metrics and charts feed `7-Day Dashboard`
- `30D` metrics and charts feed `30D Dashboard`
- `90D` metrics and charts feed `90D Dashboard`
- `180D` metrics and charts feed `180D Dashboard`
- `1Y` metrics and charts feed `1Y Dashboard`

The 7-day section still appears first because it is the default short-term view, but the other horizons should use the same structure for consistency.

### BTC Charts / ETH Charts

Keep the chart sections below the summary tables.

Reason:

- charts are supporting detail, not the first-read information
- this prevents the top of the README from becoming too tall
- users can scan numbers first, then inspect visual trend shapes

The lower chart sections should remain in the README because the user explicitly wants them kept.

They should include all generated chart horizons, including `7D`, even though those same charts also appear inside the dashboard sections. This duplication is intentional in this design.

### Deep Stats

Keep the existing limited deep-stats section:

- only `1Y`
- only `Range %`
- only `Drawdown %`

This section remains last because it is specialist detail.

## Data Mapping

The redesign should reuse the existing render contract, but the pipeline must extend generated chart metadata so it includes `90D`.

Expected template inputs remain:

- `coins`
- `window_rows`
- `charts`
- `updated_at`

Chart metadata requirements:

- BTC chart files:
  - `btc-usd-7d.svg`
  - `btc-usd-30d.svg`
  - `btc-usd-90d.svg`
  - `btc-usd-180d.svg`
  - `btc-usd-1y.svg`
- ETH chart files:
  - `eth-usd-7d.svg`
  - `eth-usd-30d.svg`
  - `eth-usd-90d.svg`
  - `eth-usd-180d.svg`
  - `eth-usd-1y.svg`

`window_rows["1Y"]` continues to feed `Deep Stats` when present.

## Template Constraints

- Keep the README markdown-first and table-driven
- Avoid adding decorative markup or HTML
- Do not duplicate the same metrics table in more than one section
- Keep BTC and ETH as the current explicit coin rows
- Preserve graceful behavior when optional data is missing, especially the guarded `1Y` deep-stats block
- Keep per-horizon section ordering stable: `7D`, `30D`, `90D`, `180D`, `1Y`

## Testing Requirements

Update README rendering and pipeline tests so they verify:

- `## 7-Day Dashboard`, `## 30D Dashboard`, `## 90D Dashboard`, `## 180D Dashboard`, and `## 1Y Dashboard` exist
- each dashboard section contains the matching chart paths for BTC and ETH
- `90D` chart generation now exists in pipeline output
- lower `BTC Charts` and `ETH Charts` sections still render
- `Deep Stats` still renders correctly when `1Y` exists
- `Deep Stats` is still omitted when `1Y` is absent

Tests should focus on rendered output, not just intermediate structures.

## Non-Goals

- No change to fetched data sources
- No new metrics
- No change to the main pipeline beyond what is required to support the README structure
- No visual/browser UI beyond the generated markdown README

## Implementation Impact

Expected implementation should be limited to:

- `main.py`
- `templates/readme.md`
- `tests/test_readme.py`

`src/readme.py` should only change if the template structure reveals a real context-shaping problem.

## Success Criteria

The redesign is successful if:

- a reader can immediately find the weekly dashboard after the market overview
- every horizon can be understood without jumping to another section for its chart
- `90D` charts are generated and rendered
- lower per-coin chart sections remain available as secondary reference blocks
- the README still renders all existing analytics cleanly
- tests continue to pass
