FROM python:3.14-alpine

ENV GITHUB_REPO_URL=""
ENV GITHUB_USERNAME=""
ENV GITHUB_EMAIL=""
ENV COINGECKO_API_KEY=""

WORKDIR /app

RUN apk add --no-cache git && rm -rf /var/cache/apk/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

COPY pyproject.toml uv.lock ./

RUN uv sync --frozen --no-dev

COPY init.py .

CMD ["uv", "run", "python", "init.py"]
