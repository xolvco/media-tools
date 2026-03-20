# CLI Reference

```
mediatools <command> [options]
```

---

## probe

Show metadata for a media file.

```bash
mediatools probe <path>
```

**Example:**

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

**Examples:**

```bash
mediatools pull-video "https://youtube.com/watch?v=..."
mediatools pull-video "https://youtube.com/watch?v=..." --output-dir ~/Videos
mediatools pull-video "https://youtube.com/watch?v=..." --cookies-from-browser chrome
mediatools pull-video "https://youtube.com/watch?v=..." --quality "bestaudio/best"
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

**Examples:**

```bash
mediatools extract-audio video.mp4 audio.wav
mediatools extract-audio video.mp4 audio.wav --sample-rate 48000 --channels 1
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

# Clip first 10 seconds
mediatools clip video.mp4 intro.mp4 --start-ms 0 --end-ms 10000
```
