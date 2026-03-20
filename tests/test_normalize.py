"""Tests for mediatools.video.normalize_video and normalize_videos."""

import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from mediatools.video import VideoError, normalize_video, normalize_videos


def _mock_run(returncode=0):
    m = MagicMock()
    m.returncode = returncode
    m.stderr = "error" if returncode != 0 else ""
    return m


class TestNormalizeVideo(unittest.TestCase):

    def _run(self, returncode=0, side_effect=None, **kwargs):
        mock_result = _mock_run(returncode)
        run_kwargs = {"side_effect": side_effect} if side_effect else {"return_value": mock_result}

        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "input.mp4"
            src.touch()
            dest = Path(tmp) / "output.mp4"

            with patch("mediatools.video.subprocess.run", **run_kwargs), \
                 patch("mediatools.video.Path.mkdir"):
                return normalize_video(src, dest, **kwargs)

    def _capture_cmd(self, **kwargs):
        """Run normalize_video and return the ffmpeg command list."""
        captured = []

        def capture(cmd, **kw):
            captured.append(cmd)
            return _mock_run()

        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "clip.mp4"
            src.touch()
            dest = Path(tmp) / "out.mp4"

            with patch("mediatools.video.subprocess.run", side_effect=capture), \
                 patch("mediatools.video.Path.mkdir"):
                normalize_video(src, dest, **kwargs)

        return captured[0]

    def test_returns_output_path(self):
        result = self._run()
        self.assertIsInstance(result, Path)
        self.assertEqual(result.name, "output.mp4")

    def test_file_not_found(self):
        with self.assertRaises(FileNotFoundError):
            normalize_video("/nonexistent/clip.mp4", "/tmp/out.mp4")

    def test_ffmpeg_not_on_path(self):
        with self.assertRaises(VideoError) as ctx:
            self._run(side_effect=FileNotFoundError)
        self.assertIn("ffmpeg not found", str(ctx.exception))

    def test_ffmpeg_nonzero_exit(self):
        with self.assertRaises(VideoError):
            self._run(returncode=1)

    def test_default_resolution_in_filter(self):
        cmd = self._capture_cmd()
        vf = cmd[cmd.index("-vf") + 1]
        self.assertIn("scale=1920:1080", vf)
        self.assertIn("pad=1920:1080", vf)

    def test_custom_resolution_in_filter(self):
        cmd = self._capture_cmd(width=1280, height=720)
        vf = cmd[cmd.index("-vf") + 1]
        self.assertIn("scale=1280:720", vf)
        self.assertIn("pad=1280:720", vf)

    def test_fps_in_filter(self):
        cmd = self._capture_cmd(fps=24.0)
        vf = cmd[cmd.index("-vf") + 1]
        self.assertIn("fps=24.0", vf)

    def test_pixel_format_in_filter(self):
        cmd = self._capture_cmd(pixel_fmt="yuv420p")
        vf = cmd[cmd.index("-vf") + 1]
        self.assertIn("format=yuv420p", vf)

    def test_letterbox_preserves_aspect(self):
        """force_original_aspect_ratio=decrease must be in the scale filter."""
        cmd = self._capture_cmd()
        vf = cmd[cmd.index("-vf") + 1]
        self.assertIn("force_original_aspect_ratio=decrease", vf)

    def test_libx264_codec(self):
        cmd = self._capture_cmd()
        self.assertIn("libx264", cmd)

    def test_aac_audio(self):
        cmd = self._capture_cmd()
        self.assertIn("aac", cmd)

    def test_custom_crf(self):
        cmd = self._capture_cmd(crf=23)
        crf_idx = cmd.index("-crf")
        self.assertEqual(cmd[crf_idx + 1], "23")

    def test_custom_preset(self):
        cmd = self._capture_cmd(preset="slow")
        preset_idx = cmd.index("-preset")
        self.assertEqual(cmd[preset_idx + 1], "slow")

    def test_audio_sample_rate(self):
        cmd = self._capture_cmd(audio_sample_rate=48000)
        ar_idx = cmd.index("-ar")
        self.assertEqual(cmd[ar_idx + 1], "48000")

    def test_audio_channels(self):
        cmd = self._capture_cmd(audio_channels=1)
        ac_idx = cmd.index("-ac")
        self.assertEqual(cmd[ac_idx + 1], "1")


class TestNormalizeVideos(unittest.TestCase):

    def test_returns_list_in_order(self):
        with tempfile.TemporaryDirectory() as tmp:
            src_dir = Path(tmp) / "src"
            src_dir.mkdir()
            out_dir = Path(tmp) / "norm"

            clips = [src_dir / f"clip{i}.mp4" for i in range(3)]
            for c in clips:
                c.touch()

            with patch("mediatools.video.subprocess.run", return_value=_mock_run()), \
                 patch("mediatools.video.Path.mkdir"):
                results = normalize_videos(clips, out_dir)

        self.assertEqual(len(results), 3)
        for r in results:
            self.assertIn(".norm", r.stem)

    def test_output_dir_created(self):
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "clip.mp4"
            src.touch()
            out_dir = Path(tmp) / "normalized"

            with patch("mediatools.video.subprocess.run", return_value=_mock_run()):
                normalize_videos([src], out_dir)

            self.assertTrue(out_dir.exists())

    def test_custom_suffix(self):
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "clip.mp4"
            src.touch()
            out_dir = Path(tmp) / "out"

            with patch("mediatools.video.subprocess.run", return_value=_mock_run()):
                results = normalize_videos([src], out_dir, suffix=".1080p")

        self.assertIn(".1080p", results[0].stem)

    def test_propagates_error(self):
        with tempfile.TemporaryDirectory() as tmp:
            src = Path(tmp) / "clip.mp4"
            src.touch()
            out_dir = Path(tmp) / "out"

            with patch("mediatools.video.subprocess.run", return_value=_mock_run(1)):
                with self.assertRaises(VideoError):
                    normalize_videos([src], out_dir)


if __name__ == "__main__":
    unittest.main()
