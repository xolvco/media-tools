"""Video download — pull a video from a URL to the local filesystem."""

from __future__ import annotations

import datetime
import json
import os
import platform
from pathlib import Path


class DownloadError(RuntimeError):
    """Raised when a download fails."""


def default_downloads_dir() -> Path:
    """Return the platform-appropriate Downloads folder.

    - Windows:  C:/Users/<user>/Downloads
    - macOS:    ~/Downloads
    - Linux:    $XDG_DOWNLOAD_DIR if set, else ~/Downloads
    """
    system = platform.system()
    if system == "Linux":
        xdg = os.environ.get("XDG_DOWNLOAD_DIR")
        if xdg:
            return Path(xdg)
    return Path.home() / "Downloads"


def _write_credits(video_path: Path, url: str, info: dict) -> Path:
    """Write a .credits.json file next to *video_path* with full provenance.

    The credits file records who made the content, where it came from,
    and when it was downloaded — suitable for attribution, compliance,
    and downstream tooling (editors, generators, etc.).
    """
    credits_path = video_path.with_name(video_path.stem + ".credits.json")
    payload = {
        "filename": video_path.name,
        "source_url": url,
        "downloaded_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "title": info.get("title"),
        "creator": {
            "uploader": info.get("uploader"),
            "uploader_url": info.get("uploader_url"),
            "channel": info.get("channel"),
            "channel_url": info.get("channel_url"),
        },
        "upload_date": info.get("upload_date"),   # YYYYMMDD string from yt-dlp
        "duration_s": info.get("duration"),
        "description": info.get("description"),
        "webpage_url": info.get("webpage_url"),
        "extractor": info.get("extractor"),
        "tags": info.get("tags") or [],
        "view_count": info.get("view_count"),
        "like_count": info.get("like_count"),
        "license": info.get("license"),
    }
    # drop None values to keep the file clean
    payload = {k: v for k, v in payload.items() if v is not None}
    if isinstance(payload.get("creator"), dict):
        payload["creator"] = {k: v for k, v in payload["creator"].items() if v is not None}
    credits_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    return credits_path


def pull_video(
    url: str,
    output_dir: str | Path | None = None,
    *,
    filename: str | None = None,
    quality: str = "bestvideo+bestaudio/best",
    timeout: float = 300.0,
) -> Path:
    """Download a video from *url* to *output_dir*.

    Uses yt-dlp under the hood — supports YouTube, Vimeo, Twitch, and
    hundreds of other sites.  Install with: ``pip install yt-dlp``

    Args:
        url:        Video URL.
        output_dir: Destination folder.  Defaults to the platform Downloads folder.
        filename:   Output filename without extension.  Defaults to the video title.
        quality:    yt-dlp format selector.  Default: best available quality.
        timeout:    Socket timeout in seconds.

    Returns:
        Path to the downloaded file.

    Raises:
        DownloadError: if yt-dlp is not installed, or the download fails.
    """
    try:
        import yt_dlp
    except ImportError:
        raise DownloadError(
            "yt-dlp is required for download support — "
            "install with: pip install yt-dlp"
        )

    dest = Path(output_dir) if output_dir else default_downloads_dir()
    dest.mkdir(parents=True, exist_ok=True)

    outtmpl = str(dest / (filename if filename else "%(title)s.%(ext)s"))

    ydl_opts = {
        "format": quality,
        "outtmpl": outtmpl,
        "socket_timeout": timeout,
        "quiet": True,
        "no_warnings": True,
        "noprogress": True,
    }

    downloaded: list[tuple[Path, dict]] = []  # (path, info_dict)

    def _on_finished(info: dict) -> None:
        filepath = info.get("filepath") or info.get("filename")
        if filepath:
            downloaded.append((Path(filepath), info))

    ydl_opts["progress_hooks"] = [
        lambda info: _on_finished(info) if info.get("status") == "finished" else None
    ]

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
    except Exception as exc:
        raise DownloadError(f"download failed: {exc}") from exc

    if downloaded:
        video_path, info = downloaded[-1]
        _write_credits(video_path, url, info)
        return video_path

    # yt-dlp didn't fire the hook — find the newest file in dest as fallback
    files = sorted(
        (p for p in dest.iterdir() if p.suffix != ".json"),
        key=lambda p: p.stat().st_mtime,
        reverse=True,
    )
    if files:
        return files[0]

    raise DownloadError(f"download completed but output file not found in {dest}")
