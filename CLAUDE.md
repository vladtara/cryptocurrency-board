# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Automated cryptocurrency price monitoring system. Fetches BTC and ETH prices from the Blockchain.com API daily, maintains 7-day rolling CSV history, generates Matplotlib charts, and renders a README with current prices via Jinja2. Runs daily at 5:50 AM UTC via GitHub Actions cron job in Docker.

## Build & Run

```bash
pip install -r requirements.txt

# Run the main pipeline (fetch prices, update CSVs, generate charts, render README)
python main.py

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
