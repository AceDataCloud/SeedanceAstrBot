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

    @filter.command("seedance_ace")
    async def seedance_ace_help(self, event: AstrMessageEvent):
        """Show Seedance setup and existing-task help without an API call."""
        yield event.plain_result(
            "Seedance by Ace Data Cloud / Ace Data Cloud 提供的 Seedance 集成\nSetup / 配置：Plugins → Plugins → Installed → plugin gear / 插件 → 插件 → 已安装 → 齿轮。\nRegister/sign in / 注册登录：https://platform.acedata.cloud/console/applications?utm_source=opensource&utm_medium=referral&utm_campaign=evergreen&utm_content=seedanceastrbot_command_help\nGeneral application → Manage Keys → Create；首次先初始化通用应用。\nAllow APIs / 允许接口：/seedance/videos + /seedance/tasks。检查当前权限、余额和价格。\nPaste the API Key in plugin settings only, never in chat. / 只在插件设置填 Key，不在聊天发送密钥。\nAdmin existing-task lookup / 管理员查已有任务：/seedance_ace_task <task_id>\nAgent lookup tool / Agent 查询工具：seedance_get_task；生成只调用一次，pending 时继续查同一 ID。\nGuide / 指南：https://github.com/AceDataCloud/SeedanceAstrBot#readme"
        )

    @filter.permission_type(filter.PermissionType.ADMIN)
    @filter.command("seedance_ace_task")
    async def seedance_ace_task(self, event: AstrMessageEvent, task_id: str):
        """Let administrators retrieve one existing task without an LLM or generation."""
        try:
            result = await SeedanceClient(self.config.get("api_key", "")).query(task_id)
        except SeedanceError as exc:
            result = {"status": "error", "message": str(exc), "task_id": task_id}
        yield event.plain_result(json.dumps(result, ensure_ascii=False))
