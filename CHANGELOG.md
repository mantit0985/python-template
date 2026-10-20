# Changelog

## v0.1.0

### Added

- professional Python service starter: FastAPI application skeleton under `src/` with smoke tests under `tests/`
- multi-stage `Dockerfile` producing the `runtime-slim`, `runtime-alpine`, and `runtime-distroless` container variants deployed by CD
- thin workflow wrappers at `.github/workflows/ci.yml` and `.github/workflows/cd.yml` calling the reusable CI and CD contracts at `mantit0985/.github` `@main`
- toolchain configuration: `pyproject.toml`, `uv.lock`, `pyrightconfig.json`, `.pre-commit-config.yaml`, with `ruff`, `pyright`, and `pytest` stages
- `make hooks` installer wiring the pre-push release gate and commit-msg guard
- baseline documentation: `README.md` starter guide and `AGENTS.md` maintenance rituals

### Verify this release

```bash
sha256sum -c SHA256SUMS
```
