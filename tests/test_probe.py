"""Tests for mediatools.probe — uses unittest.mock to avoid needing real media files."""

import json
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from mediatools.probe import ProbeError, ProbeResult, StreamInfo, probe


SAMPLE_FFPROBE_OUTPUT = json.dumps({
    "streams": [
        {
            "codec_type": "video",
            "codec_name": "h264",
            "width": 1920,
            "height": 1080,
            "duration": "10.0",
        },
        {
            "codec_type": "audio",
            "codec_name": "aac",
            "sample_rate": "44100",
            "channels": 2,
            "duration": "10.0",
        },
    ],
    "format": {
        "duration": "10.0",
        "format_name": "mov,mp4,m4a,3gp,3g2,mj2",
        "size": "1048576",
    },
})


class TestProbe(unittest.TestCase):

    def _run_probe(self, stdout=SAMPLE_FFPROBE_OUTPUT, returncode=0):
        """Helper: patch subprocess.run and Path.exists, then call probe()."""
        mock_result = MagicMock()
        mock_result.stdout = stdout
        mock_result.returncode = returncode
        mock_result.stderr = ""

        with patch("mediatools.probe.subprocess.run", return_value=mock_result), \
             patch("mediatools.probe.Path.exists", return_value=True):
            return probe("fake/video.mp4")

    def test_returns_probe_result(self):
        result = self._run_probe()
        self.assertIsInstance(result, ProbeResult)

    def test_duration(self):
        result = self._run_probe()
        self.assertAlmostEqual(result.duration_s, 10.0)
        self.assertEqual(result.duration_ms, 10000)

    def test_streams_parsed(self):
        result = self._run_probe()
        self.assertEqual(len(result.streams), 2)

    def test_has_video_and_audio(self):
        result = self._run_probe()
        self.assertTrue(result.has_video)
        self.assertTrue(result.has_audio)

    def test_video_stream_properties(self):
        result = self._run_probe()
        v = result.video_stream
        self.assertIsNotNone(v)
        self.assertEqual(v.codec_name, "h264")
        self.assertEqual(v.width, 1920)
        self.assertEqual(v.height, 1080)

    def test_audio_stream_properties(self):
        result = self._run_probe()
        a = result.audio_stream
        self.assertIsNotNone(a)
        self.assertEqual(a.codec_name, "aac")
        self.assertEqual(a.sample_rate, 44100)
        self.assertEqual(a.channels, 2)

    def test_file_not_found(self):
        with patch("mediatools.probe.Path.exists", return_value=False):
            with self.assertRaises(FileNotFoundError):
                probe("nonexistent.mp4")

    def test_ffprobe_not_on_path(self):
        with patch("mediatools.probe.Path.exists", return_value=True), \
             patch("mediatools.probe.subprocess.run", side_effect=FileNotFoundError):
            with self.assertRaises(ProbeError) as ctx:
                probe("fake.mp4")
            self.assertIn("ffprobe not found", str(ctx.exception))

    def test_ffprobe_nonzero_exit(self):
        with self.assertRaises(ProbeError):
            self._run_probe(stdout="{}", returncode=1)


class TestProbeResult(unittest.TestCase):

    def _make_result(self):
        return ProbeResult(
            path=Path("test.mp4"),
            duration_s=90.5,
            format_name="mp4",
            size_bytes=2_000_000,
            streams=[
                StreamInfo("video", "h264", 1280, 720, None, None, 90.5),
                StreamInfo("audio", "aac", None, None, 48000, 2, 90.5),
            ],
        )

    def test_duration_ms(self):
        self.assertEqual(self._make_result().duration_ms, 90500)

    def test_no_video_stream(self):
        r = ProbeResult(Path("audio.mp3"), 60.0, "mp3", 500_000, [
            StreamInfo("audio", "mp3", None, None, 44100, 2, 60.0),
        ])
        self.assertFalse(r.has_video)
        self.assertIsNone(r.video_stream)


if __name__ == "__main__":
    unittest.main()
