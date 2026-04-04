# Use the official Python base image
FROM python:3.14-slim

ENV GITHUB_REPO_URL=""
ENV GITHUB_USERNAME=""
ENV GITHUB_EMAIL=""

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential git \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir uv

COPY pyproject.toml uv.lock .python-version ./

RUN uv sync --frozen --no-dev --no-install-project

COPY init.py .

ENV PATH="/app/.venv/bin:$PATH"

CMD ["python", "init.py"]
