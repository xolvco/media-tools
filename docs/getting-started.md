# Getting Started

## Requirements

- Python 3.11 or later
- [ffmpeg](https://ffmpeg.org/download.html) installed and on your PATH
- For downloads: a logged-in browser (Chrome, Firefox, or Edge) **or** a cookies file

### Install ffmpeg

=== "Windows"
    ```powershell
    winget install ffmpeg
    ```

=== "macOS"
    ```bash
    brew install ffmpeg
    ```

=== "Linux"
    ```bash
    sudo apt install ffmpeg       # Debian/Ubuntu
    sudo dnf install ffmpeg       # Fedora
    ```

---

## Install mediatools

**Basic** (probe, clip, extract audio):

```bash
pip install git+https://github.com/xolvco/media-tools.git
```

**With download support** (adds yt-dlp):

```bash
pip install "git+https://github.com/xolvco/media-tools.git#egg=mediatools[download]"
```

Verify the install:

```bash
mediatools --help
```

---

## Your first download

```bash
mediatools pull-video "https://youtube.com/watch?v=dQw4w9WgXcQ" --cookies-from-browser chrome
```

This downloads the video to your Downloads folder and creates a `.credits.json` file next to it with the title, creator, upload date, and source URL.

---

## Your first probe

```bash
mediatools probe video.mp4
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

## Next steps

- [Downloading Videos](guide/pull-video.md) — quality, output folder, filenames
- [YouTube Authentication](guide/authentication.md) — handle age-restricted content
- [Shell Scripts](guide/scripts.md) — run without Python
