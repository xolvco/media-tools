"""Tests for mediatools.video.clip."""

import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from mediatools.video import VideoError, clip


class TestClip(unittest.TestCase):

    def _run(self, start_ms=0, end_ms=5000, returncode=0, side_effect=None):
        mock_result = MagicMock()
        mock_result.returncode = returncode
        mock_result.stderr = "error" if returncode != 0 else ""

        run_kwargs = {"side_effect": side_effect} if side_effect else {"return_value": mock_result}

        with patch("mediatools.video.subprocess.run", **run_kwargs), \
             patch("mediatools.video.Path.exists", return_value=True), \
             patch("mediatools.video.Path.mkdir"):
            return clip("input.mp4", "output.mp4", start_ms=start_ms, end_ms=end_ms)

    def test_returns_output_path(self):
        result = self._run()
        self.assertEqual(result, Path("output.mp4"))

    def test_file_not_found(self):
        with patch("mediatools.video.Path.exists", return_value=False):
            with self.assertRaises(FileNotFoundError):
                clip("missing.mp4", "out.mp4", start_ms=0, end_ms=1000)

    def test_invalid_range(self):
        with self.assertRaises(ValueError):
            self._run(start_ms=5000, end_ms=1000)

    def test_equal_start_end_raises(self):
        with self.assertRaises(ValueError):
            self._run(start_ms=1000, end_ms=1000)

    def test_ffmpeg_not_on_path(self):
        with self.assertRaises(VideoError) as ctx:
            self._run(side_effect=FileNotFoundError)
        self.assertIn("ffmpeg not found", str(ctx.exception))

    def test_ffmpeg_nonzero_exit(self):
        with self.assertRaises(VideoError):
            self._run(returncode=1)


if __name__ == "__main__":
    unittest.main()
