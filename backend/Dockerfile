FROM python:3.12-slim

WORKDIR /app

# Install uv
RUN pip install uv

# Copy project files
COPY pyproject.toml .
COPY uv.lock .

# Install dependencies using uv
RUN uv sync --frozen --no-cache

# Copy application source
COPY app/ ./app/
COPY alembic/ ./alembic/
COPY alembic.ini .
COPY config/ ./config/

ENV PYTHONPATH=/app

# Expose port
EXPOSE 8000

# Start server
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
