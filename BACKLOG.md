# Backlog

Features and improvements in priority order.
Items at the top are closest to ready. Items at the bottom are future/exploratory.

---

## Ready to build

### Video validation and repair

Check whether a video file is corrupt, truncated, or has a broken index.
Attempt remux repair (no re-encode) where possible.

```python
from mediatools.video import validate_video, repair_video

result = validate_video("clip.mp4")
# {"valid": False, "errors": ["moov atom missing"], "duration_ms": 0}

repair_video("clip.mp4", "clip_fixed.mp4")
```

CLI:
```bash
mediatools validate clip.mp4
mediatools repair clip.mp4 clip_fixed.mp4
```

---

### Video normalization

Normalize resolution, aspect ratio, FPS, and pixel format across multiple source
clips before concatenation. Uses letterbox/pad to avoid distortion.

```python
from mediatools.video import normalize_video

normalize_video("clip.mp4", "clip_norm.mp4", width=1920, height=1080, fps=30)
```

CLI:
```bash
mediatools normalize clip.mp4 --width 1920 --height 1080 --fps 30
```

---

### Video concatenation with gap and markers

Join multiple normalized clips into one output. Optional gap clip (solid color or
image) between each source. Writes ffmetadata chapter markers at each join point.

```python
from mediatools.video import concat_videos

concat_videos(
    ["clip1.mp4", "clip2.mp4", "clip3.mp4"],
    "reel.mp4",
    gap_s=2.0,
    gap_fill="black",   # "black", "white", or Path to image
)
```

CLI:
```bash
mediatools concat clip1.mp4 clip2.mp4 clip3.mp4 \
  --output reel.mp4 --gap-s 2 --gap-fill black
```

Returns `{output, duration_ms, segment_count, markers: [{label, start_ms}]}`.

---

### Title cards

Prepend a formatted title clip to each source segment before concatenation.
Uses `ffmpeg drawtext` or generates a solid-color clip with text overlay.

```python
from mediatools.video import add_title_card

add_title_card("clip.mp4", "clip_titled.mp4", text="VictoriaOaks — Scene 3",
               duration_s=3, font_size=48)
```

Composable with `concat_videos`: build `[title1, clip1, title2, clip2, ...]` then concat.

---

### Audio format conversion

Add `--audio-format` to `pull_video()` so users can request mp3, m4a, flac, wav
directly without a separate extract step.

```bash
mediatools pull-video "https://..." --quality "bestaudio/best" --audio-format mp3
```

Uses yt-dlp's built-in `FFmpegExtractAudio` postprocessor. Requires ffmpeg on PATH
(already a project requirement).

---

### Shell scripts for extract_audio and clip

Complete the script set so all CLI commands have bash + PowerShell wrappers.
Required before the workflow chaining examples in the docs are fully demonstrable.

- `scripts/extract_audio.sh` / `scripts/extract_audio.ps1`
- `scripts/clip.sh` / `scripts/clip.ps1`
- `scripts/probe.sh` / `scripts/probe.ps1`

---

### CI workflow

`.github/workflows/ci.yml` — lint + test on push/PR, Linux/macOS/Windows matrix.
Blocks bad merges, proves cross-platform compatibility.

---

### Batch download

```python
pull_videos(["url1", "url2", ...], output_dir="~/Videos")
```

CLI:
```bash
mediatools pull-video --batch urls.txt --output-dir ~/Videos
```

Returns `list[Path]`. Each download gets its own `.credits.json`.

---

### Progress reporting

Silent downloads are frustrating for large files. Add optional progress to stderr:

```python
pull_video(url, progress=True)   # prints progress bar to stderr, JSON still on stdout
```

---

## Near-term

### Playlist / channel download

Download all videos from a YouTube playlist or channel:

```bash
mediatools pull-playlist "https://youtube.com/playlist?list=..."
```

Returns a manifest JSON: `{playlist_title, count, paths: [...]}`.
Each video gets its credits file. yt-dlp handles pagination natively.

---

### Subtitle download

Download subtitles/captions alongside the video:

```bash
mediatools pull-video "https://..." --subtitles --subtitle-lang en
```

Writes `<title>.en.vtt` (or `.srt`). Also includes subtitle metadata in the
credits file.

---

### Thumbnail download

Save the video thumbnail as `<title>.jpg`:

```bash
mediatools pull-video "https://..." --thumbnail
```

Useful for building catalogs, metadata displays, or training data pipelines.

---

### Video resolution info in probe output

`probe` currently reports `width x height` but not frame rate or bit rate.
Add `fps`, `bit_rate` to `StreamInfo` and probe output.

---

## Future / exploratory

### "Interesting parts" detection (forgegen integration)

Given a set of source videos, find high-motion or high-energy windows automatically.
Feed the results directly into `concat_videos` to produce a highlights reel without
manual editing.

```python
from mediatools.video import extract_frames, detect_motion_segments, select_best_segments

frames = extract_frames("long_video.mp4", fps=2.0)
segments = detect_motion_segments(frames)
best = select_best_segments(segments, max_count=10, min_duration_ms=3000)
# best = [Segment(start_ms=12400, end_ms=18700, score=0.87), ...]
```

Then `clip()` each segment and `concat_videos()` the results.
**Dependencies:** numpy for frame diff; optional OpenCV for optical flow.

---

### External editor scripting (DaVinci Resolve, Topaz, Premiere)

Generate EDL (CMX 3600) or DaVinci Resolve Python scripts from a clip list.
Enables taking a media-tools assembly into a full NLE for color grading,
effects, or Topaz Video AI upscaling.

```python
from mediatools.export import to_edl, to_resolve_script

to_edl(clip_list, "assembly.edl")
to_resolve_script(clip_list, "import_into_resolve.py")
```

---

### Agentic tool interface (v2)

Make every library function callable by an LLM agent via tool use.

Steps:
1. `src/mediatools/tools.py` — JSON Schema tool definitions for each function
2. `mediatools tools` CLI — prints all definitions (agent discovery)
3. Agent harness — accepts natural language goal, plans + executes tool calls
   via Claude API

Example agent goal: `"Download this video, extract the audio, and clip it to
the section between 1:30 and 2:45."` → agent calls `pull_video`, `clip`, `extract_audio`
in sequence, returns all three paths.

This is the same pattern as FunscriptForge's agentic CLI gap. Both repos converge
on the same tool-calling interface.

---

### Streaming download (no temp file)

For large files where disk space matters: stream directly to the next operation
without writing the full video to disk first. Complex with yt-dlp internals but
valuable for server/pipeline use.

---

### Cloud storage output

Write directly to S3, GCS, or Azure Blob instead of a local folder:

```python
pull_video(url, output_dir="s3://my-bucket/videos/")
```

---

### Content fingerprinting

Add a `sha256` hash of the downloaded file to the credits JSON.
Enables de-duplication and integrity verification in batch workflows.

---

### Carta integration

Ingest credits files into Carta as knowledge base entries. Each downloaded video
becomes a searchable record: title, creator, tags, description, transcript (if
subtitles downloaded). Enables querying a video library with natural language.
