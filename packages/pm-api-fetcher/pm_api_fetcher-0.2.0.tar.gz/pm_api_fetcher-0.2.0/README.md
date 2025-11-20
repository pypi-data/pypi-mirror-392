# pm-api-fetcher

Focused helpers for downloading Polymarket series data and exporting the open
events/markets to JSON so they can be consumed elsewhere.

## Features

- Fetch a series payload and cache it locally via `fetch_series_to_json`
- Extract the currently open events from a cached series file
- Enrich open events with market metadata through `SeriesMarketCollector`
- Export readable token mappings for a single event

## Quickstart

```bash
cd pm-api-fetcher
uv sync --group dev
uv run pytest
```

## Usage

```python
from pm_api_fetcher import SeriesMarketCollector

collector = SeriesMarketCollector(series_id=35)
output_path = collector.export_open_events_with_markets()
print(f"JSON exported to {output_path}")
```

All helpers return paths to the generated JSON files so you can move or upload
them as needed in your own tooling or services.

## Tooling

- `uv run pre-commit install` – enable the linting pipeline locally
- `uv run pylint src` – static analysis
- `uv run mypy --config-file mypy.toml src` – type checking

## Releasing

1. Update the version in both `pyproject.toml` and `src/pm_api_fetcher/__init__.py`.
2. Run the local gates before tagging:
	```bash
	uv run pytest
	uv build
	```
3. Create an annotated tag that matches the new version (e.g. `git tag -a v0.3.0 -m "v0.3.0"`), then push it with `git push origin v0.3.0`.
4. The `ci-cd` GitHub Action will rerun tests, build the wheel/sdist, and publish them to PyPI using the `PYPI_API_TOKEN` repository secret (`__token__` user).

> Configure the `PYPI_API_TOKEN` secret ahead of time with a PyPI API token that has upload rights for `pm-api-fetcher`.
