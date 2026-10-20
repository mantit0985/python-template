# [Project Name] - Service Starter Guide

![CI](https://github.com/mantit0985/python-template/actions/workflows/ci.yml/badge.svg) ![CD](https://github.com/mantit0985/python-template/actions/workflows/cd.yml/badge.svg) ![Python](https://img.shields.io/badge/python-3.14-blue) ![License](https://img.shields.io/github/license/mantit0985/python-template)

A professional, production-ready Python service designed for scalability, maintainability, and high developer velocity.

## Compliance & Standards

- **Styling**: Adheres to [PEP 8](https://peps.python.org/pep-0008/) via `ruff`.
- **Typing**: Implements [PEP 484](https://peps.python.org/pep-0484/) Type Hints via `pyright`.
- **Security**: Verified against [OWASP Top 10](https://owasp.org/www-project-top-ten/) and [CWE](https://cwe.mitre.org/) via Semgrep SAST.

## Getting Started

### Prerequisites

- Python 3.14+
- [uv](https://github.com/astral-sh/uv) installed on your system.

### Installation & Development

1. **Install dependencies**:

   ```bash
   uv sync
   ```

2. **Configure environment**:

   ```bash
   cp .env.example .env
   # Edit .env with your specific configuration
   ```

3. **Run the service**:

   ```bash
   uv run uvicorn src.main:app --reload
   ```

The service will be available at `http://localhost:8000`. Access the interactive API documentation at `/docs`.

## Project Structure

This service uses a feature-based directory structure to ensure domain isolation and scalability.

- `src/features/`: Contains the business logic grouped by domain. Each feature typically includes:
  - `router.py`: Endpoint definitions and request handling.
  - `service.py`: Pure business logic, independent of the web framework.
  - `schemas.py`: Pydantic request and response models.
- `src/core/`: Contains shared infrastructure and cross-cutting concerns:
  - `config.py`: Centralized configuration using Pydantic Settings.
  - `logging.py`: Structured logging configuration.
  - `middleware.py`: Custom request correlation and security headers.
  - `dependencies.py`: Global FastAPI dependencies.
- `tests/`: Comprehensive test suite split into `unit/` and `integration/` tests.

## Adding New Features

To add a new domain feature:

1. **Create a new feature directory**: `src/features/<your-feature>/`
2. **Define Schemas**: Create `schemas.py` for request and response models.
3. **Implement Logic**: Create `service.py` for the business logic.
4. **Define Endpoints**: Create `router.py` to handle HTTP requests.
5. **Register Router**: Add the new router to `src/main.py` using `app.include_router()`.

## Testing and Linting

### Run Tests

```bash
uv run pytest
```

### Lint and Format

```bash
uv run ruff check .   # Linting
uv run ruff format .   # Formatting
```

### Type Checking

```bash
uv run pyright
```

## Docker

### Build the image

```bash
docker build -t python-template .
```

### Run the container

```bash
docker run -p 8000:8000 --env-file .env python-template
```

## Release process

Releases are made by pushing an annotated GPG-signed tag (`git tag -a vX.Y.Z -m "release vX.Y.Z" && git push origin vX.Y.Z`). A pre-push hook (release-gate.sh) validates the tag at push time:

1. tag name matches the VERSION file at that commit
2. tagged commit is origin/main tip
3. latest CI run for that commit is green
4. tag signature verifies

On success the hub release workflow publishes the GitHub Release with SHA256SUMS and its detached signature. Enable the hook in your clone with:
`git config core.hooksPath <hub-repo-clone>/.github/hooks`
