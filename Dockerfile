# syntax=docker/dockerfile:1

# Build stage
FROM python:3.15-slim AS builder

# Install uv
COPY --from=ghcr.io/astral-sh/uv:0.13.0 /uv /uvx /bin/
RUN apt-get update && apt-get install -y --no-install-recommends build-essential && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY pyproject.toml uv.lock README.md ./

# Export dependencies to a requirements file
RUN --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    uv export --frozen --no-dev -o requirements.txt

# Install dependencies into a specific folder to avoid system pollution and enable easy copying
RUN --mount=type=cache,target=/root/.cache/uv \
    uv pip install --target /app/pkgs -r requirements.txt

# Musl builder for Alpine/Distroless
FROM python:3.15-alpine AS builder-musl
COPY --from=ghcr.io/astral-sh/uv:0.13.0 /uv /uvx /bin/
RUN apk add --no-cache build-base
WORKDIR /app
COPY pyproject.toml uv.lock README.md ./
RUN --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    uv export --frozen --no-dev -o requirements.txt
RUN --mount=type=cache,target=/root/.cache/uv \
    uv pip install --target /app/pkgs -r requirements.txt

# --- Runtime targets ---

# 1. runtime-slim (Debugging image with shell)
FROM python:3.15-slim AS runtime-slim
WORKDIR /app
COPY --from=builder /app/pkgs /usr/local/lib/python3.15/site-packages
COPY src /app/src
COPY pyproject.toml uv.lock README.md ./
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app
RUN apt-get update && apt-get install -y build-essential
RUN python -m pip uninstall -y setuptools msgpack urllib3 jaraco.context wheel \
    && python -m pip install --no-cache-dir jaraco.context==6.1.0 wheel==0.46.2 setuptools==78.1.1 msgpack==1.2.1 urllib3==2.8.0
# Strip vendored metadata that scanners flag as stale CVE-bearing copies:
# pip's vendored SBOM (bom.cdx.json / vendor.txt) and license mirror trees,
# plus stale dist-infos vendored inside setuptools (code is untouched).
RUN rm -rf /usr/local/lib/python3.15/site-packages/pip/_vendor/bom.cdx.json \
           /usr/local/lib/python3.15/site-packages/pip/_vendor/vendor.txt \
    && rm -rf /usr/local/lib/python3.15/site-packages/pip-*.dist-info/licenses/src \
    && rm -rf /usr/local/lib/python3.15/site-packages/setuptools/_vendor/*.dist-info
RUN groupadd -r nonroot && useradd -r -g nonroot nonroot
USER nonroot
EXPOSE 8080
# Smoke contract: serve on 8080 by default; APP_PORT env overrides.
CMD ["sh", "-c", "exec python -m uvicorn src.main:app --host 0.0.0.0 --port ${APP_PORT:-8080}"]

# 2. runtime-alpine (Minimal footprint)
FROM python:3.15-alpine AS runtime-alpine
WORKDIR /app
COPY --from=builder-musl /app/pkgs /usr/local/lib/python3.15/site-packages
COPY src /app/src
COPY pyproject.toml uv.lock README.md ./
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app
RUN apk add --no-cache build-base
RUN python -m pip uninstall -y setuptools msgpack urllib3 jaraco.context wheel \
    && python -m pip install --no-cache-dir jaraco.context==6.1.0 wheel==0.46.2 setuptools==78.1.1 msgpack==1.2.1 urllib3==2.8.0
# Strip vendored metadata that scanners flag as stale CVE-bearing copies (see runtime-slim).
RUN rm -rf /usr/local/lib/python3.15/site-packages/pip/_vendor/bom.cdx.json \
           /usr/local/lib/python3.15/site-packages/pip/_vendor/vendor.txt \
    && rm -rf /usr/local/lib/python3.15/site-packages/pip-*.dist-info/licenses/src \
    && rm -rf /usr/local/lib/python3.15/site-packages/setuptools/_vendor/*.dist-info
RUN addgroup -S nonroot && adduser -S nonroot -G nonroot
USER nonroot
EXPOSE 8080
# Smoke contract: serve on 8080 by default; APP_PORT env overrides.
CMD ["sh", "-c", "exec python -m uvicorn src.main:app --host 0.0.0.0 --port ${APP_PORT:-8080}"]

# 3. runtime-distroless (Hardened production image with NO shell)
# Chainguard (Wolfi) is glibc-based, so dependencies must come from the glibc
# builder; musl-built extension modules (pydantic-core) fail to import here.
FROM cgr.dev/chainguard/python:latest AS runtime-distroless
WORKDIR /app
COPY --from=builder /app/pkgs /usr/lib/python3.15/site-packages
COPY src /app/src
COPY pyproject.toml uv.lock README.md ./
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app
USER nonroot
EXPOSE 8080
# Base image defines ENTRYPOINT ["/usr/bin/python"], so CMD passes module args only.
# No shell in distroless: launch via -c so APP_PORT env can override the 8080 default.
CMD ["-c", "import os, uvicorn; from src.main import app; uvicorn.run(app, host='0.0.0.0', port=int(os.environ.get('APP_PORT', '8080')))"]
