# Assembling a Reel from Multiple Videos

This guide walks through the full workflow: download source clips, list them,
decide on order, and concatenate into a single output file.

---

## 1 — Download your source clips

```bash
mkdir ./videos
mediatools pull-video "https://youtube.com/watch?v=AAA" --output-dir ./videos
mediatools pull-video "https://youtube.com/watch?v=BBB" --output-dir ./videos
mediatools pull-video "https://youtube.com/watch?v=CCC" --output-dir ./videos
```

Each download also writes a `.credits.json` sidecar with title, creator, and
upload date for provenance tracking.

---

## 2 — List the videos

See what you have before ordering:

```bash
mediatools list-videos ./videos --human
```

Or in JSON (pipe-friendly):

```bash
mediatools list-videos ./videos | python3 -c "
import json,sys
for c in json.load(sys.stdin)['clips']:
    mins = c['duration_ms'] // 60000
    secs = (c['duration_ms'] % 60000) // 1000
    print(f\"{mins}:{secs:02d}  {c['path']}\")
"
```

---

## 3 — Generate a manifest

```bash
mediatools init-manifest ./videos
```

This writes `videos/manifest.json`:

```json
{
  "output": "videos/reel.mp4",
  "clips": [
    {"path": "videos/clip_a.mp4", "duration_ms": 12400, "resolution": "1920x1080"},
    {"path": "videos/clip_b.mp4", "duration_ms": 9800,  "resolution": "1920x1080"},
    {"path": "videos/clip_c.mp4", "duration_ms": 15200, "resolution": "1920x1080"}
  ]
}
```

---

## 4 — Reorder manually

Open `manifest.json` in any text editor and drag the entries into the order
you want.  You can also:

- Remove entries you don't want in the final reel
- Change `"output"` to a different filename
- Add a `"label"` field to any entry (informational, not used by concat)

```json
{
  "output": "videos/final_reel.mp4",
  "clips": [
    {"path": "videos/clip_b.mp4", "duration_ms": 9800},
    {"path": "videos/clip_a.mp4", "duration_ms": 12400},
    {"path": "videos/clip_c.mp4", "duration_ms": 15200}
  ]
}
```

---

## 5 — Concatenate

```bash
mediatools concat videos/manifest.json
```

Output: `videos/final_reel.mp4`

---

## Mixed sources (different codecs or resolutions)

If your clips came from different cameras or different download qualities,
stream copy will fail because the codecs don't match.  Use `--re-encode`:

```bash
mediatools concat videos/manifest.json --re-encode
```

This re-encodes everything to H.264 + AAC.  It takes longer but works with
any combination of source formats.

!!! tip
    For best quality during re-encode, normalize all clips to the same
    resolution first (coming soon: `mediatools normalize`).

---

## Python API

```python
from mediatools import list_videos, write_manifest, concat_videos

# List and write manifest
entries = list_videos("./videos", sort_by="name")
write_manifest(entries, "manifest.json", output_video="reel.mp4")

# (Human edits manifest.json here)

# Concatenate from manifest
output = concat_videos("manifest.json")
print(f"Saved to {output}")
```

Or fully programmatic (no manifest):

```python
from pathlib import Path
from mediatools import concat_videos

clips = sorted(Path("./videos").glob("*.mp4"))
output = concat_videos(clips, "reel.mp4")
```
