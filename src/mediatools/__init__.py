"""mediatools — reusable media processing utilities."""

from mediatools.convert import convert_audio, convert_to_mp3
from mediatools.download import fetch_info, pull_video
from mediatools.media_file import MediaFile
from mediatools.probe import probe
from mediatools.thumbnails import generate_thumbnails, generate_thumbnails_at
from mediatools.video import (
    FrameInfo, VideoEntry,
    extract_frames, list_videos,
    write_manifest, read_manifest, concat_videos,
    normalize_video, normalize_videos,
)

__all__ = [
    "MediaFile", "probe", "pull_video", "fetch_info",
    "convert_to_mp3", "convert_audio",
    "generate_thumbnails", "generate_thumbnails_at",
    "extract_frames", "FrameInfo",
    "list_videos", "VideoEntry",
    "write_manifest", "read_manifest", "concat_videos",
    "normalize_video", "normalize_videos",
]
__version__ = "0.1.0"
