FROM python:3.13-slim

ENV GITHUB_REPO_URL=""
ENV GITHUB_USERNAME=""
ENV GITHUB_EMAIL=""
ENV COINGECKO_API_KEY=""

WORKDIR /app

RUN apt-get update \
    && apt-get install --yes --no-install-recommends git \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir uv

COPY pyproject.toml uv.lock ./

RUN uv sync --frozen --no-dev

COPY init.py .

CMD ["uv", "run", "python", "init.py"]
