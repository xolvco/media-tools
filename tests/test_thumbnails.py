"""Tests for mediatools.thumbnails.generate_thumbnails."""

import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import MagicMock, patch


class TestGenerateThumbnails(unittest.TestCase):

    def _run(self, returncode=0, side_effect=None, generated_files=None, **kwargs):
        """Run generate_thumbnails with mocked ffmpeg and a real temp dir."""
        from mediatools.thumbnails import generate_thumbnails

        mock_result = MagicMock()
        mock_result.returncode = returncode
        mock_result.stderr = "error" if returncode != 0 else ""
        run_kwargs = {"side_effect": side_effect} if side_effect else {"return_value": mock_result}

        with tempfile.TemporaryDirectory() as tmp:
            output_dir = Path(tmp) / "thumbnails"
            output_dir.mkdir()

            # Create fake PNG files that ffmpeg would have generated
            files = generated_files or [
                output_dir / "video_0001.png",
                output_dir / "video_0002.png",
                output_dir / "video_0003.png",
            ]
            for f in files:
                f.touch()

            with patch("mediatools.thumbnails.subprocess.run", **run_kwargs), \
                 patch("mediatools.thumbnails.Path.exists", return_value=True), \
                 patch("mediatools.thumbnails.Path.mkdir"):
                # Override glob to return our fake files
                with patch.object(Path, "glob", return_value=iter(sorted(files))):
                    return generate_thumbnails(
                        "video.mp4", output_dir=output_dir, **kwargs
                    )

    def test_returns_list_of_paths(self):
        result = self._run()
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 3)

    def test_all_png(self):
        result = self._run()
        for p in result:
            self.assertEqual(p.suffix, ".png")

    def test_file_not_found(self):
        from mediatools.thumbnails import generate_thumbnails
        with patch("mediatools.thumbnails.Path.exists", return_value=False):
            with self.assertRaises(FileNotFoundError):
                generate_thumbnails("missing.mp4")

    def test_ffmpeg_not_on_path(self):
        from mediatools.thumbnails import ThumbnailError
        with self.assertRaises(ThumbnailError) as ctx:
            self._run(side_effect=FileNotFoundError)
        self.assertIn("ffmpeg not found", str(ctx.exception))

    def test_ffmpeg_nonzero_exit(self):
        from mediatools.thumbnails import ThumbnailError
        with self.assertRaises(ThumbnailError):
            self._run(returncode=1)

    def test_zip_output_returns_path(self):
        result = self._run(zip_output=True)
        self.assertIsInstance(result, Path)
        self.assertEqual(result.suffix, ".zip")

    def test_zip_contains_thumbnails(self):
        from mediatools.thumbnails import generate_thumbnails
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stderr = ""

        with tempfile.TemporaryDirectory() as tmp:
            output_dir = Path(tmp) / "thumbnails"
            output_dir.mkdir()
            files = [output_dir / f"video_{i:04d}.png" for i in range(1, 4)]
            for f in files:
                f.touch()

            with patch("mediatools.thumbnails.subprocess.run", return_value=mock_result), \
                 patch("mediatools.thumbnails.Path.exists", return_value=True), \
                 patch("mediatools.thumbnails.Path.mkdir"), \
                 patch.object(Path, "glob", return_value=iter(sorted(files))):
                result = generate_thumbnails("video.mp4", output_dir=output_dir, zip_output=True)

            # Read zip while temp dir still exists
            with zipfile.ZipFile(result) as zf:
                names = zf.namelist()

        self.assertEqual(len(names), 3)
        for name in names:
            self.assertTrue(name.endswith(".png"))

    def test_default_output_dir_name(self):
        """Default output dir is thumbnails/ next to the input file."""
        from mediatools.thumbnails import generate_thumbnails
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stderr = ""

        captured_cmd = []

        def capture(cmd, **kwargs):
            captured_cmd.append(cmd)
            return mock_result

        with tempfile.TemporaryDirectory() as tmp:
            video = Path(tmp) / "video.mp4"
            video.touch()
            expected_dir = Path(tmp) / "thumbnails"
            expected_dir.mkdir()
            fake_file = expected_dir / "video_0001.png"
            fake_file.touch()

            with patch("mediatools.thumbnails.subprocess.run", side_effect=capture), \
                 patch.object(Path, "glob", return_value=iter([fake_file])):
                generate_thumbnails(video)

        # The ffmpeg output pattern should contain "thumbnails/"
        self.assertIn("thumbnails", captured_cmd[0][-1])


if __name__ == "__main__":
    unittest.main()
