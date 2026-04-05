# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Automated cryptocurrency price monitoring system. Fetches BTC and ETH prices from CoinGecko API daily, stores full historical data in CSV, generates pygal SVG charts (7-day window), and renders a README dashboard via Jinja2. Runs daily at 5:50 AM UTC via GitHub Actions cron job in Docker.

## Commands

### Run locally
```bash
uv run python main.py
```

### Run via Docker (CI/scheduled mode)
```bash
docker build -t cryptocurrency-board .
docker run -e GITHUB_REPO_URL=... -e GITHUB_USERNAME=... -e GITHUB_EMAIL=... -e COINGECKO_API_KEY=... cryptocurrency-board
```

### Run tests
```bash
uv run pytest -v
```

### Lint and format
```bash
uv run ruff check .
uv run ruff format --check .
```

### Type checking
```bash
uv run pyright
```

### Install dependencies
```bash
uv sync --all-extras
```

## Architecture

### Entry Points

- **`main.py`** — Orchestrator. Fetches prices via `src/api.py`, appends to CSV via `src/storage.py`, generates SVG charts via `src/charts.py`, renders README via `src/readme.py`.
- **`init.py`** — CI/Docker wrapper. Clones/pulls the repo, runs `main.py`, commits ("Duty Updates YYYY-MM-DD"), and pushes.

### Source Modules (`src/`)

- **`src/models.py`** — Pydantic `CoinPrice` model, `FetchError` exception
- **`src/api.py`** — CoinGecko async client (httpx), retry with backoff
- **`src/storage.py`** — CSV append, load (with day window), cleanup
- **`src/charts.py`** — Pygal SVG chart generation, dark theme
- **`src/readme.py`** — Jinja2 README rendering

### Data Flow

1. Fetch prices from CoinGecko API → 2. Append to `data/{btc,eth}-usd.csv` → 3. Load last 7 days → 4. Generate SVG charts to `img/{btc,eth}-usd.svg` → 5. Render `templates/readme.md` → `README.md`

### Key Directories

- `data/` — CSV price history (full archive)
- `img/` — Generated SVG charts
- `templates/` — Jinja2 template for README
- `tests/` — pytest test suite

## Configuration

- **Package management**: `uv` (pyproject.toml + uv.lock)
- **Python version**: 3.14
- **Type checking**: Pyright in standard mode
- **Linting**: Ruff (E, F, W, I, UP rules)
- **Testing**: pytest
- **Docker**: Alpine-based image with uv

## Environment Variables

- `COINGECKO_API_KEY` — CoinGecko Demo API key (required)
- `GITHUB_REPO_URL` — Repository URL with embedded auth token (CI only)
- `GITHUB_USERNAME` — Git commit author name (CI only)
- `GITHUB_EMAIL` — Git commit author email (CI only)

## CI/CD

- `ci.yaml` — Runs ruff, pyright, pytest on PRs and pushes to master
- `build.yaml` — Builds and pushes Docker image when init.py, Dockerfile, pyproject.toml, or uv.lock change
- `cron.yaml` — Daily scheduled run at 5:50 UTC

## API

- **CoinGecko API**: `https://api.coingecko.com/api/v3/simple/price`
- Auth: `x-cg-demo-api-key` header
- Coins: `bitcoin`, `ethereum`
