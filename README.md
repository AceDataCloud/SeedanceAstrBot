# Seedance for AstrBot

Submit one Seedance text or image video job in an AstrBot conversation, then query that same task for its final video URL through your own Ace Data Cloud account. The tools are `seedance_generate_video` and `seedance_get_task`.

[简体中文指南](readme/README_zh_Hans.md) · [Seedance Videos API](https://platform.acedata.cloud/documents/seedance-videos?utm_source=opensource&utm_medium=referral&utm_campaign=evergreen&utm_content=seedanceastrbot_readme_documents_seedance_videos) · [Seedance Tasks API](https://platform.acedata.cloud/documents/seedance-tasks?utm_source=opensource&utm_medium=referral&utm_campaign=evergreen&utm_content=seedanceastrbot_readme_documents_seedance_tasks) · [Current prices](https://platform.acedata.cloud/models?utm_source=opensource&utm_medium=referral&utm_campaign=evergreen&utm_content=seedanceastrbot_readme_pricing)

## Find and install

In AstrBot WebUI, open **Extensions → Plugins → AstrBot Plugin Market** and search **Seedance**. Confirm the card says **Seedance by Ace Data Cloud**, the author is **acedatacloud**, and the logo matches the [Seedance service icon](https://cdn.acedata.cloud/9q90dl.png). Install it, then check **Installed** for load errors.

The official AstrBot Cloud listing has not yet been published. After the source release is merged, **Installed → Install (+) → Install from URL** with `https://github.com/AceDataCloud/SeedanceAstrBot` can preview it. A URL installation is not an official market installation.

## Configure your key

New account? Register and sign in first. If the Applications page has no General application yet, choose **Initialize General Application**, then continue with the key steps below.

In [Ace Data Cloud Applications](https://platform.acedata.cloud/console/applications?utm_source=opensource&utm_medium=referral&utm_campaign=evergreen&utm_content=seedanceastrbot_readme_api_key), copy a generation API key from your General application or create a key that permits both `/seedance/videos` and `/seedance/tasks`. Check the current price for the selected model, resolution, and duration before submitting a video. Paste the key into the plugin's **Ace Data Cloud generation API key with Seedance access** setting. Do not add `Bearer ` or use a `platform-...` management token. AstrBot masks the field in WebUI but stores the original value in its data directory, which should be protected.

Select a chat model that supports tool calling. Allow both Seedance tools in the conversation's profile and persona.

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

On official AstrBot `v4.28.2`, an isolated editable installation registered both tools. ChatUI submitted one supported `doubao-seedance-2-0-mini-260615` text video at 480p and four seconds, and later queried the same task ID through `seedance_get_task` without another generation. The terminal HTTPS MP4 responded HTTP 200, `video/mp4`; `ffprobe` decoded H.264 at 864×496 and 4.042 seconds. The exact generation trace matched a successful `/seedance/videos` usage row with 1.404 Credits deducted; the current cost rule computes 1.56 Credits before the account discount. See the [sanitized evidence](tests/e2e-results.json). This is a local editable installation; official Cloud review, market installation, and a first call from a market installation remain open.

`logo.png` is the unmodified 200×200 [current Seedance service icon](https://cdn.acedata.cloud/9q90dl.png), SHA-256 `6a5b07c1d33d2910eb9fe1c8549874a004d13a0e75d9b30a7cfdc255c586a83d`.
