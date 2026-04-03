# mediatools

`mediatools` is now a deprecated compatibility wrapper around `videoedit`.

Use `videoedit` for new work:

- repo: `https://github.com/xolvco/videoedit`
- package: `videoedit`

This repo continues to exist so older imports and scripts keep working during the migration, but it is no longer the canonical implementation.

## Install

```bash
pip install git+https://github.com/xolvco/media-tools.git
```

**Requires:** ffmpeg on PATH.

## Usage

### Python API

Compatibility import:

```python
from mediatools import MediaFile
```

Preferred new import:

```python
from videoedit.media import MediaFile
```

### CLI

Compatibility commands still work:

```bash
mediatools probe video.mp4
mediatools extract-audio video.mp4 audio.wav
mediatools clip video.mp4 clip.mp4 --start-ms 30000 --end-ms 75000
```

## Compatibility policy

- compatibility is still maintained for now
- new behavior should land in `videoedit`, not here
- this repo should stay small and wrapper-focused

## License

MIT - see [LICENSE](LICENSE).
