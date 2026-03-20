"""Tests for mediatools.video.speed_change and _build_atempo_chain."""

import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from mediatools.video import VideoError, _build_atempo_chain, speed_change


def _mock_run(returncode=0, stderr=""):
    result = MagicMock()
    result.returncode = returncode
    result.stderr = stderr
    return result


def _run_speed(speed=2.0, audio=True, returncode=0, side_effect=None):
    run_kwargs = (
        {"side_effect": side_effect}
        if side_effect
        else {"return_value": _mock_run(returncode=returncode)}
    )
    with patch("mediatools.video.subprocess.run", **run_kwargs), \
         patch("mediatools.video.Path.exists", return_value=True), \
         patch("mediatools.video.Path.mkdir"):
        return speed_change("input.mp4", "output.mp4", speed, audio=audio)


class TestSpeedChange(unittest.TestCase):

    # ------------------------------------------------------------------
    # Basic return value
    # ------------------------------------------------------------------

    def test_returns_output_path(self):
        result = _run_speed(speed=2.0)
        self.assertEqual(result, Path("output.mp4"))

    def test_accepts_path_object(self):
        with patch("mediatools.video.subprocess.run", return_value=_mock_run()), \
             patch("mediatools.video.Path.exists", return_value=True), \
             patch("mediatools.video.Path.mkdir"):
            result = speed_change(Path("input.mp4"), Path("output.mp4"), 2.0)
        self.assertEqual(result, Path("output.mp4"))

    # ------------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------------

    def test_file_not_found(self):
        with patch("mediatools.video.Path.exists", return_value=False):
            with self.assertRaises(FileNotFoundError):
                speed_change("missing.mp4", "out.mp4", 2.0)

    def test_zero_speed_raises(self):
        with patch("mediatools.video.Path.exists", return_value=True):
            with self.assertRaises(ValueError):
                speed_change("input.mp4", "out.mp4", 0.0)

    def test_negative_speed_raises(self):
        with patch("mediatools.video.Path.exists", return_value=True):
            with self.assertRaises(ValueError):
                speed_change("input.mp4", "out.mp4", -1.0)

    # ------------------------------------------------------------------
    # FFmpeg command construction
    # ------------------------------------------------------------------

    def test_setpts_filter_fast_forward(self):
        """2× speed → setpts=0.5*PTS"""
        with patch("mediatools.video.subprocess.run",
                   return_value=_mock_run()) as mock_run, \
             patch("mediatools.video.Path.exists", return_value=True), \
             patch("mediatools.video.Path.mkdir"):
            speed_change("input.mp4", "output.mp4", 2.0)
        cmd = mock_run.call_args[0][0]
        vf_idx = cmd.index("-filter:v") + 1
        self.assertIn("setpts=0.5", cmd[vf_idx])

    def test_setpts_filter_slow_motion(self):
        """0.5× speed → setpts=2.0*PTS"""
        with patch("mediatools.video.subprocess.run",
                   return_value=_mock_run()) as mock_run, \
             patch("mediatools.video.Path.exists", return_value=True), \
             patch("mediatools.video.Path.mkdir"):
            speed_change("input.mp4", "output.mp4", 0.5)
        cmd = mock_run.call_args[0][0]
        vf_idx = cmd.index("-filter:v") + 1
        self.assertIn("setpts=2.0", cmd[vf_idx])

    def test_audio_filter_included_by_default(self):
        with patch("mediatools.video.subprocess.run",
                   return_value=_mock_run()) as mock_run, \
             patch("mediatools.video.Path.exists", return_value=True), \
             patch("mediatools.video.Path.mkdir"):
            speed_change("input.mp4", "output.mp4", 2.0, audio=True)
        cmd = mock_run.call_args[0][0]
        self.assertIn("-filter:a", cmd)
        self.assertNotIn("-an", cmd)

    def test_audio_false_drops_audio(self):
        with patch("mediatools.video.subprocess.run",
                   return_value=_mock_run()) as mock_run, \
             patch("mediatools.video.Path.exists", return_value=True), \
             patch("mediatools.video.Path.mkdir"):
            speed_change("input.mp4", "output.mp4", 2.0, audio=False)
        cmd = mock_run.call_args[0][0]
        self.assertIn("-an", cmd)
        self.assertNotIn("-filter:a", cmd)

    # ------------------------------------------------------------------
    # Error handling
    # ------------------------------------------------------------------

    def test_ffmpeg_not_found(self):
        import subprocess
        with self.assertRaises(VideoError) as ctx:
            _run_speed(side_effect=FileNotFoundError)
        self.assertIn("ffmpeg not found", str(ctx.exception))

    def test_ffmpeg_timeout(self):
        import subprocess
        with self.assertRaises(VideoError) as ctx:
            _run_speed(side_effect=subprocess.TimeoutExpired(cmd="ffmpeg", timeout=600))
        self.assertIn("timed out", str(ctx.exception))

    def test_ffmpeg_nonzero_exit(self):
        with self.assertRaises(VideoError):
            _run_speed(returncode=1)


class TestBuildAtempoChain(unittest.TestCase):

    def test_1x_speed(self):
        chain = _build_atempo_chain(1.0)
        self.assertEqual(len(chain), 1)
        self.assertAlmostEqual(float(chain[0].split("=")[1]), 1.0, places=3)

    def test_2x_speed_single_filter(self):
        chain = _build_atempo_chain(2.0)
        self.assertEqual(len(chain), 1)
        self.assertAlmostEqual(float(chain[0].split("=")[1]), 2.0, places=3)

    def test_4x_speed_chained(self):
        """4× = atempo=2.0 + atempo=2.0"""
        chain = _build_atempo_chain(4.0)
        self.assertEqual(len(chain), 2)
        for f in chain:
            self.assertAlmostEqual(float(f.split("=")[1]), 2.0, places=3)

    def test_0_5x_speed(self):
        chain = _build_atempo_chain(0.5)
        self.assertEqual(len(chain), 1)
        self.assertAlmostEqual(float(chain[0].split("=")[1]), 0.5, places=3)

    def test_0_25x_speed_chained(self):
        """0.25× = atempo=0.5 + atempo=0.5"""
        chain = _build_atempo_chain(0.25)
        self.assertEqual(len(chain), 2)
        for f in chain:
            self.assertAlmostEqual(float(f.split("=")[1]), 0.5, places=3)

    def test_product_equals_speed(self):
        """The product of all atempo values must equal the requested speed."""
        import math
        for speed in [0.25, 0.5, 1.0, 1.5, 2.0, 3.0, 4.0, 8.0]:
            chain = _build_atempo_chain(speed)
            product = math.prod(float(f.split("=")[1]) for f in chain)
            self.assertAlmostEqual(product, speed, places=4,
                                   msg=f"product mismatch at speed={speed}")


if __name__ == "__main__":
    unittest.main()
