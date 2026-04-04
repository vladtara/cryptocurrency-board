# Cryptocurrency Board Redesign

## Overview

Full rewrite of the cryptocurrency-board project: switch from Blockchain.com to CoinGecko API, replace Matplotlib PNGs with pygal SVG charts, modernize project structure with proper src layout, add comprehensive testing and linting, and upgrade the README dashboard with richer data presentation.

## Goals

1. Reliable price data via CoinGecko free API (replacing unreliable Blockchain.com)
2. Fancy SVG charts rendered natively in GitHub README
3. Python best practices: src layout, tests, linting, type checking, error handling
4. Clean historical data (remove 0.0 entries), keep full valid archive
5. Python 3.14, uv for dependency management

## Project Structure

```
cryptocurrency-board/
├── src/
│   ├── __init__.py
│   ├── api.py          # CoinGecko API client (httpx, async)
│   ├── models.py       # Pydantic models
│   ├── storage.py      # CSV read/write/cleanup logic
│   ├── charts.py       # SVG chart generation (pygal)
│   └── readme.py       # Jinja2 README rendering
├── tests/
│   ├── __init__.py
│   ├── test_api.py
│   ├── test_storage.py
│   ├── test_charts.py
│   └── test_readme.py
├── templates/
│   └── readme.md       # Jinja2 template (upgraded)
├── data/               # CSV files (git-tracked)
├── img/                # Generated SVG charts
├── main.py             # Orchestrator
├── init.py             # CI/Docker wrapper
├── pyproject.toml      # uv, pyright, ruff config
├── Dockerfile          # Python 3.14 + uv
└── .github/workflows/
    ├── cron.yaml       # Daily run at 5:50 UTC
    ├── build.yaml      # Docker image build (renamed from main.yaml)
    └── ci.yaml         # NEW: ruff + pyright + pytest
```

## API Client (`src/api.py`)

Single CoinGecko call fetches both coins at once:

```
GET https://api.coingecko.com/api/v3/simple/price?ids=bitcoin,ethereum&vs_currencies=usd&include_24hr_change=true
```

- Uses `httpx.AsyncClient` with async context manager
- Retry with exponential backoff: 3 attempts (1s, 2s, 4s)
- Returns `dict[str, CoinPrice]`
- Raises `FetchError` on failure — never writes 0.0 to CSV

## Data Models (`src/models.py`)

```python
class CoinPrice(BaseModel):
    coin: str           # "bitcoin" / "ethereum"
    symbol: str         # "BTC" / "ETH"
    price: float
    change_24h: float   # percentage
    date: date
```

## CSV Storage (`src/storage.py`)

- CSV columns: `date,price,change_24h`
- Append new row to top (newest first)
- Keep all valid historical data — no rolling window at write time
- 7-day window applied only at read time for chart generation
- Backward compatible: existing CSVs missing `change_24h` get `NaN` on load
- One-time cleanup function removes rows with `price == 0.0`
- File paths unchanged: `data/btc-usd.csv`, `data/eth-usd.csv`

Functions:
- `append_price(coin_price: CoinPrice, filepath: Path) -> None`
- `load_history(filepath: Path, days: int = 7) -> pd.DataFrame`
- `load_full_history(filepath: Path) -> pd.DataFrame`
- `cleanup_zeros(filepath: Path) -> None`

## SVG Charts (`src/charts.py`)

Library: `pygal` — purpose-built SVG charting, no JS (GitHub-safe), clean output.

Chart style:
- Dark theme with background `#0d1117` (GitHub dark mode)
- Line chart with filled area under curve
- BTC in orange, ETH in blue
- Price labels on data points
- Min/max annotations
- Dimensions: 800x300
- X-axis: dates, Y-axis: USD price

Output: `img/btc-usd.svg`, `img/eth-usd.svg`

Function:
```python
def generate_chart(df: pd.DataFrame, coin: str, output_path: Path) -> None
```

## README Dashboard (`src/readme.py` + `templates/readme.md`)

Template layout:

```markdown
# Cryptocurrency Board

> Last updated: 2026-04-05 05:50 UTC

## Market Overview

| Coin | Price (USD) | 24h Change |
|------|-------------|------------|
| BTC  | $67,500.00  | ▲ +1.2%    |
| ETH  | $3,450.00   | ▼ -0.8%    |

## BTC — 7 Day Chart
![BTC chart](./img/btc-usd.svg)

## ETH — 7 Day Chart
![ETH chart](./img/eth-usd.svg)

## 7-Day Summary
| Coin | High | Low | Avg |
|------|------|-----|-----|
| BTC  | ...  | ... | ... |
| ETH  | ...  | ... | ... |
```

Features:
- Timestamp showing last refresh
- 24h change with green ▲ / red ▼ directional arrows
- Prices formatted with commas and 2 decimal places
- 7-day summary stats (high, low, average)
- SVG charts instead of PNGs
- No installation/contributing boilerplate

## Error Handling & Logging

- `FetchError` custom exception in `src/api.py`
- Retry 3x with exponential backoff (1s, 2s, 4s)
- Price validation: reject `price <= 0`
- Top-level try/except in `main.py` — log error, exit non-zero (so GitHub Action fails visibly)
- `logging` stdlib throughout, structured messages
- `init.py` retains its existing logging pattern

## Testing (`pytest`)

- `test_api.py` — mock httpx responses, test parsing, retry behavior, error handling
- `test_storage.py` — append, load with days param, zero cleanup, missing file
- `test_charts.py` — SVG generation, expected elements present
- `test_readme.py` — template renders correctly with sample data

## CI/CD

**`.github/workflows/ci.yaml`** (new):
- Triggers: PRs and pushes to master
- Steps: `uv sync` -> `ruff check` -> `ruff format --check` -> `pyright` -> `pytest`

**`.github/workflows/build.yaml`** (renamed from `main.yaml`):
- Trigger: push to master when `init.py`, `Dockerfile`, `pyproject.toml`, or `uv.lock` change
- Updated for Python 3.14

**`.github/workflows/cron.yaml`**:
- Unchanged pattern, daily at 5:50 UTC

**Dockerfile:**
- Base image: `python:3.14-alpine`
- Install `uv` via pip or copy from official image
- Copy `pyproject.toml` + `uv.lock` instead of `requirements.txt`
- Dependency install via `uv sync --frozen`

## Dependency Changes

**Add:**
- `pygal` — SVG chart generation
- `ruff` (dev) — linting and formatting
- `pytest` (dev) — testing

**Remove:**
- `aiohttp` — replaced by `httpx`
- `matplotlib` — replaced by `pygal`
- `pendulum` — replaced by `datetime.date.today()`

**Keep:**
- `httpx`, `pandas`, `Jinja2`, `pydantic`, `gitpython`

**Remove file:**
- `requirements.txt` — replaced by `pyproject.toml` + `uv.lock`

## Configuration Updates

**`pyproject.toml`:**
- `requires-python = ">=3.14"`
- Add `[tool.ruff]` section: rules `E`, `F`, `W`, `I`, `UP`
- Add `[tool.ruff.format]` section
- Dev dependencies: `ruff`, `pytest`

**`.python-version`:** `3.14`

## Migration Steps

1. Run `cleanup_zeros()` on both CSVs to remove 0.0 entries
2. Add `change_24h` column handling for backward compatibility
3. Swap chart file extensions from `.png` to `.svg` in template
4. Update CLAUDE.md to reflect new structure and commands
