"""Tests for mediatools.video.extract_frames."""

import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from mediatools.video import FrameInfo, VideoError, extract_frames


def _mock_run(returncode=0):
    m = MagicMock()
    m.returncode = returncode
    m.stderr = "error" if returncode != 0 else ""
    return m


def _fake_probe(fps=30.0):
    """Return a minimal mock ProbeResult with a video stream."""
    vs = MagicMock()
    vs.fps = fps
    pr = MagicMock()
    pr.video_stream = vs
    return pr


class TestExtractFrames(unittest.TestCase):

    def _run(self, fps=2.0, start_ms=None, end_ms=None,
             width=None, height=None, fmt="png",
             returncode=0, side_effect=None, num_frames=4):
        mock_result = _mock_run(returncode)
        run_kwargs = {"side_effect": side_effect} if side_effect else {"return_value": mock_result}

        with tempfile.TemporaryDirectory() as tmp:
            output_dir = Path(tmp) / "frames"
            output_dir.mkdir()

            # Create fake frame files that ffmpeg would have produced
            fake_files = [output_dir / f"frame_{i:06d}.{fmt}" for i in range(1, num_frames + 1)]
            for f in fake_files:
                f.touch()

            with patch("mediatools.video.subprocess.run", **run_kwargs), \
                 patch("mediatools.video.Path.exists", return_value=True), \
                 patch("mediatools.video.Path.mkdir"), \
                 patch.object(Path, "glob", return_value=iter(sorted(fake_files))):
                return extract_frames(
                    "video.mp4", output_dir,
                    fps=fps, start_ms=start_ms, end_ms=end_ms,
                    width=width, height=height, fmt=fmt,
                )

    def test_returns_list_of_frame_info(self):
        result = self._run()
        self.assertIsInstance(result, list)
        self.assertTrue(all(isinstance(f, FrameInfo) for f in result))

    def test_frame_count(self):
        result = self._run(num_frames=6)
        self.assertEqual(len(result), 6)

    def test_timestamps_at_2fps(self):
        """Frame 1 = 0ms, frame 2 = 500ms at 2 fps."""
        result = self._run(fps=2.0, num_frames=3)
        self.assertEqual(result[0].timestamp_ms, 0)
        self.assertEqual(result[1].timestamp_ms, 500)
        self.assertEqual(result[2].timestamp_ms, 1000)

    def test_timestamps_with_start_ms(self):
        """Timestamps are offset by start_ms."""
        result = self._run(fps=1.0, start_ms=5000, num_frames=3)
        self.assertEqual(result[0].timestamp_ms, 5000)
        self.assertEqual(result[1].timestamp_ms, 6000)
        self.assertEqual(result[2].timestamp_ms, 7000)

    def test_indices_are_one_based(self):
        result = self._run(num_frames=3)
        self.assertEqual([f.index for f in result], [1, 2, 3])

    def test_paths_are_png(self):
        result = self._run(fmt="png")
        for f in result:
            self.assertEqual(f.path.suffix, ".png")

    def test_paths_are_jpg(self):
        result = self._run(fmt="jpg")
        for f in result:
            self.assertEqual(f.path.suffix, ".jpg")

    def test_file_not_found(self):
        with patch("mediatools.video.Path.exists", return_value=False):
            with self.assertRaises(FileNotFoundError):
                extract_frames("missing.mp4", fps=2.0)

    def test_invalid_fmt(self):
        with patch("mediatools.video.Path.exists", return_value=True):
            with self.assertRaises(ValueError) as ctx:
                extract_frames("video.mp4", fps=2.0, fmt="bmp")
            self.assertIn("fmt", str(ctx.exception))

    def test_invalid_time_range(self):
        with patch("mediatools.video.Path.exists", return_value=True):
            with self.assertRaises(ValueError):
                extract_frames("video.mp4", fps=2.0, start_ms=5000, end_ms=1000)

    def test_ffmpeg_not_on_path(self):
        with self.assertRaises(VideoError) as ctx:
            self._run(side_effect=FileNotFoundError)
        self.assertIn("ffmpeg not found", str(ctx.exception))

    def test_ffmpeg_nonzero_exit(self):
        with self.assertRaises(VideoError):
            self._run(returncode=1)

    def test_native_fps_probes_video(self):
        """When fps=None, probe() is called to determine native fps."""
        mock_result = _mock_run()

        with tempfile.TemporaryDirectory() as tmp:
            output_dir = Path(tmp) / "frames"
            output_dir.mkdir()
            fake_file = output_dir / "frame_000001.png"
            fake_file.touch()

            with patch("mediatools.video.subprocess.run", return_value=mock_result), \
                 patch("mediatools.video.Path.exists", return_value=True), \
                 patch("mediatools.video.Path.mkdir"), \
                 patch("mediatools.probe.probe", return_value=_fake_probe(fps=24.0)) as mock_probe, \
                 patch.object(Path, "glob", return_value=iter([fake_file])):
                result = extract_frames("video.mp4", output_dir, fps=None)

            mock_probe.assert_called_once()
            # At 24fps, frame 1 = 0ms
            self.assertEqual(result[0].timestamp_ms, 0)

    def test_resize_included_in_filter(self):
        """Width/height resize is passed to ffmpeg -vf."""
        mock_result = _mock_run()
        captured = []

        def capture(cmd, **kwargs):
            captured.append(cmd)
            return mock_result

        with tempfile.TemporaryDirectory() as tmp:
            output_dir = Path(tmp) / "frames"
            output_dir.mkdir()

            with patch("mediatools.video.subprocess.run", side_effect=capture), \
                 patch("mediatools.video.Path.exists", return_value=True), \
                 patch("mediatools.video.Path.mkdir"), \
                 patch.object(Path, "glob", return_value=iter([])):
                extract_frames("video.mp4", output_dir, fps=1.0, width=640, height=360)

        cmd = captured[0]
        vf_idx = cmd.index("-vf")
        self.assertIn("scale=640:360", cmd[vf_idx + 1])


if __name__ == "__main__":
    unittest.main()
