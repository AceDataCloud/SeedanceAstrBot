# AstrBot 的 Seedance 插件

通过自己的 Ace Data Cloud 账号，在 AstrBot 对话中提交一次 Seedance 文生视频或单张参考图生视频任务，再用相同任务 ID 查询最终视频。插件提供 `seedance_generate_video` 和 `seedance_get_task`。

[English guide](../README.md) · [Seedance 视频 API](https://platform.acedata.cloud/documents/seedance-videos?utm_source=opensource&utm_medium=referral&utm_campaign=evergreen&utm_content=seedanceastrbot_readme_documents_seedance_videos) · [Seedance 任务 API](https://platform.acedata.cloud/documents/seedance-tasks?utm_source=opensource&utm_medium=referral&utm_campaign=evergreen&utm_content=seedanceastrbot_readme_documents_seedance_tasks) · [当前价格](https://platform.acedata.cloud/models?utm_source=opensource&utm_medium=referral&utm_campaign=evergreen&utm_content=seedanceastrbot_readme_pricing)

## 搜索与安装

在 AstrBot WebUI 打开 **Extensions → Plugins → AstrBot Plugin Market**，搜索 **Seedance**。核对卡片名称 **Seedance by Ace Data Cloud**、作者 **acedatacloud** 和 [Seedance 服务图标](https://cdn.acedata.cloud/9q90dl.png)，安装后到 **Installed** 检查加载状态。

AstrBot Cloud 官方上架尚未完成。源码合并发布后，可在 **Installed → Install (+) → Install from URL** 输入 `https://github.com/AceDataCloud/SeedanceAstrBot` 预览。URL 安装不等于官方市场安装。

## 配置 Key

首次使用请先注册并登录；如果应用页还没有通用应用，点击 **初始化通用应用（Initialize General Application）**，再按下面步骤管理密钥。

到 [Ace Data Cloud Applications](https://platform.acedata.cloud/console/applications?utm_source=opensource&utm_medium=referral&utm_campaign=evergreen&utm_content=seedanceastrbot_readme_api_key) 复制 General application 的生成 API Key，或创建同时允许 `/seedance/videos` 和 `/seedance/tasks` 的 Key。提交视频前，检查所选模型、分辨率和时长的当前价格。在插件设置 **Ace Data Cloud generation API key with Seedance access** 中粘贴 Key 本身；不要加 `Bearer `，也不要使用 `platform-...` 管理 Token。AstrBot WebUI 会遮蔽字段，但数据目录会保存原值，请保护该目录。

选择支持工具调用的聊天模型，在当前 Profile 和 Persona 中允许两个 Seedance 工具。

## 只生成一次，再查同一任务

文生视频示例：

> 只调用一次 `seedance_generate_video`，生成“一只纸风筝飞向晴朗天空”，模型 `doubao-seedance-2-0-mini-260615`，时长 `4` 秒，分辨率 `480p`，比例 `16:9`。告诉我 task ID。

工具向 `POST /seedance/videos` 提交一次异步任务，返回 `status: submitted` 和 task ID；提交成功不代表视频已经完成。保留 ID，之后询问：

> 用 `seedance_get_task` 查询原来的 `<task_id>`，只告诉我 pending、failed 或 succeeded，不要重新生成。

若仍为 pending，稍后继续查询**同一 ID**。只有 `status: succeeded`、`success: true` 且返回最终 HTTPS `video_url` 才算完成。插件不会自动重试付费提交。

2.x 模型可选传入有处理权限的 HTTPS `image_url`，`image_role` 选择 `first_frame` 或 `reference_image`。首版支持文本与单张图片；参考音频/视频、编辑/延长、2.5 纯音频参考和 1.x 模型暂未包含。

| 模型 | 时长 | 分辨率 |
| --- | --- | --- |
| `doubao-seedance-2-0-260128` | 4–15 秒 | 480p、720p、1080p、4k |
| `doubao-seedance-2-0-fast-260128` | 4–15 秒 | 480p、720p |
| `doubao-seedance-2-0-mini-260615` | 4–15 秒 | 480p、720p |
| `doubao-seedance-2-5-260628` | 4–30 秒 | 480p、720p、1080p |

## 用量与排障

在 Ace Data Cloud 用量页按返回的 trace ID 精确匹配。若响应没有 trace ID，按 API 和时间筛选只能得到关联线索。查询任务只读取已有作业，不会再次提交生成。

| 现象 | 检查项 |
| --- | --- |
| 插件加载失败 | AstrBot 版本、**Failed to Load Plugins**、**Data & Logs → Logs**。 |
| 看不到工具 | 插件已启用；当前 Profile/Persona 允许两个工具；聊天模型支持工具调用。 |
| HTTP 401/403 | Key 类型、两个 Allowed APIs 路径和账号权限。 |
| 提交后网络错误 | 再次生成前查请求历史；超时请求可能已创建付费任务。 |
| 任务 pending | 稍后查询同一个 task ID。 |
| 任务 failed | 按 task ID 或 trace ID 查看请求历史。 |

Key 只发送到 `https://api.acedata.cloud`，重定向会被拒绝。插件仅向模型返回任务状态和最终视频链接，不透出上游内部数据。运行只需 Python 标准库。

## 已验证的本地运行与图标

官方 AstrBot `v4.28.2` 的隔离实例通过 editable 安装注册了两个工具。ChatUI 使用受支持的 `doubao-seedance-2-0-mini-260615`，以 480p、4 秒提交一次文生视频，并通过 `seedance_get_task` 查询同一 task ID，没有再次生成。最终 HTTPS MP4 为 HTTP 200、`video/mp4`；`ffprobe` 解码为 H.264、864×496、4.042 秒。生成 trace 精确匹配一条成功的 `/seedance/videos` 用量，实扣 1.404 Credits；当前成本规则计算折扣前 1.56 Credits。详见[脱敏证据](../tests/e2e-results.json)。这仍是本地 editable 安装；Cloud 审核、官方市场安装及市场安装后的首次调用尚未完成。

`logo.png` 是未经修改的 200×200 [当前 Seedance 服务图标](https://cdn.acedata.cloud/9q90dl.png)，SHA-256 `6a5b07c1d33d2910eb9fe1c8549874a004d13a0e75d9b30a7cfdc255c586a83d`。
