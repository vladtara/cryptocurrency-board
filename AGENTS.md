# AGENTS.md

This file provides guidance to Codex (Codex.ai/code) when working with code in this repository.

## Project Overview

Automated cryptocurrency price monitoring system. Fetches BTC and ETH prices from the Blockchain.com API daily, maintains 7-day rolling CSV history, generates Matplotlib charts, and renders a README with current prices via Jinja2. Runs daily at 5:50 AM UTC via GitHub Actions cron job in Docker.

## Build & Run

```bash
uv sync --all-extras

# Run the main pipeline (fetch prices, update CSVs, generate charts, render README)
uv run python main.py

# Run with git automation (clone repo to /tmp/update, run main.py, commit and push)
python init.py
```

Docker (used in CI):

```bash
docker build -t cryptocurrency-board .
docker run --env GITHUB_REPO_URL="..." --env GITHUB_USERNAME="..." --env GITHUB_EMAIL="..." cryptocurrency-board
```

No formal test suite. `test.ipynb` is used for manual/exploratory validation.

## Architecture

**Data pipeline**: `main.py` drives the entire flow sequentially:

1. Async fetch via aiohttp → Blockchain.com API (`price_24h` field)
2. Pydantic `Data` model validates response (date + price)
3. Pandas appends to CSV, keeps last 7 entries (rolling window)
4. Matplotlib generates chart PNGs to `img/`
5. Jinja2 renders `templates/readme.md` → `README.md` with current prices

**Deployment model**: The Docker image only contains `init.py` and dependencies. At runtime, `init.py` clones the full repo to `/tmp/update`, runs `main.py` from there, then commits and pushes changes back. This means `main.py` changes take effect without rebuilding the Docker image. The image only rebuilds when `init.py` or `Dockerfile` change (see `.github/workflows/main.yaml`).

**CI/CD** (two workflows):

- `cron.yaml` — daily scheduled run using the pre-built container image from GHCR
- `main.yaml` — rebuilds and pushes Docker image to `ghcr.io` only when `init.py` or `Dockerfile` change on master

## Code Conventions

- PEP 8, 4-space indentation
- Full type annotations on function signatures
- Google-style docstrings with Args/Returns sections
- Async context managers for HTTP sessions
- Commit messages: `Duty Updates YYYY-MM-DD`

## Environment Variables (for init.py / CI)

- `GITHUB_REPO_URL` — Repository URL with embedded auth token
- `GITHUB_USERNAME` — Git commit author name
- `GITHUB_EMAIL` — Git commit author email

## API

- Endpoint: `https://api.blockchain.com/v3/exchange/tickers/{symbol}`
- Symbols: `BTC-USD`, `ETH-USD`
- Response field used: `price_24h`
  Automated cryptocurrency price tracking and visualization system. Fetches BTC and ETH prices daily, stores historical data in CSV, generates 7-day price charts, dynamically renders README.md via Jinja2 templates, and auto-commits/pushes updates to GitHub.

## Commands

### Run locally

```bash
uv run python main.py
```

### Run via Docker (automated/scheduled mode)

```bash
docker build -t cryptocurrency-board .
docker run -e GITHUB_REPO_URL=... -e GITHUB_USERNAME=... -e GITHUB_EMAIL=... cryptocurrency-board
```

### Type checking

```bash
uv run pyright
```

### Install dependencies

```bash
uv sync
```

## Architecture

### Entry Points

- **`main.py`** — Primary local execution script. Fetches prices via `fetchv2()` from Blockchain.com Exchange API, appends to CSV, generates charts with Matplotlib, and renders README from Jinja2 template.
- **`init.py`** — CI/Docker wrapper. Clones/pulls the repo, runs `main.py`, then stages, commits ("Duty Updates YYYY-MM-DD"), and pushes results.

### Source Modules (`src/`)

- **`src/read.py`** — Reusable `Read` class wrapping httpx for fetching price data with error handling.
- **`src/main.py`** — Alternative implementation using `Read` class and CoinGecko API.

### Data Flow

1. Fetch prices from API → 2. Append to `data/{btc,eth}-usd.csv` → 3. Load last 7 days → 4. Generate charts to `img/{btc,eth}-usd.png` → 5. Render `templates/readme.md` → `README.md`

### Key Directories

- `data/` — CSV price history files
- `img/` — Generated chart PNGs
- `templates/` — Jinja2 template for README

## Configuration

- **Package management**: `uv` (replaces former `requirements.txt`)
- **Python version**: 3.14 (`.python-version`)
- **Type checking**: Pyright in standard mode (see `pyproject.toml [tool.pyright]`)
- **Docker**: `python:3.14-slim` image, entrypoint is `init.py`

## APIs

- **Blockchain.com Exchange API**: `https://api.blockchain.com/v3/exchange/tickers/` — used in `main.py`
- **CoinGecko API**: `https://api.coingecko.com/api/v3/simple/price` — used in `src/main.py`
