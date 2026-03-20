"""Tests for mediatools.convert."""

import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from mediatools.convert import ConvertError, SUPPORTED_FORMATS, convert_audio, convert_to_mp3


class TestConvertToMp3(unittest.TestCase):

    def _run(self, returncode=0, side_effect=None):
        mock_result = MagicMock()
        mock_result.returncode = returncode
        mock_result.stderr = "error" if returncode != 0 else ""
        run_kwargs = {"side_effect": side_effect} if side_effect else {"return_value": mock_result}
        with patch("mediatools.convert.subprocess.run", **run_kwargs), \
             patch("mediatools.convert.Path.exists", return_value=True), \
             patch("mediatools.convert.Path.mkdir"):
            return convert_to_mp3("input.mp4")

    def test_returns_mp3_path(self):
        result = self._run()
        self.assertEqual(result.suffix, ".mp3")

    def test_default_output_same_stem(self):
        result = self._run()
        self.assertEqual(result.stem, "input")

    def test_file_not_found(self):
        with patch("mediatools.convert.Path.exists", return_value=False):
            with self.assertRaises(FileNotFoundError):
                convert_to_mp3("missing.mp4")

    def test_ffmpeg_not_on_path(self):
        with self.assertRaises(ConvertError) as ctx:
            self._run(side_effect=FileNotFoundError)
        self.assertIn("ffmpeg not found", str(ctx.exception))

    def test_ffmpeg_nonzero_exit(self):
        with self.assertRaises(ConvertError):
            self._run(returncode=1)


class TestConvertAudio(unittest.TestCase):

    def _run(self, fmt="mp3", output=None, returncode=0):
        mock_result = MagicMock()
        mock_result.returncode = returncode
        mock_result.stderr = ""
        with patch("mediatools.convert.subprocess.run", return_value=mock_result), \
             patch("mediatools.convert.Path.exists", return_value=True), \
             patch("mediatools.convert.Path.mkdir"):
            return convert_audio("input.mp4", output, fmt=fmt)

    def test_all_supported_formats(self):
        for fmt in SUPPORTED_FORMATS:
            with self.subTest(fmt=fmt):
                result = self._run(fmt=fmt)
                self.assertEqual(result.suffix, f".{fmt}")

    def test_unsupported_format(self):
        with self.assertRaises(ValueError) as ctx:
            self._run(fmt="avi")
        self.assertIn("unsupported format", str(ctx.exception))

    def test_custom_output_path(self):
        result = self._run(output="custom/out.mp3")
        self.assertEqual(result, Path("custom/out.mp3"))

    def test_wav_no_bitrate_in_cmd(self):
        """WAV is lossless — bitrate arg should not be passed to ffmpeg."""
        captured = []
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stderr = ""

        def capture(cmd, **kwargs):
            captured.append(cmd)
            return mock_result

        with patch("mediatools.convert.subprocess.run", side_effect=capture), \
             patch("mediatools.convert.Path.exists", return_value=True), \
             patch("mediatools.convert.Path.mkdir"):
            convert_audio("input.mp4", fmt="wav")

        self.assertNotIn("-b:a", captured[0])


if __name__ == "__main__":
    unittest.main()
