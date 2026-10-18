"""Bounded Seedance video submission and task lookup for AstrBot."""

from __future__ import annotations

import asyncio
import json
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener

API_BASE = "https://api.acedata.cloud"
MODELS = {
    "doubao-seedance-2-0-260128": (4, 15, {"480p", "720p", "1080p", "4k"}),
    "doubao-seedance-2-0-fast-260128": (4, 15, {"480p", "720p"}),
    "doubao-seedance-2-0-mini-260615": (4, 15, {"480p", "720p"}),
    "doubao-seedance-2-5-260628": (4, 30, {"480p", "720p", "1080p"}),
}
RATIOS = {"16:9", "4:3", "1:1", "3:4", "9:16", "21:9"}
FAILED = {"failed", "error", "cancelled", "canceled", "rejected"}


class _NoRedirect(HTTPRedirectHandler):
    """Keep the configured API key on the fixed Ace Data Cloud host."""

    def redirect_request(self, request, fp, code, msg, headers, newurl):
        """Reject every API redirect."""
        return


OPENER = build_opener(_NoRedirect)


class SeedanceError(RuntimeError):
    """An error safe to return to an AstrBot conversation."""


def _valid_https_url(url: str) -> bool:
    try:
        parsed = urlsplit(url)
    except ValueError:
        return False
    return bool(
        parsed.scheme == "https"
        and parsed.netloc
        and not parsed.username
        and not parsed.password
    )


class SeedanceClient:
    """Submit one video job or query one existing task."""

    def __init__(self, api_key: str) -> None:
        token = api_key.strip()
        if (
            not token
            or token.lower().startswith("bearer ")
            or token.startswith("platform-")
        ):
            raise SeedanceError(
                "Set an Ace Data Cloud generation API key in plugin settings."
            )
        self._api_key = token

    def _post(self, path: str, payload: dict[str, Any]) -> tuple[dict[str, Any], str]:
        request = Request(
            API_BASE + path,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": "Bearer " + self._api_key,
                "Accept": "application/json",
                "Content-Type": "application/json",
                "User-Agent": "AceDataCloudAstrBot/0.1.1",
            },
            method="POST",
        )
        try:
            with OPENER.open(request, timeout=90) as response:
                body = json.load(response)
                trace_id = response.headers.get(
                    "x-trace-id", ""
                ) or response.headers.get("x-request-id", "")
        except HTTPError as exc:
            raise SeedanceError(
                f"Ace Data Cloud returned HTTP {exc.code}. Check service access and request history."
            ) from None
        except (URLError, TimeoutError, OSError):
            raise SeedanceError(
                "The API connection failed. Check request history before submitting another video."
            ) from None
        except (ValueError, UnicodeError):
            raise SeedanceError(
                "The API returned invalid JSON. Check request history before retrying."
            ) from None
        if not isinstance(body, dict):
            raise SeedanceError("The API returned an unexpected response format.")
        return body, str(body.get("trace_id") or trace_id)

    async def submit(
        self,
        prompt: str,
        model: str = "doubao-seedance-2-0-mini-260615",
        duration: int = 4,
        resolution: str = "480p",
        ratio: str = "16:9",
        image_url: str = "",
        image_role: str = "first_frame",
    ) -> dict[str, Any]:
        """Submit one asynchronous text or image video request without retrying."""
        prompt = prompt.strip()
        if not prompt or len(prompt) > 4000:
            raise SeedanceError("Provide a video prompt of 1–4000 characters.")
        spec = MODELS.get(model)
        if spec is None:
            raise SeedanceError("Choose one of the supported Seedance model IDs.")
        minimum, maximum, resolutions = spec
        if (
            not isinstance(duration, int)
            or isinstance(duration, bool)
            or not minimum <= duration <= maximum
        ):
            raise SeedanceError(
                f"Duration for this model must be {minimum}–{maximum} seconds."
            )
        if resolution not in resolutions:
            raise SeedanceError("Choose a resolution supported by this model.")
        if ratio not in RATIOS:
            raise SeedanceError("Choose a supported aspect ratio.")
        content: list[dict[str, Any]] = [{"type": "text", "text": prompt}]
        if image_url:
            if not _valid_https_url(image_url):
                raise SeedanceError("Provide an authorized HTTPS reference image URL.")
            if image_role not in {"first_frame", "reference_image"}:
                raise SeedanceError(
                    "Image role must be first_frame or reference_image."
                )
            content.append(
                {
                    "type": "image_url",
                    "role": image_role,
                    "image_url": {"url": image_url},
                }
            )
        payload = {
            "model": model,
            "content": content,
            "duration": duration,
            "resolution": resolution,
            "ratio": ratio,
            "async": True,
        }
        body, trace_id = await asyncio.to_thread(
            self._post, "/seedance/videos", payload
        )
        if body.get("success") is False or body.get("error"):
            raise SeedanceError(
                "Video submission was rejected. Check request history before trying again."
            )
        task_id = body.get("task_id")
        if not isinstance(task_id, str) or not task_id:
            raise SeedanceError(
                "No task ID was returned. Check request history before submitting again."
            )
        return {
            "status": "submitted",
            "task_id": task_id,
            "trace_id": trace_id,
            "next_step": "Query this same task ID; do not submit another video while it is pending.",
        }

    async def query(self, task_id: str) -> dict[str, Any]:
        """Return a final video URL only after this same task succeeds."""
        task_id = task_id.strip()
        if not task_id or len(task_id) > 128:
            raise SeedanceError("Pass the exact task ID from Seedance submission.")
        body, trace_id = await asyncio.to_thread(
            self._post,
            "/seedance/tasks",
            {"id": task_id, "action": "retrieve"},
        )
        if body.get("success") is False or body.get("error"):
            raise SeedanceError("Task lookup failed. Check request history.")
        response = body.get("response")
        if isinstance(response, str):
            try:
                response = json.loads(response)
            except ValueError:
                response = None
        if not isinstance(response, dict):
            response = {}
        data = response.get("data")
        if not isinstance(data, dict):
            data = {}
        state = str(data.get("status") or response.get("status") or "").lower()
        trace_id = str(response.get("trace_id") or trace_id)
        if state in FAILED or response.get("success") is False or response.get("error"):
            return {
                "task_id": task_id,
                "trace_id": trace_id,
                "status": "failed",
                "success": False,
                "video_url": "",
            }
        video_url = data.get("video_url")
        if (
            state == "succeeded"
            and isinstance(video_url, str)
            and _valid_https_url(video_url)
        ):
            return {
                "task_id": task_id,
                "trace_id": trace_id,
                "status": "succeeded",
                "success": True,
                "video_url": video_url,
                "model": str(data.get("model") or ""),
            }
        return {
            "task_id": task_id,
            "trace_id": trace_id,
            "status": "pending",
            "success": False,
            "video_url": "",
        }
