# Backlog

Features and improvements in priority order.
Items at the top are closest to ready. Items at the bottom are future/exploratory.

---

## Ready to build

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
