# CLI Reference

```
mediatools <command> [options]
```

All commands output **JSON by default**.  Add `--human` for readable text.
Errors always go to stderr.  Exit code `0` = success, `1` = error.

---

## probe

Show metadata for a media file.

```bash
mediatools probe <path>
```

**Example:**

```bash
mediatools probe video.mp4 --human
```

```
path:     video.mp4
duration: 183400 ms (183.40s)
format:   mov,mp4,m4a,3gp,3g2,mj2
size:     48,234,496 bytes
video:    h264 1920x1080
audio:    aac 44100Hz 2ch
```

---

## list-videos

Scan a directory and list all video files with metadata.

```bash
mediatools list-videos <directory> [options]
```

| Option | Default | Description |
| --- | --- | --- |
| `--sort-by` | `name` | `name`, `mtime`, `size`, or `duration` |
| `-r / --recursive` | off | Descend into subdirectories |

**Example:**

```bash
mediatools list-videos ./videos --sort-by name
```

```json
{
  "count": 3,
  "directory": "videos",
  "clips": [
    {"path": "videos/clip_a.mp4", "duration_ms": 12400, "size_bytes": 8200000,
     "resolution": "1920x1080", "fps": 30.0, "codec": "h264"},
    {"path": "videos/clip_b.mp4", "duration_ms": 9800, ...},
    {"path": "videos/clip_c.mp4", "duration_ms": 15200, ...}
  ]
}
```

---

## init-manifest

Scan a directory and write a `manifest.json` you can reorder before concatenating.

```bash
mediatools init-manifest <directory> [options]
```

| Option | Default | Description |
| --- | --- | --- |
| `--manifest` | `<dir>/manifest.json` | Output path for the manifest |
| `--output` | `<dir>/reel.mp4` | Output video path stored in manifest |
| `--sort-by` | `name` | Initial sort order |
| `-r / --recursive` | off | Scan subdirectories |

**Example:**

```bash
mediatools init-manifest ./videos
# → writes videos/manifest.json
# Edit the file to reorder clips, then:
mediatools concat videos/manifest.json
```

**manifest.json format:**

```json
{
  "output": "videos/reel.mp4",
  "clips": [
    {"path": "videos/clip_b.mp4", "duration_ms": 9800, "resolution": "1920x1080"},
    {"path": "videos/clip_a.mp4", "duration_ms": 12400, "resolution": "1920x1080"},
    {"path": "videos/clip_c.mp4", "duration_ms": 15200, "resolution": "1920x1080"}
  ]
}
```

Reorder the `"clips"` array, remove entries you don't want, then run `concat`.

---

## concat

Concatenate video files in order.  Accepts a file list or a `manifest.json`.

```bash
# From manifest (recommended):
mediatools concat manifest.json

# From file list:
mediatools concat clip1.mp4 clip2.mp4 clip3.mp4 --output reel.mp4
```

| Option | Default | Description |
| --- | --- | --- |
| `--output / -o` | from manifest | Output file (required for file list) |
| `--re-encode` | off | Re-encode to H.264/AAC — slower, required for mixed-format sources |

**Notes:**

- Default (`--re-encode` off) uses ffmpeg stream copy — fast and lossless, but all inputs must share the same codec, resolution, and frame rate.
- Use `--re-encode` when concatenating clips from different cameras or download sources.

**Example:**

```bash
# Full workflow: download → list → reorder → concat
mediatools pull-video "https://..." --output-dir ./videos
mediatools pull-video "https://..." --output-dir ./videos
mediatools init-manifest ./videos
# edit manifest.json …
mediatools concat ./videos/manifest.json
```

---

## clip

Trim a media file to a time range.

```bash
mediatools clip <input> <output> --start-ms <ms> --end-ms <ms>
```

| Option | Required | Description |
| --- | --- | --- |
| `--start-ms` | Yes | Start position in milliseconds |
| `--end-ms` | Yes | End position in milliseconds |

**Examples:**

```bash
# Clip from 30s to 1m15s
mediatools clip video.mp4 clip.mp4 --start-ms 30000 --end-ms 75000
```

---

## extract-frames

Extract frames from a video for analysis or assembly pipelines.

```bash
mediatools extract-frames <input> [options]
```

| Option | Default | Description |
| --- | --- | --- |
| `--output-dir` | `frames/` next to input | Destination folder |
| `--fps` | native fps | Frames per second to extract |
| `--start-ms` | — | Start of extraction window |
| `--end-ms` | — | End of extraction window |
| `--width` | original | Output width (`-1` = preserve aspect) |
| `--height` | original | Output height |
| `--fmt` | `png` | `png` (lossless) or `jpg` |

**Example:**

```bash
# 2 fps for motion analysis
mediatools extract-frames video.mp4 --fps 2 --output-dir frames/

# 1 frame per second, first 60 seconds, scaled for ML
mediatools extract-frames video.mp4 --fps 1 --end-ms 60000 --width 640 --height 360
```

Output JSON contains per-frame `path`, `index`, and `timestamp_ms`.

---

## thumbnails

Generate PNG thumbnails at regular intervals.

```bash
mediatools thumbnails <input> [options]
```

| Option | Default | Description |
| --- | --- | --- |
| `--output-dir` | `thumbnails/` next to input | Output folder |
| `--interval` | `15.0` | Seconds between thumbnails |
| `--zip` | off | Zip all thumbnails on completion |

---

## thumbnails-at

Extract a thumbnail at each timestamp from a JSON file.

```bash
mediatools thumbnails-at <input> <timestamps.json> [options]
```

| Option | Default | Description |
| --- | --- | --- |
| `--output-dir` | `thumbnails/` next to input | Output folder |
| `--timestamp-key` | `timestamps` | Key to read from the JSON file |
| `--zip` | off | Zip output |

**Timestamps JSON format:**

```json
{
  "timestamps": [
    {"ms": 0, "label": "intro"},
    {"ms": 30000, "label": "chapter-1"}
  ]
}
```

---

## extract-audio

Extract the audio stream from a media file.

```bash
mediatools extract-audio <input> <output> [options]
```

| Option | Default | Description |
| --- | --- | --- |
| `--sample-rate` | `44100` | Output sample rate in Hz |
| `--channels` | `2` | Number of channels (1=mono, 2=stereo) |

---

## convert

Convert media to an audio format.

```bash
mediatools convert <input> [output] [options]
```

| Option | Default | Description |
| --- | --- | --- |
| `--format` | `mp3` | `mp3`, `m4a`, `wav`, `flac`, `ogg`, `opus` |
| `--bitrate` | `320k` | Audio bitrate (ignored for lossless formats) |

---

## fetch-info

Fetch video metadata from a URL without downloading.

```bash
mediatools fetch-info <url>
```

Returns title, creator, duration, upload date, view count, license, and format list.

---

## pull-video

Download a video from a URL.

```bash
mediatools pull-video <url> [options]
```

| Option | Default | Description |
| --- | --- | --- |
| `--output-dir` | Platform Downloads | Destination folder |
| `--filename` | Video title | Output filename (no extension) |
| `--quality` | `bestvideo+bestaudio/best` | yt-dlp format selector |
| `--cookies` | — | Netscape cookies.txt file |
| `--cookies-from-browser` | — | `chrome`, `firefox`, `edge`, `safari` |

Also writes a `.credits.json` sidecar with full provenance.
