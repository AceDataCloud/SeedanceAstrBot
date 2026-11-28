<!-- Generated from README.md by AceDataCloud/Index plans/plugin-readme-audit/render_channel_readmes.py. -->

# Seedance

<img src="../logo.png" width="96" height="96" alt="Seedance">

Submit one Seedance text or image video job in an AstrBot conversation, then query that same task for its final video URL through your own Ace Data Cloud account. The tools are `seedance_generate_video` and `seedance_get_task`.

This independent **Seedance integration is provided by Ace Data Cloud**. It is not an official plugin from the Seedance publisher or the AstrBot team. Use your own Ace account and API key.

[简体中文指南](README_zh_Hans.md) · [Seedance Videos API](https://platform.acedata.cloud/documents/seedance-videos?utm_source=github&utm_medium=referral&utm_campaign=evergreen) · [Seedance Tasks API](https://platform.acedata.cloud/documents/seedance-tasks?utm_source=github&utm_medium=referral&utm_campaign=evergreen) · [Current prices](https://platform.acedata.cloud/models?utm_source=github&utm_medium=referral&utm_campaign=evergreen)

## Find and install

Current upstream navigation (2026-10-18): **Plugins → Plugins → Plugin Market / Installed**. The earlier tested 4.28.2 English UI may label the section Extensions. Configure this service in the installed plugin gear; **do not paste its key into model-provider settings**.

Search the [AstrBot Cloud plugin market](https://cloud.astrbot.app/market) for **Seedance** and check the publisher `acedatacloud`.

To install from source, enter `https://github.com/AceDataCloud/SeedanceAstrBot` under **Plugins → Installed → Install Plugin (+) → Install from URL**.

## Configure your key

[Register or sign in to Ace](https://platform.acedata.cloud/console/applications?utm_source=github&utm_medium=referral&utm_campaign=evergreen) first. Open **General Application**. The following images show the shared Ace Applications page, not AstrBot.

In [Ace Data Cloud Applications](https://platform.acedata.cloud/console/applications?utm_source=github&utm_medium=referral&utm_campaign=evergreen), copy a generation API key from your General application or create a key that permits both `/seedance/videos` and `/seedance/tasks`. Check the current price for the selected model, resolution, and duration before submitting a video. Paste the key into the plugin's **Ace Data Cloud generation API key with Seedance access** setting. Do not add `Bearer ` or use a `platform-...` management token. AstrBot masks the field in WebUI but stores the original value in its data directory, which should be protected.

For Agent-tool use, select a chat model that supports tool calling. Allow both Seedance tools in the conversation's profile and persona.

1. Open **General application**. Use **1** to copy the existing key, or **2 Manage Keys → Create** for a dedicated key.

![Copy an Ace key or open Manage Keys (redacted)](../_assets/tutorial/get-api-key-en.png)

2. Use a name such as `AstrBot Seedance`. Set expiry/limits as needed and allow both `/seedance/videos` and `/seedance/tasks`. The screenshot’s Dify tutorial name is an older example.

![Create an optional dedicated key (shared Ace page, not AstrBot)](../_assets/tutorial/create-api-key-en.png)

Images reused and checked on 2026-10-18; original capture dates were not supplied. Credentials and balance are redacted. [Sources and version limits](../_assets/tutorial/sources.json).

### Where to paste it in AstrBot

Open **Plugins → Plugins → Installed**, select the gear on **Seedance**, paste the key into **Ace Data Cloud generation API key with Seedance access** (stored as `api_key`), and save. No `Bearer ` prefix; never paste the key in chat.

[AstrBot plugin configuration guide](https://docs.astrbot.app/en/dev/star/plugin-new.html)

## Native commands without a chat model

| Input | Result |
| --- | --- |
| `/seedance_ace` | Show service, Token setup and lookup help; no external API call. |
| `/seedance_ace_task <task_id>` | AstrBot administrators only: retrieve one existing task, with status/final media; no LLM or generation. |

Commands use the default `/` prefix; adapt it if your instance uses another wake prefix. AstrBot enforces administrator identity. The instance shares this plugin key, so direct lookup is administrator-only; other users use Agent tools allowed by their profile/persona. For `pending`, query the same ID later; for `failed`, inspect the original task/trace.

## Generate once, then query

For a short text-to-video request, ask:

> Use `seedance_generate_video` once for “A paper kite rises into a clear sky.” Choose model `doubao-seedance-2-0-mini-260615`, duration `4`, resolution `480p`, ratio `16:9`. Show me the task ID.

The tool sends one asynchronous `POST /seedance/videos` request and returns `status: submitted` with a task ID. The submit response is not a finished video. Keep the task ID and ask:

> Use `seedance_get_task` with the exact task ID `<task_id>`. Tell me whether it is pending, failed, or succeeded. Do not submit another video.

If pending, query the same ID later. Only `status: succeeded`, `success: true`, and a final HTTPS `video_url` mean the video is finished. The plugin never retries a paid submission automatically.

An optional authorized HTTPS `image_url` can serve as `first_frame` or `reference_image` for the 2.x models. This first version supports text video and one image reference; reference audio/video, edit/extend, 2.5 pure-audio workflows, and 1.x models are not included.

| Model | Duration | Resolution |
| --- | --- | --- |
| `doubao-seedance-2-0-260128` | 4–15 seconds | 480p, 720p, 1080p, 4k |
| `doubao-seedance-2-0-fast-260128` | 4–15 seconds | 480p, 720p |
| `doubao-seedance-2-0-mini-260615` | 4–15 seconds | 480p, 720p |
| `doubao-seedance-2-5-260628` | 4–30 seconds | 480p, 720p, 1080p |

## Verify and troubleshoot

### Cancelled tasks and interrupted waiting

An explicit failed/cancelled/rejected task is terminal: the plugin returns `status: failed`, `success: false` and no media, even if `finished_at` is still empty. It does not resubmit. Cancelling a local chat/command stops waiting locally; it does **not** cancel an upstream generation, and an already-started HTTP request may still finish. Inspect the original task/history and keep the same ID; there is no upstream-cancel command in this plugin.

In Ace Data Cloud usage, match a returned trace ID if present. If it is absent, API and time only correlate with a usage row. A task lookup retrieves the existing job; it does not submit another generation.

| Symptom | Check |
| --- | --- |
| Plugin fails to load | AstrBot version, **Failed to Load Plugins**, and **Data & Logs → Logs**. |
| Tools are missing | Plugin enabled, active profile and persona allow both tools, chat model supports tool calling. |
| HTTP 401/403 | Key type, both allowed API paths, and account access. |
| Network error after submission | Inspect request history before generating again; a timed-out request may have created a paid task. |
| Pending task | Query the same task ID later. |
| Failed task | Use its task or trace ID to inspect request history. |

The key goes only to `https://api.acedata.cloud`; redirects are rejected. The plugin exposes only task status and final video URL to the model, without internal provider data. It uses Python's standard library and needs no runtime package installation.

## Verified local run and brand asset

On official AstrBot `v4.28.2`, an isolated editable installation registered both tools. ChatUI submitted one supported `doubao-seedance-2-0-mini-260615` text video at 480p and four seconds, and later queried the same task ID through `seedance_get_task` without another generation. The terminal HTTPS MP4 responded HTTP 200, `video/mp4`; `ffprobe` decoded H.264 at 864×496 and 4.042 seconds. The exact generation trace matched a successful `/seedance/videos` usage row with 1.404 Credits deducted; the current cost rule computes 1.56 Credits before the account discount. See the [sanitized evidence](../tests/e2e-results.json). This is a local editable installation; official Cloud review, market installation, and a first call from a market installation remain open.

The plugin includes original 256×256 artwork. [SVG source](../_assets/artwork/logo.svg)

## Reproduce the no-cost host check

From this repository in an isolated Python 3.12 environment:

```bash
uv venv --python 3.12 .venv-host
uv pip install --python .venv-host/bin/python astrbot==4.29.0
.venv-host/bin/python scripts/verify_host.py
```

The check needs no API Key and starts no server. It imports real AstrBot
decorators, registers both commands/two tools, checks admin/non-admin access,
masked-key schema, missing-Key handling and cancellation propagation with
socket access blocked. Fake events and mocked cancellation do not establish
a full message-dispatcher, market install, live generation, task ownership,
new billing or signup/conversion result. Use normal `python -m pytest -q`
for transport and command regression tests.
