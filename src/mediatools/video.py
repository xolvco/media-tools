"""Video clipping and processing functions."""

from __future__ import annotations

import subprocess
from pathlib import Path


class VideoError(RuntimeError):
    """Raised when a video operation fails."""


def clip(
    input: str | Path,
    output: str | Path,
    *,
    start_ms: int,
    end_ms: int,
    timeout: float = 120.0,
) -> Path:
    """Clip *input* from *start_ms* to *end_ms* and write to *output*.

    Uses stream copy where possible (no re-encode) for speed.

    Args:
        input:     Source media file.
        output:    Destination path — format inferred from extension.
        start_ms:  Start position in milliseconds.
        end_ms:    End position in milliseconds.
        timeout:   ffmpeg timeout in seconds.

    Returns:
        Path to the output file.

    Raises:
        FileNotFoundError: if *input* does not exist
        ValueError: if start_ms >= end_ms
        VideoError: if ffmpeg is not on PATH or returns an error
    """
    input = Path(input)
    output = Path(output)

    if not input.exists():
        raise FileNotFoundError(input)

    if start_ms >= end_ms:
        raise ValueError(f"start_ms ({start_ms}) must be less than end_ms ({end_ms})")

    output.parent.mkdir(parents=True, exist_ok=True)

    start_s = start_ms / 1000.0
    duration_s = (end_ms - start_ms) / 1000.0

    cmd = [
        "ffmpeg", "-y",
        "-ss", str(start_s),
        "-i", str(input),
        "-t", str(duration_s),
        "-c", "copy",              # stream copy — fast, no re-encode
        str(output),
    ]

    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, timeout=timeout
        )
    except FileNotFoundError:
        raise VideoError("ffmpeg not found — install ffmpeg and ensure it is on PATH")
    except subprocess.TimeoutExpired:
        raise VideoError(f"ffmpeg timed out after {timeout}s")

    if result.returncode != 0:
        raise VideoError(f"ffmpeg error: {result.stderr[-500:]}")

    return output
