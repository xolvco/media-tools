# Downloading Videos

`pull_video` downloads a video from YouTube, Vimeo, or any of the [1000+ sites supported by yt-dlp](https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md) and saves it to your local filesystem.

Every download produces two files:

- `<title>.mp4` — the video
- `<title>.credits.json` — provenance: source URL, creator, upload date, license, tags

---

## CLI

```bash
mediatools pull-video <url> [options]
```

### Options

| Option | Default | Description |
| --- | --- | --- |
| `--output-dir` | Platform Downloads folder | Where to save the file |
| `--filename` | Video title | Output filename (no extension) |
| `--quality` | `bestvideo+bestaudio/best` | yt-dlp format selector |
| `--cookies` | — | Path to a Netscape cookies.txt file |
| `--cookies-from-browser` | — | Browser to extract cookies from |

---

## Examples

### Download to the default Downloads folder

```bash
mediatools pull-video "https://youtube.com/watch?v=dQw4w9WgXcQ"
```

### Download to a specific folder

```bash
mediatools pull-video "https://youtube.com/watch?v=dQw4w9WgXcQ" \
  --output-dir ~/Videos/research
```

### Download with a specific filename

```bash
mediatools pull-video "https://youtube.com/watch?v=dQw4w9WgXcQ" \
  --output-dir ~/Videos \
  --filename "rick-astley-never-gonna-give-you-up"
```

### Download audio-only (best audio quality)

```bash
mediatools pull-video "https://youtube.com/watch?v=dQw4w9WgXcQ" \
  --quality "bestaudio/best"
```

### Download at a specific resolution

```bash
# Best video up to 1080p
mediatools pull-video "https://youtube.com/watch?v=dQw4w9WgXcQ" \
  --quality "bestvideo[height<=1080]+bestaudio/best"

# 720p only
mediatools pull-video "https://youtube.com/watch?v=dQw4w9WgXcQ" \
  --quality "bestvideo[height=720]+bestaudio"
```

### Download with authentication (age-restricted / members-only)

```bash
mediatools pull-video "https://youtube.com/watch?v=..." \
  --cookies-from-browser chrome
```

See [YouTube Authentication](authentication.md) for full details.

---

## Python API

```python
from mediatools import pull_video
from pathlib import Path

# Basic download — saves to ~/Downloads
path = pull_video("https://youtube.com/watch?v=dQw4w9WgXcQ")
print(path)  # /home/user/Downloads/Rick Astley - Never Gonna Give You Up.mp4

# Custom output folder
path = pull_video(
    "https://youtube.com/watch?v=dQw4w9WgXcQ",
    output_dir=Path("~/Videos/research").expanduser(),
)

# Custom filename
path = pull_video(
    "https://youtube.com/watch?v=dQw4w9WgXcQ",
    output_dir="~/Videos",
    filename="rick-astley",
)

# Audio only
path = pull_video(
    "https://youtube.com/watch?v=dQw4w9WgXcQ",
    quality="bestaudio/best",
)

# With authentication
path = pull_video(
    "https://youtube.com/watch?v=...",
    cookies_from_browser="chrome",
)

# With cookies file
path = pull_video(
    "https://youtube.com/watch?v=...",
    cookies="~/youtube-cookies.txt",
)
```

---

## The credits file

Every download produces a `.credits.json` sidecar file with provenance information:

```json
{
  "filename": "Rick Astley - Never Gonna Give You Up.mp4",
  "source_url": "https://youtube.com/watch?v=dQw4w9WgXcQ",
  "downloaded_at": "2026-03-19T14:23:01+00:00",
  "title": "Rick Astley - Never Gonna Give You Up (Official Music Video)",
  "creator": {
    "uploader": "Rick Astley",
    "uploader_url": "https://www.youtube.com/@RickAstleyYT",
    "channel": "Rick Astley",
    "channel_url": "https://www.youtube.com/channel/UCuAXFkgsw1L7xaCfnd5JJOw"
  },
  "upload_date": "20091025",
  "duration_s": 213.0,
  "description": "The official video for ...",
  "webpage_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
  "extractor": "youtube",
  "tags": ["rick astley", "never gonna give you up"],
  "view_count": 1500000000,
  "like_count": 16000000
}
```

Use this file for attribution, compliance, or to feed metadata into downstream tools.

---

## Supported sites

Any site supported by yt-dlp works — YouTube, Vimeo, Twitch, Twitter/X, TikTok, SoundCloud, and [1000+ more](https://github.com/yt-dlp/yt-dlp/blob/master/supportedsites.md).

!!! note
    Authentication (cookies) is primarily a YouTube requirement. Most other sites work without it.
