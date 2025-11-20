# pyright: reportMissingTypeStubs=false
"""Helpers to fetch Polymarket series data and extract open events."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

import requests  # type: ignore[reportMissingTypeStubs]

URL_TEMPLATE = "https://gamma-api.polymarket.com/series/{series_id}"
EVENT_URL_TEMPLATE = "https://gamma-api.polymarket.com/events/{event_id}"
DEFAULT_SERIES_ID = 35


def _series_file(series_id: int) -> Path:
    return Path(__file__).with_name(f"series_{series_id}.json")


def _open_events_file(series_id: int) -> Path:
    return Path(__file__).with_name(f"series_{series_id}_open_events.json")


def fetch_series_to_json(
    series_id: int = DEFAULT_SERIES_ID,
    output_path: Path | None = None,
) -> Path:
    """Fetch series data by id and persist result as JSON."""

    target_path = Path(output_path) if output_path else _series_file(series_id)
    response = requests.get(
        URL_TEMPLATE.format(series_id=series_id),
        timeout=30,
    )
    response.raise_for_status()
    target_path.write_text(
        json.dumps(response.json(), indent=2),
        encoding="utf-8",
    )
    return target_path


def extract_open_events(
    series_id: int = DEFAULT_SERIES_ID,
    series_json_path: Path | None = None,
    output_path: Path | None = None,
) -> Path:
    """Load the cached series JSON and persist all open events."""

    source_path = (
        Path(series_json_path)
        if series_json_path
        else _series_file(series_id)
    )
    series_payload: dict[str, Any] = json.loads(
        source_path.read_text(encoding="utf-8")
    )
    open_events = [
        event
        for event in series_payload.get("events", [])
        if not event.get("closed", False)
    ]
    target_path = (
        Path(output_path)
        if output_path
        else _open_events_file(series_id)
    )
    target_path.write_text(
        json.dumps(open_events, indent=2),
        encoding="utf-8",
    )
    return target_path


def _parse_clob_tokens(raw_token_ids: Any) -> list[str]:
    """Parse yes/no token identifiers from a Polymarket market payload."""

    if isinstance(raw_token_ids, str):
        try:
            parsed = json.loads(raw_token_ids)
            return [str(token) for token in parsed]
        except json.JSONDecodeError:  # pragma: no cover - defensive fallback
            return []
    if isinstance(raw_token_ids, list):
        return [str(token) for token in raw_token_ids]
    return []


class SeriesMarketCollector:
    """Collect open events and associated markets for a series."""

    def __init__(
        self,
        series_id: int,
        output_dir: Path | None = None,
    ) -> None:
        self.series_id = series_id
        self.output_dir = output_dir or Path(__file__).parent
        self._series_payload: dict[str, Any] | None = None

    def _fetch_json(self, url: str) -> dict[str, Any]:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        return response.json()

    @staticmethod
    def _parse_iso_datetime(value: str | None) -> datetime | None:
        if not value:
            return None
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            return None

    def fetch_series_data(self) -> dict[str, Any]:
        """Fetch and cache the full series payload."""

        if self._series_payload is None:
            self._series_payload = self._fetch_json(
                URL_TEMPLATE.format(series_id=self.series_id)
            )
        return self._series_payload

    def iter_open_events(self) -> Iterable[dict[str, Any]]:
        """Yield every open event from the cached series payload."""

        series_payload = self.fetch_series_data()
        now = datetime.now(timezone.utc)
        for event in series_payload.get("events", []):
            if event.get("closed", False):
                continue
            end_date = self._parse_iso_datetime(event.get("endDate"))
            if end_date and end_date <= now:
                continue
            yield event

    def _format_market(self, market: dict[str, Any]) -> dict[str, Any]:
        token_ids = _parse_clob_tokens(market.get("clobTokenIds"))
        return {
            "market_id": market.get("id", ""),
            "question": market.get("question"),
            "groupItemTitle": market.get("groupItemTitle"),
            "active": market.get("active"),
            "closed": market.get("closed"),
            "yes_token": token_ids[0] if len(token_ids) > 0 else "",
            "no_token": token_ids[1] if len(token_ids) > 1 else "",
        }

    def _fetch_event_detail(self, event_id: str) -> dict[str, Any]:
        return self._fetch_json(EVENT_URL_TEMPLATE.format(event_id=event_id))

    def _compose_event_payload(
        self,
        series_event: dict[str, Any],
        detailed_event: dict[str, Any],
    ) -> dict[str, Any]:
        markets_payload = [
            self._format_market(market)
            for market in detailed_event.get("markets", [])
            if market.get("active", False) and not market.get("closed", False)
        ]
        return {
            "event_id": detailed_event.get("id", series_event.get("id")),
            "title": detailed_event.get("title", series_event.get("title")),
            "slug": detailed_event.get("slug", series_event.get("slug")),
            "startDate": detailed_event.get(
                "startDate", series_event.get("startDate")
            ),
            "endDate": detailed_event.get(
                "endDate",
                series_event.get("endDate"),
            ),
            "seriesSnapshot": {
                "ticker": series_event.get("ticker"),
                "volume": series_event.get("volume"),
                "liquidity": series_event.get("liquidity"),
            },
            "markets": markets_payload,
        }

    def build_open_events_payload(self) -> list[dict[str, Any]]:
        """Return list of open events enriched with market data."""

        events_payload: list[dict[str, Any]] = []
        for series_event in self.iter_open_events():
            event_id = series_event.get("id")
            if not event_id:
                continue
            detailed_event = self._fetch_event_detail(str(event_id))
            events_payload.append(
                self._compose_event_payload(series_event, detailed_event)
            )
        return events_payload

    def export_open_events_with_markets(
        self,
        output_filename: str | None = None,
    ) -> Path:
        """Persist all open events with markets to JSON and return the path."""

        payload = {
            "series_id": str(self.series_id),
            "generatedAt": datetime.now(timezone.utc).isoformat(),
            "events": self.build_open_events_payload(),
        }
        target_path = (
            Path(output_filename)
            if output_filename
            else Path(self.output_dir)
            / f"series_{self.series_id}_open_events_with_markets.json"
        )
        target_path.write_text(
            json.dumps(payload, indent=2),
            encoding="utf-8",
        )
        return target_path


def export_event_market_tokens(
    event_id: str,
    output_path: Path | None = None,
) -> Path:
    """Fetch event detail and export readable market/token mappings."""

    response = requests.get(
        EVENT_URL_TEMPLATE.format(event_id=event_id),
        timeout=30,
    )
    response.raise_for_status()
    event_payload: dict[str, Any] = response.json()

    markets_data: list[dict[str, Any]] = []
    for market in event_payload.get("markets", []):
        token_ids = _parse_clob_tokens(market.get("clobTokenIds"))
        markets_data.append(
            {
                "market_id": market.get("id", ""),
                "question": market.get("question"),
                "groupItemTitle": market.get("groupItemTitle"),
                "active": market.get("active"),
                "closed": market.get("closed"),
                "yes_token": token_ids[0] if len(token_ids) > 0 else "",
                "no_token": token_ids[1] if len(token_ids) > 1 else "",
            }
        )

    readable_payload = {
        "event_id": event_payload.get("id", event_id),
        "title": event_payload.get("title"),
        "slug": event_payload.get("slug"),
        "startDate": event_payload.get("startDate"),
        "endDate": event_payload.get("endDate"),
        "markets": markets_data,
    }

    target_path = (
        Path(output_path)
        if output_path
        else Path(__file__).with_name(
            f"event_{event_id}_market_tokens.json"
        )
    )
    target_path.write_text(
        json.dumps(readable_payload, indent=2),
        encoding="utf-8",
    )
    return target_path


__all__ = [
    "DEFAULT_SERIES_ID",
    "URL_TEMPLATE",
    "EVENT_URL_TEMPLATE",
    "SeriesMarketCollector",
    "export_event_market_tokens",
    "extract_open_events",
    "fetch_series_to_json",
]
