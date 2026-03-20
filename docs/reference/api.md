# Python API Reference

## mediatools.pull_video

```python
from mediatools import pull_video

pull_video(
    url,
    output_dir=None,
    *,
    filename=None,
    quality="bestvideo+bestaudio/best",
    timeout=300.0,
    cookies=None,
    cookies_from_browser=None,
) -> Path
```

Download a video from *url* to *output_dir*.

| Parameter | Type | Default | Description |
| --- | --- | --- | --- |
| `url` | `str` | required | Video URL |
| `output_dir` | `str \| Path \| None` | Platform Downloads | Destination folder |
| `filename` | `str \| None` | Video title | Output filename without extension |
| `quality` | `str` | `"bestvideo+bestaudio/best"` | yt-dlp format selector |
| `timeout` | `float` | `300.0` | Socket timeout in seconds |
| `cookies` | `str \| Path \| None` | `None` | Path to Netscape cookies.txt |
| `cookies_from_browser` | `str \| None` | `None` | Browser name: `"chrome"`, `"firefox"`, `"edge"`, `"safari"` |

Returns the `Path` to the downloaded file. Also writes a `.credits.json` sidecar.

Raises `DownloadError` if yt-dlp is not installed or the download fails.

---

## mediatools.MediaFile

```python
from mediatools import MediaFile

mf = MediaFile(path)
```

Wraps a media file and provides lazy-cached metadata and operations.

| Property / Method | Type | Description |
| --- | --- | --- |
| `mf.path` | `Path` | Absolute path to the file |
| `mf.duration_ms` | `int` | Duration in milliseconds |
| `mf.duration_s` | `float` | Duration in seconds |
| `mf.has_video` | `bool` | Has a video stream |
| `mf.has_audio` | `bool` | Has an audio stream |
| `mf.size_bytes` | `int` | File size in bytes |
| `mf.info` | `ProbeResult` | Full probe result (lazy, cached) |
| `mf.extract_audio(output, **kwargs)` | `Path` | Extract audio stream |
| `mf.clip(output, start_ms, end_ms, **kwargs)` | `Path` | Clip to time range |

---

## mediatools.probe

```python
from mediatools import probe

result = probe(path, timeout=10.0) -> ProbeResult
```

Run ffprobe on *path* and return structured metadata.

### ProbeResult

| Attribute | Type | Description |
| --- | --- | --- |
| `path` | `Path` | File path |
| `duration_s` | `float` | Duration in seconds |
| `duration_ms` | `int` | Duration in milliseconds |
| `format_name` | `str` | Container format |
| `size_bytes` | `int` | File size |
| `streams` | `list[StreamInfo]` | Audio and video streams |
| `has_video` | `bool` | |
| `has_audio` | `bool` | |
| `video_stream` | `StreamInfo \| None` | First video stream |
| `audio_stream` | `StreamInfo \| None` | First audio stream |

---

## mediatools.audio.extract_audio

```python
from mediatools.audio import extract_audio

extract_audio(input, output, *, sample_rate=44100, channels=2, timeout=120.0) -> Path
```

---

## mediatools.video.clip

```python
from mediatools.video import clip

clip(input, output, *, start_ms, end_ms, timeout=120.0) -> Path
```

Uses ffmpeg stream copy (no re-encode) for fast, lossless trimming.
