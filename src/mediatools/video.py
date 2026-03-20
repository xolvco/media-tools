"""Video clipping and frame extraction functions."""

from __future__ import annotations

import dataclasses
import subprocess
from pathlib import Path


class VideoError(RuntimeError):
    """Raised when a video operation fails."""


@dataclasses.dataclass
class FrameInfo:
    """Metadata for a single extracted frame."""
    path: Path
    index: int          # 1-based frame index within the extraction run
    timestamp_ms: int   # approximate presentation timestamp in milliseconds


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


def extract_frames(
    input: str | Path,
    output_dir: str | Path | None = None,
    *,
    fps: float | None = None,
    start_ms: int | None = None,
    end_ms: int | None = None,
    width: int | None = None,
    height: int | None = None,
    fmt: str = "png",
    timeout: float = 600.0,
) -> list[FrameInfo]:
    """Extract frames from a video for analysis or assembly pipelines.

    Suitable for feeding into optical flow, motion detection, keypoint
    tracking, or ML inference.  Output files are named
    ``frame_000001.png``, ``frame_000002.png``, etc.

    Args:
        input:      Source video file.
        output_dir: Destination folder (default: ``frames/`` next to *input*).
        fps:        Frames to extract per second.  ``None`` extracts every
                    native frame (potentially thousands — use with care for
                    long videos).  Set e.g. ``2.0`` for 2 fps analysis.
        start_ms:   Start of the extraction window in milliseconds.
        end_ms:     End of the extraction window in milliseconds.
        width:      Resize output width.  ``-1`` preserves aspect ratio.
        height:     Resize output height.  ``-1`` preserves aspect ratio.
        fmt:        Output format: ``"png"`` (lossless) or ``"jpg"``.
        timeout:    ffmpeg timeout in seconds.

    Returns:
        List of :class:`FrameInfo` objects sorted by frame index, each
        containing the output ``path``, 1-based ``index``, and
        ``timestamp_ms`` (approximate).

    Raises:
        FileNotFoundError: if *input* does not exist.
        ValueError: if *fmt* is unsupported, or start_ms >= end_ms.
        VideoError: if ffmpeg is not on PATH or returns an error.
    """
    input = Path(input)
    if not input.exists():
        raise FileNotFoundError(input)

    if fmt not in ("png", "jpg", "jpeg"):
        raise ValueError(f"fmt must be 'png' or 'jpg', got {fmt!r}")
    ext = "jpg" if fmt == "jpeg" else fmt

    if start_ms is not None and end_ms is not None and start_ms >= end_ms:
        raise ValueError(f"start_ms ({start_ms}) must be less than end_ms ({end_ms})")

    if output_dir is None:
        output_dir = input.parent / "frames"
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Resolve effective fps for timestamp computation
    effective_fps: float
    if fps is not None:
        effective_fps = fps
    else:
        from mediatools.probe import probe, ProbeError
        try:
            info = probe(input)
        except ProbeError as e:
            raise VideoError(f"Cannot probe {input}: {e}") from e
        vs = info.video_stream
        if vs is None or vs.fps is None:
            raise VideoError(f"{input} has no video stream with readable frame rate")
        effective_fps = vs.fps

    # Build ffmpeg filter chain
    filters: list[str] = []
    if fps is not None:
        filters.append(f"fps={fps}")
    if width is not None or height is not None:
        w = width if width is not None else -1
        h = height if height is not None else -1
        filters.append(f"scale={w}:{h}")

    cmd = ["ffmpeg", "-y"]
    if start_ms is not None:
        cmd += ["-ss", str(start_ms / 1000.0)]
    cmd += ["-i", str(input)]
    if end_ms is not None and start_ms is not None:
        cmd += ["-t", str((end_ms - start_ms) / 1000.0)]
    elif end_ms is not None:
        cmd += ["-to", str(end_ms / 1000.0)]
    if filters:
        cmd += ["-vf", ",".join(filters)]
    cmd += ["-an"]   # no audio track in frame output
    cmd += [str(output_dir / f"frame_%06d.{ext}")]

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

    base_ms = start_ms or 0
    frames: list[FrameInfo] = []
    for frame_path in sorted(output_dir.glob(f"frame_*.{ext}")):
        # frame_000001.png → index 1
        try:
            idx = int(frame_path.stem.split("_")[1])
        except (IndexError, ValueError):
            continue
        ts_ms = base_ms + round((idx - 1) / effective_fps * 1000)
        frames.append(FrameInfo(path=frame_path, index=idx, timestamp_ms=ts_ms))

    return frames
