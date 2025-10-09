FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Install minimal system build deps (kept small on purpose)
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy lock and pyproject first for better layer caching
COPY pyproject.toml uv.lock /app/

# Install uv and use it to install dependencies from the lockfile.
# If `uv install` fails for any reason, fall back to installing the project with pip.
RUN python -m pip install --upgrade pip setuptools wheel \
    && pip install uv \
    && (uv install --no-dev || pip install .)

# Copy the rest of the application
COPY . /app

EXPOSE 5000

# Default command - keep using the builtin Flask server so the image is simple to run.
CMD ["python", "app.py"]
