"""Thumbnail generation — extract PNG frames from a video at regular intervals."""

from __future__ import annotations

import subprocess
import zipfile
from pathlib import Path


class ThumbnailError(RuntimeError):
    """Raised when thumbnail generation fails."""


def generate_thumbnails(
    input: str | Path,
    output_dir: str | Path | None = None,
    *,
    interval_s: float = 15.0,
    zip_output: bool = False,
    timeout: float = 300.0,
) -> list[Path] | Path:
    """Extract PNG thumbnails from *input* at every *interval_s* seconds.

    Args:
        input:       Source video file.
        output_dir:  Destination folder.  Defaults to a ``thumbnails/`` subfolder
                     next to the input file.
        interval_s:  Seconds between thumbnails.  Default: 15.
        zip_output:  If True, zip all thumbnails into ``<stem>-thumbnails.zip``
                     in *output_dir* and return the zip path instead of the list.
        timeout:     ffmpeg timeout in seconds.

    Returns:
        List of Paths to generated PNG files, or a single Path to the zip file
        if *zip_output* is True.

    Raises:
        FileNotFoundError: if *input* does not exist
        ThumbnailError: if ffmpeg is not on PATH or extraction fails
    """
    input = Path(input)
    if not input.exists():
        raise FileNotFoundError(input)

    if output_dir is None:
        output_dir = input.parent / "thumbnails"
    else:
        output_dir = Path(output_dir)

    output_dir.mkdir(parents=True, exist_ok=True)

    # Output pattern: <stem>_0001.png, <stem>_0002.png, ...
    pattern = output_dir / f"{input.stem}_%04d.png"

    cmd = [
        "ffmpeg", "-y",
        "-i", str(input),
        "-vf", f"fps=1/{interval_s}",   # one frame every interval_s seconds
        "-f", "image2",
        str(pattern),
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout)
    except FileNotFoundError:
        raise ThumbnailError("ffmpeg not found — install ffmpeg and ensure it is on PATH")
    except subprocess.TimeoutExpired:
        raise ThumbnailError(f"ffmpeg timed out after {timeout}s")

    if result.returncode != 0:
        raise ThumbnailError(f"ffmpeg error: {result.stderr[-500:]}")

    # Collect generated files in order
    thumbs = sorted(output_dir.glob(f"{input.stem}_*.png"))

    if not thumbs:
        raise ThumbnailError(f"no thumbnails generated in {output_dir}")

    if zip_output:
        zip_path = output_dir / f"{input.stem}-thumbnails.zip"
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
            for thumb in thumbs:
                zf.write(thumb, thumb.name)
        return zip_path

    return thumbs
