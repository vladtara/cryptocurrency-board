# README UX Redesign Spec

Date: 2026-04-05
Project: `cryptocurrency-board`
Scope: Reorganize the generated README so the 7-day view is the primary dashboard while preserving the broader multi-window analytics.

## Goal

Make the README easier to scan by giving the 7-day dashboard clear visual priority. The current README has the right data, but the short-term view is buried inside a multi-window block. The redesign should make the weekly snapshot the main analytical section while keeping longer-horizon windows, charts, and deep stats available below it.

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
3. `## Extended Windows`
4. `## BTC Charts`
5. `## ETH Charts`
6. `## Deep Stats`

This keeps the current price snapshot first, then promotes the 7-day dashboard to the main decision block, then moves longer-horizon summaries into a secondary section.

## Section Behavior

### Market Overview

Keep the existing compact price table:

- coin
- current price
- 24h change

This stays at the top because it is the fastest high-level summary.

### 7-Day Dashboard

Create a dedicated weekly analytics section immediately after Market Overview.

It should contain:

- one compact table
- one row for BTC
- one row for ETH

Columns:

- Coin
- Min
- Max
- Avg
- Median
- Return %
- Volatility

This section should use the existing `7D` metrics already computed by the pipeline. It should not include charts. The intent is a fast numeric weekly dashboard, not a visual block.
This section should also render the 7-day BTC and ETH charts directly below the table so the weekly view is self-contained.

### Extended Windows

Create a section for longer-horizon summaries only.

It should contain subsections for:

- `30D`
- `90D`
- `180D`
- `1Y`

Each subsection should keep the same table structure already used for the multi-window summary:

- Coin
- Min
- Max
- Avg
- Median
- Return %
- Volatility

The `7D` subsection must be removed from this section because it now has its own dedicated dashboard above.

### BTC Charts / ETH Charts

Keep the chart sections below the summary tables.

Reason:

- charts are supporting detail, not the first-read information
- this prevents the top of the README from becoming too tall
- users can scan numbers first, then inspect visual trend shapes

The lower chart sections should continue to show the longer-horizon charts only. The 7-day charts belong directly under `7-Day Dashboard`, not in the lower per-coin chart sections.

### Deep Stats

Keep the existing limited deep-stats section:

- only `1Y`
- only `Range %`
- only `Drawdown %`

This section remains last because it is specialist detail.

## Data Mapping

The redesign should reuse the existing render contract and avoid changing the pipeline shape unless implementation reveals a gap.

Expected template inputs remain:

- `coins`
- `window_rows`
- `charts`
- `updated_at`

Mapping rules:

- `window_rows["7D"]` feeds `7-Day Dashboard`
- `window_rows["30D"]`, `window_rows["90D"]`, `window_rows["180D"]`, and `window_rows["1Y"]` feed `Extended Windows`
- `window_rows["1Y"]` continues to feed `Deep Stats` when present

## Template Constraints

- Keep the README markdown-first and table-driven
- Avoid adding decorative markup or HTML
- Do not duplicate the same `7D` table in more than one section
- Keep BTC and ETH as the current explicit coin rows
- Preserve graceful behavior when optional data is missing, especially the guarded `1Y` deep-stats block

## Testing Requirements

Update README rendering tests so they verify:

- `## 7-Day Dashboard` exists
- `## Extended Windows` exists
- `### 7D` no longer appears under the extended windows area
- `30D`, `90D`, `180D`, and `1Y` still render in the longer-horizon section
- `Deep Stats` still renders correctly when `1Y` exists
- `Deep Stats` is still omitted when `1Y` is absent

Tests should focus on rendered output, not just intermediate structures.

## Non-Goals

- No change to fetched data sources
- No new metrics
- No new metrics
- No change to the main pipeline beyond what is required to support the README structure
- No visual/browser UI beyond the generated markdown README

## Implementation Impact

Expected implementation should be limited to:

- `templates/readme.md`
- `tests/test_readme.py`

`src/readme.py` should only change if the template structure reveals a real context-shaping problem.

## Success Criteria

The redesign is successful if:

- a reader can immediately find the weekly dashboard after the market overview
- the 7-day table is no longer buried inside a larger summary block
- longer-horizon analytics remain available but visually secondary
- the README still renders all existing analytics cleanly
- tests continue to pass
