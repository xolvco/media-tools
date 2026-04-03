from mediatools import concat_videos, probe_media, trim_video
from mediatools.cli import main
from mediatools.download import pull_video
from mediatools.video import speed_change


def test_wrapper_exports_core_videoedit_functions() -> None:
    assert callable(probe_media)
    assert callable(trim_video)
    assert callable(concat_videos)
    assert callable(speed_change)
    assert callable(pull_video)
    assert callable(main)
