# AstrBot 的 Seedance 插件

通过自己的 Ace Data Cloud 账号，在 AstrBot 对话中提交一次 Seedance 文生视频或单张参考图生视频任务，再用相同任务 ID 查询最终视频。插件提供 `seedance_generate_video` 和 `seedance_get_task`。

**本 PR 的目标版本为 0.1.1**：新增原生帮助及管理员查询指令、双语配置和图文说明。合并和市场发布前，当前 0.1.0 安装不会自动获得这些入口。

这是 **Ace Data Cloud 提供的 Seedance 独立集成**，不是 Seedance 厂商或 AstrBot 团队的官方插件。使用自己的 Ace 账号和 API Key；不要填写其他平台的密钥。

[English guide](../README.md) · [Seedance 视频 API](https://platform.acedata.cloud/documents/seedance-videos?utm_source=opensource&utm_medium=referral&utm_campaign=evergreen&utm_content=seedanceastrbot_readme_documents_seedance_videos) · [Seedance 任务 API](https://platform.acedata.cloud/documents/seedance-tasks?utm_source=opensource&utm_medium=referral&utm_campaign=evergreen&utm_content=seedanceastrbot_readme_documents_seedance_tasks) · [当前价格](https://platform.acedata.cloud/models?utm_source=opensource&utm_medium=referral&utm_campaign=evergreen&utm_content=seedanceastrbot_readme_pricing)

## 搜索与安装

当前上游文档（2026-10-18）：侧栏 **插件 → 顶部插件 → 插件市场 / 已安装**；旧 4.28.2 英文界面可能显示 Extensions。插件参数在已安装卡片齿轮里设置，**不要把服务插件 Key 填进模型提供商**。

**发布状态（2026-10-18）：尚未在官方市场上架。** 正式发布后，先打开 [AstrBot Cloud 插件市场](https://cloud.astrbot.app/market)，搜索 **Seedance**，再核对 **Seedance by Ace Data Cloud / acedatacloud**。当前请用下面的 Git 仓地址手动安装；不要把仓库安装说成官方市场收录。

AstrBot Cloud 官方上架尚未完成。源码已合并，可在 **Plugins → Plugins → Installed → Install Plugin (+) → Install from URL** 输入 `https://github.com/AceDataCloud/SeedanceAstrBot` 预览。URL 安装不等于官方市场安装。

## 配置 Key

先[注册或登录 Ace](https://platform.acedata.cloud/console/applications?utm_source=opensource&utm_medium=referral&utm_campaign=evergreen&utm_content=seedanceastrbot_readme_signup)；首次没有通用应用时，先初始化 **General application**。下图取自同一 Ace 应用管理页面，不是 AstrBot 界面。

到 [Ace Data Cloud Applications](https://platform.acedata.cloud/console/applications?utm_source=opensource&utm_medium=referral&utm_campaign=evergreen&utm_content=seedanceastrbot_readme_api_key) 复制 General application 的生成 API Key，或创建同时允许 `/seedance/videos` 和 `/seedance/tasks` 的 Key。提交视频前，检查所选模型、分辨率和时长的当前价格。在插件设置 **Ace Data Cloud generation API key with Seedance access** 中粘贴 Key 本身；不要加 `Bearer `，也不要使用 `platform-...` 管理 Token。AstrBot WebUI 会遮蔽字段，但数据目录会保存原值，请保护该目录。

使用 Agent 工具时，选择支持工具调用的聊天模型，在当前 Profile 和 Persona 中允许两个 Seedance 工具。

1. 打开 **General application**，用图中 **1** 复制现有 Key，或点 **2 Manage Keys → Create** 创建专用 Key。

![复制 Ace Key 或管理专用 Key（已脱敏）](../_assets/tutorial/get-api-key-en.png)

2. 可把名称设为 `AstrBot Seedance`，按需要设置到期/限额；Allowed APIs 同时包含 `/seedance/videos` 和 `/seedance/tasks`。截图的 Dify tutorial 只是旧示例名称。

![创建专用 Key（共享 Ace 页面，非 AstrBot）](../_assets/tutorial/create-api-key-en.png)

图片于 2026-10-18 复用核验，原始拍摄日期未提供；凭据与余额已脱敏。 [来源和版本边界](../_assets/tutorial/sources.json)。

### 在 AstrBot 粘贴的位置

打开 **插件 → 插件 → 已安装**，点击 **Seedance by Ace Data Cloud** 卡片齿轮，把 Key 填入 **Ace Data Cloud generation API key with Seedance access**（保存字段为 `api_key`）并保存。不要填 `Bearer `；也不要在聊天里输入 Key。

![AstrBot 官方历史插件配置参考，非本插件运行截图](../_assets/tutorial/astrbot-plugin-config-reference.png)

此图是 AstrBot 官方 `helloworld` 配置示例，界面标签 v3.4.14（构建 v3.4.9），不是 Ace 配置或运行证明。上方说明给出了本插件的准确字段和当前菜单；新版本布局可能不同。

## 无需聊天模型的原生指令

| 输入 | 作用 |
| --- | --- |
| `/seedance_ace` | 显示本服务、Token 配置和查询用法，不请求外部 API。 |
| `/seedance_ace_task <task_id>` | 仅 AstrBot 管理员：查询一个已有任务，返回状态与最终媒体，不调用 LLM 或生成。 |

指令采用默认 `/` 前缀；自定义唤醒前缀时相应替换。管理员身份由 AstrBot 判断；同一实例的插件 Key 是共享配置，因此查询指令默认限管理员。其他用户继续使用受当前人格/配置允许的 Agent 工具。`pending` 时稍后只查同一编号，`failed` 时按原 task/trace 排查。

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
