# Pipeline Gap Analysis

Generated after: feat/pull-video initial implementation
Status: manual — updated at the end of each feature

---

## Implemented ✅

| Stage | What shipped |
| --- | --- |
| Python library | `probe`, `extract_audio`, `clip`, `pull_video`, `MediaFile` |
| Tests | 31 tests, all mocked (no real media files needed) |
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
