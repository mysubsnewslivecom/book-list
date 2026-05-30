# ---------- Builder ----------
FROM python:3.14-slim AS builder

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Use system Python
ENV UV_PYTHON_DOWNLOADS=0

# Create non-root user
RUN useradd -m appuser

USER appuser
WORKDIR /app

# Copy dependency files first for better layer caching
COPY --chown=appuser:appuser pyproject.toml uv.lock ./

# Create virtualenv + install deps
RUN uv sync --frozen --no-dev && rm -rvf *.egg-info uv.lock pyproject.toml

# Copy application source
COPY --chown=appuser:appuser . .

# ---------- Runtime ----------
FROM python:3.14-slim

ENV VIRTUAL_ENV=/app/.venv \
    PATH="/app/.venv/bin:$PATH" \
    PYTHONPATH=/app/src

RUN useradd -m appuser

WORKDIR /app

# Copy virtual environment
COPY --from=builder /app/.venv /app/.venv

# Copy application files
COPY --from=builder /app/ /app/

# Use non-root user
USER appuser

EXPOSE 8001

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]
