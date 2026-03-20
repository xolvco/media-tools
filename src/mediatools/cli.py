"""mediatools CLI — thin wrapper over the library API."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def cmd_probe(args: argparse.Namespace) -> int:
    from mediatools.probe import probe, ProbeError
    try:
        info = probe(args.path)
    except (FileNotFoundError, ProbeError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 1

    print(f"path:     {info.path}")
    print(f"duration: {info.duration_ms} ms ({info.duration_s:.2f}s)")
    print(f"format:   {info.format_name}")
    print(f"size:     {info.size_bytes:,} bytes")
    for s in info.streams:
        if s.codec_type == "video":
            print(f"video:    {s.codec_name} {s.width}x{s.height}")
        elif s.codec_type == "audio":
            print(f"audio:    {s.codec_name} {s.sample_rate}Hz {s.channels}ch")
    return 0


def cmd_extract_audio(args: argparse.Namespace) -> int:
    from mediatools.audio import extract_audio, AudioError
    try:
        out = extract_audio(args.input, args.output,
                            sample_rate=args.sample_rate,
                            channels=args.channels)
        print(f"wrote {out}")
        return 0
    except (FileNotFoundError, AudioError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 1


def cmd_clip(args: argparse.Namespace) -> int:
    from mediatools.video import clip, VideoError
    try:
        out = clip(args.input, args.output,
                   start_ms=args.start_ms, end_ms=args.end_ms)
        print(f"wrote {out}")
        return 0
    except (FileNotFoundError, ValueError, VideoError) as e:
        print(f"error: {e}", file=sys.stderr)
        return 1


def cmd_pull_video(args: argparse.Namespace) -> int:
    from mediatools.download import pull_video, DownloadError, default_downloads_dir
    dest = args.output_dir or default_downloads_dir()
    print(f"downloading to {dest} ...")
    try:
        out = pull_video(
            args.url,
            output_dir=dest,
            filename=args.filename,
            quality=args.quality,
            cookies=args.cookies,
            cookies_from_browser=args.cookies_from_browser,
        )
        print(f"saved {out}")
        return 0
    except DownloadError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="mediatools",
        description="Media processing utilities",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # probe
    p = sub.add_parser("probe", help="Show metadata for a media file")
    p.add_argument("path", type=Path)
    p.set_defaults(func=cmd_probe)

    # extract-audio
    p = sub.add_parser("extract-audio", help="Extract audio stream from a media file")
    p.add_argument("input", type=Path)
    p.add_argument("output", type=Path)
    p.add_argument("--sample-rate", type=int, default=44100)
    p.add_argument("--channels", type=int, default=2)
    p.set_defaults(func=cmd_extract_audio)

    # clip
    p = sub.add_parser("clip", help="Clip a media file to a time range")
    p.add_argument("input", type=Path)
    p.add_argument("output", type=Path)
    p.add_argument("--start-ms", type=int, required=True)
    p.add_argument("--end-ms", type=int, required=True)
    p.set_defaults(func=cmd_clip)

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
    p.set_defaults(func=cmd_pull_video)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    sys.exit(args.func(args))


if __name__ == "__main__":
    main()
