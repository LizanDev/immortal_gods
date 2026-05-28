FROM python:3.13-slim AS base

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

COPY apps/ apps/
COPY config/ config/
COPY templates/ templates/
COPY static/ static/
COPY manage.py entrypoint.sh ./
RUN chmod +x entrypoint.sh

ENV PORT=8000
EXPOSE 8000

CMD ["bash", "entrypoint.sh"]
