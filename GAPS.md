# Pipeline Gap Analysis

Generated after: feat/pull-video initial implementation
Status: manual — updated at the end of each feature

---

## Implemented ✅

| Stage | What shipped |
| --- | --- |
| Python library | `probe`, `extract_audio`, `clip`, `pull_video`, `convert_audio`, `generate_thumbnails`, `generate_thumbnails_at`, `extract_frames`, `list_videos`, `write_manifest`, `read_manifest`, `concat_videos`, `normalize_video`, `normalize_videos`, `MediaFile` |
| Tests | 114 tests, all mocked (no real media files needed) |
| CLI | All commands, JSON default output, `--human` flag |
| Shell scripts | `pull_video.sh` (bash), `pull_video.ps1` (PowerShell) — JSON-parsing, chainable |
| User docs | MkDocs site — getting started, guide, authentication, scripts, workflows, reference |
| Credits sidecar | `.credits.json` next to every downloaded file — full provenance |
| YouTube auth | `--cookies-from-browser` (live browser) + `--cookies` (exported file) |
| Audio-only download | `--quality "bestaudio/best"` — no video downloaded |

---

## Gaps — known, deferred

### Audio format conversion (--audio-format)

**What's missing:** yt-dlp can convert downloaded audio to mp3, m4a, flac, etc. via
ffmpeg post-processing. Currently the format is whatever the source serves (usually
.webm/Opus or .m4a/AAC).
**To do:** add `--audio-format mp3` option to `pull_video()` and CLI; set
`ydl_opts["postprocessors"]` with `FFmpegExtractAudio` when specified.

### extract_audio shell scripts

**What's missing:** `scripts/extract_audio.sh` and `scripts/extract_audio.ps1`
**To do:** follow same pattern as `pull_video` scripts; JSON output; chainable.

### clip shell scripts

**What's missing:** `scripts/clip.sh` and `scripts/clip.ps1`
**To do:** follow same pattern; accept `--start-ms` / `--end-ms`; JSON output.

### probe shell scripts

**What's missing:** `scripts/probe.sh` and `scripts/probe.ps1`
**To do:** follow same pattern; pipe-friendly; JSON output useful for feeding into clip/extract.

### Coverage gate

**What's missing:** `pytest --cov` with a minimum threshold in `pyproject.toml`
**To do:** run `pytest --cov=src/mediatools`, observe baseline, set threshold.

### CI workflow (GitHub Actions)

**What's missing:** no `.github/workflows/` — tests only run locally
**To do:** add `ci.yml` — lint (ruff) + test on push/PR; Linux/macOS/Windows matrix.

### Dependabot

**What's missing:** no `.github/dependabot.yml`
**To do:** weekly updates for pip + GitHub Actions.

### macOS / Linux package managers

**What's missing:** no Homebrew formula or apt/snap package
**Why deferred:** library-first; pip install from GitHub is sufficient for now.

### Progress output during download

**What's missing:** `pull_video()` is silent during long downloads (quiet=True)
**To do:** add optional `progress=True` param that enables yt-dlp progress hooks
printing to stderr; leave JSON stdout clean.

### Batch download function

**What's missing:** no `pull_videos(urls, ...)` for downloading a list
**To do:** thin wrapper over `pull_video` in a loop; returns `list[Path]`;
CLI: `mediatools pull-video --batch urls.txt`.

### Video validation and repair

**What's missing:** no way to check whether a video file is corrupt or truncated.
**To do:** `validate_video(path) -> ValidationResult` — runs ffprobe + a fast ffmpeg
decode pass; returns `{valid, errors, warnings, duration_ms, ...}`. If repair is
possible (missing moov atom, broken index), call `ffmpeg -i in -c copy out` (remux
without re-encode).  CLI: `mediatools validate video.mp4` / `mediatools repair video.mp4 out.mp4`.

### Video normalization (same size + aspect ratio)

**What's missing:** when assembling clips from multiple sources they often differ in
resolution, aspect ratio, FPS, and color space.
**To do:** `normalize_video(input, output, *, width, height, fps, ...)` — scales
(letterbox / crop / pad), sets FPS, converts color. Uses `-vf scale+pad` or
`-vf scale,setsar=1`. CLI: `mediatools normalize video.mp4 --width 1920 --height 1080 --fps 30`.

### Video concatenation with transitions

**What's missing:** no way to join multiple clips into one output.
**To do:** `concat_videos(inputs, output, *, gap_s=0, gap_fill="black"|"white"|Path) -> Path`.
Inserts a gap clip (solid color or image) of `gap_s` seconds between each input.
Output has chapter markers (ffmetadata) at each join point.
CLI: `mediatools concat clip1.mp4 clip2.mp4 clip3.mp4 --output reel.mp4 --gap-s 2 --gap-fill black`.

### Title cards

**What's missing:** formatted overlay or pre-clip with title text (product name, actor name, scene).
**To do:** `add_title_card(input, output, text, *, duration_s=3, font_size=48, ...)`.
Uses `ffmpeg drawtext` or prepends a generated title clip.  Can be composed with
`concat_videos` to produce `[title_card, clip1, title_card2, clip2, ...]`.

### "Interesting parts" detection

**What's missing:** no automated segment selection based on motion or audio energy.
This is the core of the forgegen use case: take a long video, find the high-motion
windows, extract them as clips for assembly.
**To do (two-stage approach):**

1. `extract_frames(fps=2.0)` — already shipped
2. `detect_motion_segments(frames, ...)` — compute frame-to-frame diff scores;
   return `list[Segment(start_ms, end_ms, score)]` ranked by activity
3. `select_best_segments(segments, ...)` — apply min_duration, max_count, dedup

**Dependencies:** numpy (frame diff), optional OpenCV for optical flow.

### Scripting external editors (DaVinci Resolve, Topaz, Premiere)

**What's missing:** no EDL/XML/script export for non-linear editors.
**To do (exploratory):**

- EDL export: CMX 3600 format; supported by Resolve, Premiere, Avid
- DaVinci Resolve scripting: Python API (`DaVinciResolveScript`); can import
  bins, create timelines, apply color grades
- Topaz Video AI: command-line `topazai` — enhance, upscale, slow-mo

**Approach:** generate a `resolve_script.py` from the assembled clip list;
user runs it inside Resolve.

### Agentic tool interface (v2)

**What's missing:** no formal tool schema (JSON Schema / OpenAI function format)
**Description:** each CLI command + library function needs a tool definition:
name, description, input params with types, output schema. This is what an LLM
agent uses to call the tool. The JSON default output is already step 1.
**To do:**

1. Add `mediatools tools` CLI command — prints all tool definitions as JSON
2. Add `src/mediatools/tools.py` — tool schema registry
3. Wire into an agent harness (Claude API tool use)

**Connection:** same pattern as FunscriptForge agentic CLI gap.

---

## Required before first release (v0.1.0)

- [ ] CI workflow passing on all three platforms
- [ ] Coverage baseline established
- [ ] `extract_audio` and `clip` shell scripts complete
- [ ] `--audio-format` option for audio-only downloads
- [ ] Dependabot configured
