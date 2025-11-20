from __future__ import annotations

from datetime import datetime, timedelta, timezone

from pm_api_fetcher.polymarket import (
    SeriesMarketCollector,
    _parse_clob_tokens,
)


def test_parse_clob_tokens_handles_stringified_list() -> None:
    tokens = _parse_clob_tokens('["yes-token","no-token"]')
    assert tokens == ["yes-token", "no-token"]


def test_iter_open_events_filters_closed_and_expired() -> None:
    collector = SeriesMarketCollector(series_id=1)
    now = datetime.now(timezone.utc)
    collector._series_payload = {  # type: ignore[attr-defined]
        "events": [
            {
                "id": "active",
                "closed": False,
                "endDate": (now + timedelta(days=1)).isoformat(),
            },
            {
                "id": "closed",
                "closed": True,
                "endDate": (now + timedelta(days=1)).isoformat(),
            },
            {
                "id": "expired",
                "closed": False,
                "endDate": (now - timedelta(days=1)).isoformat(),
            },
        ]
    }

    events = list(collector.iter_open_events())

    assert len(events) == 1
    assert events[0]["id"] == "active"


def test_build_open_events_payload_enriches_markets(monkeypatch) -> None:
    future = (datetime.now(timezone.utc) + timedelta(days=2)).isoformat()

    class DummyCollector(SeriesMarketCollector):
        def __init__(self) -> None:
            super().__init__(series_id=99)
            self._series_payload = {  # type: ignore[attr-defined]
                "events": [
                    {
                        "id": "evt-1",
                        "title": "Series Level Title",
                        "slug": "series-level",
                        "startDate": future,
                        "endDate": future,
                        "ticker": "PM99",
                        "volume": "100",
                        "liquidity": "50",
                    }
                ]
            }

        def _fetch_event_detail(self, event_id: str) -> dict[str, object]:
            assert event_id == "evt-1"
            return {
                "id": event_id,
                "title": "Detailed Title",
                "slug": "detailed",
                "startDate": future,
                "endDate": future,
                "markets": [
                    {
                        "id": "m-active",
                        "question": "Will it rain?",
                        "groupItemTitle": "Weather",
                        "active": True,
                        "closed": False,
                        "clobTokenIds": '["yes","no"]',
                    },
                    {
                        "id": "m-closed",
                        "active": False,
                        "closed": True,
                        "clobTokenIds": '["x","y"]',
                    },
                ],
            }

    collector = DummyCollector()
    payload = collector.build_open_events_payload()

    assert len(payload) == 1
    event = payload[0]
    assert event["event_id"] == "evt-1"
    assert event["markets"] == [
        {
            "market_id": "m-active",
            "question": "Will it rain?",
            "groupItemTitle": "Weather",
            "active": True,
            "closed": False,
            "yes_token": "yes",
            "no_token": "no",
        }
    ]
