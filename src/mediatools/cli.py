"""mediatools CLI — thin wrapper over the library API.

Output format: JSON by default (machine-readable, agentic-friendly).
Use --human for human-readable text output.

Error output always goes to stderr.  Exit code 0 = success, 1 = error.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


# ── output helpers ────────────────────────────────────────────────────────────

def _out(data: dict, human: bool) -> None:
    """Print *data* as JSON (default) or human-readable text."""
    if human:
        for k, v in data.items():
            print(f"{k}: {v}")
    else:
        print(json.dumps(data, indent=2, default=str))


def _err(message: str, human: bool) -> None:
    """Print an error — always to stderr, always as the right format."""
    if human:
        print(f"error: {message}", file=sys.stderr)
    else:
        print(json.dumps({"error": message}), file=sys.stderr)


# ── commands ──────────────────────────────────────────────────────────────────

def cmd_probe(args: argparse.Namespace) -> int:
    from mediatools.probe import probe, ProbeError
    try:
        info = probe(args.path)
    except (FileNotFoundError, ProbeError) as e:
        _err(str(e), args.human)
        return 1

    streams = []
    for s in info.streams:
        entry = {"codec_type": s.codec_type, "codec_name": s.codec_name}
        if s.codec_type == "video":
            entry.update({"width": s.width, "height": s.height})
        elif s.codec_type == "audio":
            entry.update({"sample_rate": s.sample_rate, "channels": s.channels})
        streams.append(entry)

    data = {
        "path": str(info.path),
        "duration_ms": info.duration_ms,
        "duration_s": round(info.duration_s, 3),
        "format": info.format_name,
        "size_bytes": info.size_bytes,
        "streams": streams,
    }

    if args.human:
        print(f"path:     {info.path}")
        print(f"duration: {info.duration_ms} ms ({info.duration_s:.2f}s)")
        print(f"format:   {info.format_name}")
        print(f"size:     {info.size_bytes:,} bytes")
        for s in info.streams:
            if s.codec_type == "video":
                print(f"video:    {s.codec_name} {s.width}x{s.height}")
            elif s.codec_type == "audio":
                print(f"audio:    {s.codec_name} {s.sample_rate}Hz {s.channels}ch")
    else:
        print(json.dumps(data, indent=2))
    return 0


def cmd_extract_audio(args: argparse.Namespace) -> int:
    from mediatools.audio import extract_audio, AudioError
    try:
        out = extract_audio(args.input, args.output,
                            sample_rate=args.sample_rate,
                            channels=args.channels)
    except (FileNotFoundError, AudioError) as e:
        _err(str(e), args.human)
        return 1

    _out({"path": str(out), "sample_rate": args.sample_rate, "channels": args.channels},
         args.human)
    return 0


def cmd_clip(args: argparse.Namespace) -> int:
    from mediatools.video import clip, VideoError
    try:
        out = clip(args.input, args.output,
                   start_ms=args.start_ms, end_ms=args.end_ms)
    except (FileNotFoundError, ValueError, VideoError) as e:
        _err(str(e), args.human)
        return 1

    _out({"path": str(out), "start_ms": args.start_ms, "end_ms": args.end_ms},
         args.human)
    return 0


def cmd_thumbnails(args: argparse.Namespace) -> int:
    from mediatools.thumbnails import generate_thumbnails, ThumbnailError
    try:
        result = generate_thumbnails(
            args.input,
            args.output_dir,
            interval_s=args.interval,
            zip_output=args.zip,
        )
    except (FileNotFoundError, ThumbnailError) as e:
        _err(str(e), args.human)
        return 1

    if args.zip:
        _out({"zip": str(result)}, args.human)
    else:
        _out({"count": len(result), "paths": [str(p) for p in result]}, args.human)
    return 0


def cmd_fetch_info(args: argparse.Namespace) -> int:
    from mediatools.download import fetch_info, DownloadError
    try:
        info = fetch_info(args.url)
    except DownloadError as e:
        _err(str(e), args.human)
        return 1

    if args.human:
        print(f"title:    {info.get('title')}")
        print(f"creator:  {info.get('creator', {}).get('uploader')}")
        print(f"duration: {info.get('duration_s')}s")
        print(f"uploaded: {info.get('upload_date')}")
        print(f"views:    {info.get('view_count')}")
        print(f"formats:  {len(info.get('formats', []))}")
    else:
        print(json.dumps(info, indent=2, default=str))
    return 0


def cmd_convert(args: argparse.Namespace) -> int:
    from mediatools.convert import convert_audio, ConvertError
    try:
        out = convert_audio(
            args.input,
            args.output,
            fmt=args.format,
            bitrate=args.bitrate,
        )
    except (FileNotFoundError, ValueError, ConvertError) as e:
        _err(str(e), args.human)
        return 1

    _out({"path": str(out), "format": args.format, "bitrate": args.bitrate}, args.human)
    return 0


def cmd_pull_video(args: argparse.Namespace) -> int:
    from mediatools.download import pull_video, DownloadError, default_downloads_dir
    import json as _json
    dest = args.output_dir or default_downloads_dir()
    if args.human:
        print(f"downloading to {dest} ...", file=sys.stderr)
    try:
        out = pull_video(
            args.url,
            output_dir=dest,
            filename=args.filename,
            quality=args.quality,
            cookies=args.cookies,
            cookies_from_browser=args.cookies_from_browser,
        )
    except DownloadError as e:
        _err(str(e), args.human)
        return 1

    # Load credits sidecar if present
    credits_path = out.with_name(out.stem + ".credits.json")
    credits = {}
    if credits_path.exists():
        try:
            credits = _json.loads(credits_path.read_text(encoding="utf-8"))
        except Exception:
            pass

    data = {"path": str(out), "credits": credits}
    _out(data, args.human)
    return 0


# ── parser ────────────────────────────────────────────────────────────────────

def _add_human(p: argparse.ArgumentParser) -> None:
    p.add_argument("--human", action="store_true",
                   help="Human-readable text output instead of JSON")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="mediatools",
        description="Media processing utilities — JSON output by default",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # probe
    p = sub.add_parser("probe", help="Show metadata for a media file")
    p.add_argument("path", type=Path)
    _add_human(p)
    p.set_defaults(func=cmd_probe)

    # extract-audio
    p = sub.add_parser("extract-audio", help="Extract audio stream from a media file")
    p.add_argument("input", type=Path)
    p.add_argument("output", type=Path)
    p.add_argument("--sample-rate", type=int, default=44100)
    p.add_argument("--channels", type=int, default=2)
    _add_human(p)
    p.set_defaults(func=cmd_extract_audio)

    # clip
    p = sub.add_parser("clip", help="Clip a media file to a time range")
    p.add_argument("input", type=Path)
    p.add_argument("output", type=Path)
    p.add_argument("--start-ms", type=int, required=True)
    p.add_argument("--end-ms", type=int, required=True)
    _add_human(p)
    p.set_defaults(func=cmd_clip)

    # thumbnails
    p = sub.add_parser("thumbnails", help="Extract PNG thumbnails at regular intervals")
    p.add_argument("input", type=Path)
    p.add_argument("--output-dir", type=Path, default=None,
                   help="Output folder (default: thumbnails/ next to input file)")
    p.add_argument("--interval", type=float, default=15.0,
                   help="Seconds between thumbnails (default: 15)")
    p.add_argument("--zip", action="store_true",
                   help="Zip all thumbnails on completion")
    _add_human(p)
    p.set_defaults(func=cmd_thumbnails)

    # fetch-info
    p = sub.add_parser("fetch-info", help="Fetch video metadata without downloading")
    p.add_argument("url")
    _add_human(p)
    p.set_defaults(func=cmd_fetch_info)

    # convert
    p = sub.add_parser("convert", help="Convert media to an audio format (default: mp3)")
    p.add_argument("input", type=Path)
    p.add_argument("output", type=Path, nargs="?", default=None,
                   help="Output path (default: input filename with new extension)")
    p.add_argument("--format", default="mp3",
                   choices=["mp3", "m4a", "wav", "flac", "ogg", "opus"],
                   help="Output format (default: mp3)")
    p.add_argument("--bitrate", default="320k",
                   help="Audio bitrate (default: 320k)")
    _add_human(p)
    p.set_defaults(func=cmd_convert)

    # pull-video
    p = sub.add_parser("pull-video", help="Download a video from a URL")
    p.add_argument("url")
    p.add_argument("--output-dir", type=Path, default=None,
                   help="Destination folder (default: platform Downloads)")
    p.add_argument("--filename", default=None,
                   help="Output filename without extension (default: video title)")
    p.add_argument("--quality", default="bestvideo+bestaudio/best",
                   help="yt-dlp format selector (default: best)")
    p.add_argument("--cookies", type=Path, default=None,
                   help="Path to Netscape-format cookies.txt file")
    p.add_argument("--cookies-from-browser", default=None,
                   metavar="BROWSER",
                   help="Extract cookies from browser: chrome, firefox, edge, safari")
    _add_human(p)
    p.set_defaults(func=cmd_pull_video)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    sys.exit(args.func(args))


if __name__ == "__main__":
    main()
