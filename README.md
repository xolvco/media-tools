# mediatools

Reusable media processing utilities built on ffmpeg/ffprobe.

## Install

```bash
pip install git+https://github.com/xolvco/media-tools.git
```

**Requires:** ffmpeg on PATH.

## Usage

### Python API

```python
from mediatools import MediaFile

mf = MediaFile("video.mp4")
print(mf.duration_ms)       # 183400
print(mf.has_audio)         # True

mf.extract_audio("audio.wav")
mf.clip("clip.mp4", start_ms=30_000, end_ms=75_000)
```

### CLI

```bash
mediatools probe video.mp4
mediatools extract-audio video.mp4 audio.wav
mediatools clip video.mp4 clip.mp4 --start-ms 30000 --end-ms 75000
```

## License

MIT — see [LICENSE](LICENSE).
