# Python API Reference

---

## Downloading

### `pull_video`

```python
from mediatools import pull_video

path = pull_video(
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

Download a video to *output_dir*.  Writes a `.credits.json` sidecar.
Raises `DownloadError` if yt-dlp is not installed or the download fails.

---

### `fetch_info`

```python
from mediatools import fetch_info

info = fetch_info(url) -> dict
```

Fetch metadata from *url* without downloading.  Returns a dict with
`title`, `creator`, `duration_s`, `upload_date`, `tags`, `view_count`, and `formats`.

---

## Listing and Assembly

### `list_videos`

```python
from mediatools import list_videos

entries = list_videos(
    directory,
    *,
    recursive=False,
    extensions=None,       # defaults to common video extensions
    sort_by="name",        # "name" | "mtime" | "size" | "duration"
) -> list[VideoEntry]
```

Scan *directory* for video files and return metadata for each.
Files that cannot be probed are skipped (warning printed to stderr).

#### `VideoEntry`

| Field | Type | Description |
| --- | --- | --- |
| `path` | `Path` | Absolute path to the file |
| `duration_ms` | `int` | Duration in milliseconds |
| `size_bytes` | `int` | File size |
| `width` | `int \| None` | Video width |
| `height` | `int \| None` | Video height |
| `fps` | `float \| None` | Frame rate |
| `codec` | `str \| None` | Video codec name |

---

### `write_manifest`

```python
from mediatools import write_manifest

manifest_path = write_manifest(
    entries,           # list[VideoEntry] or list[Path]
    manifest_path,
    *,
    output_video=None, # default: reel.mp4 next to manifest
) -> Path
```

Write a human-editable `manifest.json` listing clips in order.
Edit the `"clips"` array to reorder, add, or remove clips before concatenating.

---

### `read_manifest`

```python
from mediatools import read_manifest

clips, output = read_manifest(manifest_path) -> tuple[list[Path], Path]
```

Read a manifest back.  Returns ordered clip paths and the output video path.

---

### `concat_videos`

```python
from mediatools import concat_videos

output = concat_videos(
    inputs,            # list[Path] or path to manifest.json
    output=None,       # required for list; manifest supplies default
    *,
    re_encode=False,   # True = H.264/AAC, works with mixed sources
    timeout=3600.0,
) -> Path
```

Concatenate clips into a single output using ffmpeg concat demuxer.

- `re_encode=False` — stream copy, fast and lossless.  All inputs must share the same codec, resolution, and frame rate.
- `re_encode=True` — re-encode to H.264 + AAC.  Handles mixed sources at the cost of processing time.

**Typical workflow:**

```python
from mediatools import list_videos, write_manifest, concat_videos

entries = list_videos("./videos")
write_manifest(entries, "manifest.json")

# Human edits manifest.json to reorder …

output = concat_videos("manifest.json")
print(output)  # videos/reel.mp4
```

---

## Frame Extraction

### `extract_frames`

```python
from mediatools import extract_frames

frames = extract_frames(
    input,
    output_dir=None,   # default: frames/ next to input
    *,
    fps=None,          # None = native fps; e.g. 2.0 = 2 frames/sec
    start_ms=None,
    end_ms=None,
    width=None,        # -1 = preserve aspect
    height=None,
    fmt="png",         # "png" or "jpg"
    timeout=600.0,
) -> list[FrameInfo]
```

Extract frames for motion analysis, ML inference, or assembly pipelines.

#### `FrameInfo`

| Field | Type | Description |
| --- | --- | --- |
| `path` | `Path` | Path to the extracted frame file |
| `index` | `int` | 1-based frame index |
| `timestamp_ms` | `int` | Approximate presentation timestamp |

---

## Thumbnails

### `generate_thumbnails`

```python
from mediatools import generate_thumbnails

paths = generate_thumbnails(
    input,
    output_dir=None,   # default: thumbnails/ next to input
    *,
    interval_s=15.0,
    zip_output=False,
) -> list[Path] | Path
```

---

### `generate_thumbnails_at`

```python
from mediatools import generate_thumbnails_at

paths = generate_thumbnails_at(
    input,
    timestamps,        # list[int] (ms) or Path to JSON file
    output_dir=None,
    *,
    timestamp_key="timestamps",
    zip_output=False,
) -> list[Path] | Path
```

**JSON file format:**

```json
{
  "timestamps": [
    {"ms": 0, "label": "intro"},
    {"ms": 30000, "label": "chapter-1"}
  ]
}
```

---

## Audio

### `extract_audio`

```python
from mediatools.audio import extract_audio

extract_audio(input, output, *, sample_rate=44100, channels=2, timeout=120.0) -> Path
```

---

### `convert_audio` / `convert_to_mp3`

```python
from mediatools import convert_audio, convert_to_mp3

convert_audio(input, output=None, *, fmt="mp3", bitrate=None, timeout=120.0) -> Path
convert_to_mp3(input, output=None, *, bitrate="320k", timeout=120.0) -> Path
```

Supported formats: `mp3`, `m4a`, `wav`, `flac`, `ogg`, `opus`.

---

## Clipping

### `clip`

```python
from mediatools.video import clip

clip(input, output, *, start_ms, end_ms, timeout=120.0) -> Path
```

Uses ffmpeg stream copy (no re-encode) for fast, lossless trimming.

---

## Probing

### `probe`

```python
from mediatools import probe

result = probe(path, timeout=10.0) -> ProbeResult
```

#### `ProbeResult`

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

#### `StreamInfo`

| Attribute | Type | Description |
| --- | --- | --- |
| `codec_type` | `str` | `"video"` or `"audio"` |
| `codec_name` | `str` | e.g. `"h264"`, `"aac"` |
| `width` | `int \| None` | Video width |
| `height` | `int \| None` | Video height |
| `fps` | `float \| None` | Frame rate (video only) |
| `sample_rate` | `int \| None` | Audio sample rate |
| `channels` | `int \| None` | Audio channel count |

---

## MediaFile

```python
from mediatools import MediaFile

mf = MediaFile(path)
```

Wraps a media file with lazy-cached metadata and convenience methods.

| Property / Method | Returns | Description |
| --- | --- | --- |
| `mf.path` | `Path` | File path |
| `mf.duration_ms` | `int` | Duration in milliseconds |
| `mf.duration_s` | `float` | Duration in seconds |
| `mf.has_video` | `bool` | Has video stream |
| `mf.has_audio` | `bool` | Has audio stream |
| `mf.size_bytes` | `int` | File size |
| `mf.info` | `ProbeResult` | Full probe result (lazy) |
| `mf.extract_audio(output, **kw)` | `Path` | Extract audio stream |
| `mf.clip(output, start_ms, end_ms)` | `Path` | Trim to time range |
| `mf.extract_frames(output_dir, **kw)` | `list[FrameInfo]` | Extract frames |
| `mf.generate_thumbnails(output_dir, **kw)` | `list[Path]` | Thumbnails at intervals |
| `mf.generate_thumbnails_at(timestamps, **kw)` | `list[Path]` | Thumbnails at timestamps |
| `mf.convert_to_mp3(output, **kw)` | `Path` | Convert to MP3 |
| `mf.convert_audio(output, fmt, **kw)` | `Path` | Convert to audio format |
