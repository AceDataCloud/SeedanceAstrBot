"""Video submission and terminal-result boundaries."""

from __future__ import annotations

import json
from unittest.mock import patch

import pytest

from client import SeedanceClient, SeedanceError


class FakeResponse:
    def __init__(self, payload: dict) -> None:
        self.payload = payload
        self.headers = {"x-trace-id": "trace-seedance"}

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False

    def read(self, *_):
        return json.dumps(self.payload).encode()


@pytest.mark.asyncio
async def test_submit_sends_one_async_video_request():
    calls = []

    def fake_open(request, timeout):
        calls.append((request.full_url, json.loads(request.data), timeout))
        return FakeResponse({"success": True, "task_id": "task-123"})

    with patch("client.OPENER.open", side_effect=fake_open):
        result = await SeedanceClient("test-key").submit(
            "A paper kite rises", duration=4
        )
    assert calls == [
        (
            "https://api.acedata.cloud/seedance/videos",
            {
                "model": "doubao-seedance-2-0-mini-260615",
                "content": [{"type": "text", "text": "A paper kite rises"}],
                "duration": 4,
                "resolution": "480p",
                "ratio": "16:9",
                "async": True,
            },
            90,
        )
    ]
    assert result["status"] == "submitted"
    assert result["task_id"] == "task-123"
    assert "video_url" not in result


@pytest.mark.asyncio
async def test_task_lookup_withholds_video_until_terminal_success():
    pending = {"id": "task-123", "finished_at": None, "response": None}
    finished = {
        "id": "task-123",
        "finished_at": 123.0,
        "response": {
            "success": True,
            "data": {
                "status": "succeeded",
                "video_url": "https://cdn.example.org/final.mp4",
                "model": "doubao-seedance-2-0-mini-260615",
                "supplier": "internal-only",
            },
        },
    }
    failed = {
        "response": {
            "success": False,
            "data": {
                "status": "failed",
                "video_url": "https://cdn.example.org/preview.mp4",
            },
        }
    }
    with patch(
        "client.OPENER.open",
        side_effect=[
            FakeResponse(pending),
            FakeResponse(finished),
            FakeResponse(failed),
        ],
    ) as opening:
        first = await SeedanceClient("test-key").query("task-123")
        last = await SeedanceClient("test-key").query("task-123")
        unsuccessful = await SeedanceClient("test-key").query("task-123")
    assert opening.call_count == 3
    assert first["status"] == "pending"
    assert first["video_url"] == ""
    assert last["status"] == "succeeded"
    assert last["video_url"] == "https://cdn.example.org/final.mp4"
    assert "supplier" not in last
    assert unsuccessful["status"] == "failed"
    assert unsuccessful["video_url"] == ""


@pytest.mark.asyncio
async def test_invalid_inputs_never_submit_a_paid_job():
    with patch("client.OPENER.open") as opening, pytest.raises(SeedanceError):
        await SeedanceClient("test-key").submit(" ")
    assert opening.call_count == 0
    with patch("client.OPENER.open") as opening, pytest.raises(SeedanceError):
        await SeedanceClient("test-key").submit(
            "A kite", model="doubao-seedance-1-0-lite-t2v-250428"
        )
    assert opening.call_count == 0
    with patch("client.OPENER.open") as opening, pytest.raises(SeedanceError):
        await SeedanceClient("test-key").submit(
            "A kite", model="doubao-seedance-2-0-mini-260615", duration=2
        )
    assert opening.call_count == 0
    with patch("client.OPENER.open") as opening, pytest.raises(SeedanceError):
        await SeedanceClient("test-key").submit(
            "A kite", image_url="http://example.org/image.jpg"
        )
    assert opening.call_count == 0
