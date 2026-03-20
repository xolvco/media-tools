"""Tests for mediatools.audio.extract_audio."""

import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from mediatools.audio import AudioError, extract_audio


class TestExtractAudio(unittest.TestCase):

    def _run(self, returncode=0, side_effect=None):
        mock_result = MagicMock()
        mock_result.returncode = returncode
        mock_result.stderr = "some error" if returncode != 0 else ""

        run_kwargs = {"side_effect": side_effect} if side_effect else {"return_value": mock_result}

        with patch("mediatools.audio.subprocess.run", **run_kwargs), \
             patch("mediatools.audio.Path.exists", return_value=True), \
             patch("mediatools.audio.Path.mkdir"):
            return extract_audio("input.mp4", "output.wav")

    def test_returns_output_path(self):
        result = self._run()
        self.assertEqual(result, Path("output.wav"))

    def test_file_not_found(self):
        with patch("mediatools.audio.Path.exists", return_value=False):
            with self.assertRaises(FileNotFoundError):
                extract_audio("missing.mp4", "out.wav")

    def test_ffmpeg_not_on_path(self):
        with self.assertRaises(AudioError) as ctx:
            self._run(side_effect=FileNotFoundError)
        self.assertIn("ffmpeg not found", str(ctx.exception))

    def test_ffmpeg_nonzero_exit(self):
        with self.assertRaises(AudioError):
            self._run(returncode=1)


if __name__ == "__main__":
    unittest.main()
