"""Seedance video tools for AstrBot through Ace Data Cloud."""

from __future__ import annotations

import json

from astrbot.api import AstrBotConfig
from astrbot.api.event import AstrMessageEvent, filter
from astrbot.api.star import Context, Star

from .client import SeedanceClient, SeedanceError


class SeedancePlugin(Star):
    """Expose one video submission and one existing-task lookup tool."""

    def __init__(self, context: Context, config: AstrBotConfig) -> None:
        super().__init__(context)
        self.config = config

    @filter.llm_tool(name="seedance_generate_video")
    async def seedance_generate_video(
        self,
        event: AstrMessageEvent,
        prompt: str,
        model: str = "doubao-seedance-2-0-mini-260615",
        duration: int = 4,
        resolution: str = "480p",
        ratio: str = "16:9",
        image_url: str = "",
        image_role: str = "first_frame",
    ) -> str:
        """Submit one billable video job and save the returned task ID.

        Args:
            prompt(string): Description of the desired video.
            model(string): Explicit supported Seedance model ID.
            duration(number): Model-supported seconds; the default is four.
            resolution(string): Model-supported output resolution.
            ratio(string): Output aspect ratio such as 16:9 or 9:16.
            image_url(string): Optional authorized HTTPS image URL.
            image_role(string): first_frame or reference_image when an image is used.

        Returns:
            JSON submission status and task ID, never a finished-video claim.
        """
        try:
            result = await SeedanceClient(self.config.get("api_key", "")).submit(
                prompt, model, duration, resolution, ratio, image_url, image_role
            )
        except SeedanceError as exc:
            result = {"status": "error", "message": str(exc)}
        return json.dumps(result, ensure_ascii=False)

    @filter.llm_tool(name="seedance_get_task")
    async def seedance_get_task(self, event: AstrMessageEvent, task_id: str) -> str:
        """Query an existing Seedance task without generating another video.

        Args:
            task_id(string): Exact task ID returned by seedance_generate_video.

        Returns:
            JSON task status and final video URL only after terminal success.
        """
        try:
            result = await SeedanceClient(self.config.get("api_key", "")).query(task_id)
        except SeedanceError as exc:
            result = {"status": "error", "message": str(exc), "task_id": task_id}
        return json.dumps(result, ensure_ascii=False)
