# mediatools

Reusable media processing utilities built on [ffmpeg](https://ffmpeg.org) and [yt-dlp](https://github.com/yt-dlp/yt-dlp).

Use it as a **Python library**, a **CLI tool**, or via ready-made **shell scripts** you can chain into workflows.

---

## What it does

| Capability | Description |
| --- | --- |
| `probe` | Read metadata from any media file — duration, codec, resolution, streams |
| `pull_video` | Download a video from YouTube, Vimeo, or 1000+ other sites |
| `extract_audio` | Extract the audio stream from any video file |
| `clip` | Trim a video to a time range (stream copy — no re-encode) |

---

## Quick install

```bash
pip install git+https://github.com/xolvco/media-tools.git
```

With download support:

```bash
pip install "git+https://github.com/xolvco/media-tools.git#egg=mediatools[download]"
```

**Requires:** [ffmpeg](https://ffmpeg.org/download.html) on PATH.

---

## Quick example

```python
from mediatools import pull_video, MediaFile

# Download a video
path = pull_video("https://youtube.com/watch?v=...", cookies_from_browser="chrome")

# Inspect it
mf = MediaFile(path)
print(mf.duration_ms)   # 183400
print(mf.has_audio)     # True

# Extract audio
mf.extract_audio("audio.wav")
```

---

## Next steps

- [Getting Started](getting-started.md) — install, first download
- [Downloading Videos](guide/pull-video.md) — all options
- [YouTube Authentication](guide/authentication.md) — handle age-restricted and members-only content
- [Shell Scripts](guide/scripts.md) — ready-made bash and PowerShell scripts
- [Chaining Workflows](guide/workflows.md) — combine scripts into automated pipelines
