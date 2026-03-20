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

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    sys.exit(args.func(args))


if __name__ == "__main__":
    main()
