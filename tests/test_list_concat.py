"""Tests for list_videos, write_manifest, read_manifest, and concat_videos."""

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from mediatools.video import (
    VideoEntry, VideoError,
    concat_videos, list_videos, read_manifest, write_manifest,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_probe_result(duration_ms=5000, width=1920, height=1080, fps=30.0):
    vs = MagicMock()
    vs.width = width
    vs.height = height
    vs.fps = fps
    vs.codec_name = "h264"
    pr = MagicMock()
    pr.duration_ms = duration_ms
    pr.size_bytes = 50_000_000
    pr.video_stream = vs
    return pr


def _mock_run(returncode=0):
    m = MagicMock()
    m.returncode = returncode
    m.stderr = "err" if returncode != 0 else ""
    return m


# ---------------------------------------------------------------------------
# list_videos
# ---------------------------------------------------------------------------

class TestListVideos(unittest.TestCase):

    def test_returns_entries(self):
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp)
            for name in ["a.mp4", "b.mkv", "c.txt"]:
                (d / name).touch()

            probe_result = _make_probe_result()
            with patch("mediatools.probe.probe", return_value=probe_result):
                entries = list_videos(d)

        self.assertEqual(len(entries), 2)
        names = {e.path.name for e in entries}
        self.assertEqual(names, {"a.mp4", "b.mkv"})

    def test_sorted_by_name(self):
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp)
            for name in ["c.mp4", "a.mp4", "b.mp4"]:
                (d / name).touch()

            pr = _make_probe_result()
            with patch("mediatools.probe.probe", return_value=pr):
                entries = list_videos(d, sort_by="name")

        self.assertEqual([e.path.name for e in entries], ["a.mp4", "b.mp4", "c.mp4"])

    def test_directory_not_found(self):
        with self.assertRaises(FileNotFoundError):
            list_videos("/nonexistent/path/xyz")

    def test_not_a_directory(self):
        with tempfile.NamedTemporaryFile(suffix=".mp4") as f:
            with self.assertRaises(NotADirectoryError):
                list_videos(f.name)

    def test_invalid_sort_key(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):
                list_videos(tmp, sort_by="invalid")

    def test_skips_probe_failures(self):
        from mediatools.probe import ProbeError
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp)
            (d / "good.mp4").touch()
            (d / "bad.mp4").touch()

            call_count = 0

            def selective_probe(p, **kw):
                nonlocal call_count
                call_count += 1
                if "bad" in str(p):
                    raise ProbeError("corrupt")
                return _make_probe_result()

            with patch("mediatools.probe.probe", side_effect=selective_probe):
                entries = list_videos(d)

        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0].path.name, "good.mp4")

    def test_entry_fields_populated(self):
        with tempfile.TemporaryDirectory() as tmp:
            d = Path(tmp)
            (d / "v.mp4").touch()

            pr = _make_probe_result(duration_ms=10000, width=1280, height=720, fps=24.0)
            with patch("mediatools.probe.probe", return_value=pr):
                entries = list_videos(d)

        e = entries[0]
        self.assertIsInstance(e, VideoEntry)
        self.assertEqual(e.duration_ms, 10000)
        self.assertEqual(e.width, 1280)
        self.assertEqual(e.height, 720)
        self.assertAlmostEqual(e.fps, 24.0)
        self.assertEqual(e.codec, "h264")


# ---------------------------------------------------------------------------
# write_manifest / read_manifest
# ---------------------------------------------------------------------------

class TestManifest(unittest.TestCase):

    def _make_entries(self, names):
        return [
            VideoEntry(
                path=Path(f"/videos/{n}"),
                duration_ms=5000, size_bytes=1000,
                width=1920, height=1080, fps=30.0, codec="h264",
            )
            for n in names
        ]

    def test_write_creates_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            entries = self._make_entries(["clip1.mp4", "clip2.mp4"])
            manifest_path = Path(tmp) / "manifest.json"
            write_manifest(entries, manifest_path)
            self.assertTrue(manifest_path.exists())

    def test_write_contains_clips(self):
        with tempfile.TemporaryDirectory() as tmp:
            entries = self._make_entries(["clip1.mp4", "clip2.mp4", "clip3.mp4"])
            manifest_path = Path(tmp) / "manifest.json"
            write_manifest(entries, manifest_path)
            data = json.loads(manifest_path.read_text())
            self.assertEqual(len(data["clips"]), 3)
            self.assertIn("output", data)

    def test_write_stores_duration_and_resolution(self):
        with tempfile.TemporaryDirectory() as tmp:
            entries = self._make_entries(["clip.mp4"])
            manifest_path = Path(tmp) / "manifest.json"
            write_manifest(entries, manifest_path)
            data = json.loads(manifest_path.read_text())
            clip = data["clips"][0]
            self.assertEqual(clip["duration_ms"], 5000)
            self.assertEqual(clip["resolution"], "1920x1080")

    def test_write_custom_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            entries = self._make_entries(["a.mp4"])
            manifest_path = Path(tmp) / "manifest.json"
            write_manifest(entries, manifest_path, output_video=Path(tmp) / "final.mp4")
            data = json.loads(manifest_path.read_text())
            self.assertIn("final.mp4", data["output"])

    def test_roundtrip(self):
        with tempfile.TemporaryDirectory() as tmp:
            entries = self._make_entries(["x.mp4", "y.mp4"])
            manifest_path = Path(tmp) / "manifest.json"
            write_manifest(entries, manifest_path, output_video=Path(tmp) / "reel.mp4")
            clips, output = read_manifest(manifest_path)
            self.assertEqual(len(clips), 2)
            self.assertIn("reel.mp4", str(output))

    def test_read_missing_file(self):
        with self.assertRaises(FileNotFoundError):
            read_manifest("/nonexistent/manifest.json")

    def test_read_missing_clips_key(self):
        with tempfile.NamedTemporaryFile(
            suffix=".json", mode="w", delete=False
        ) as f:
            f.write(json.dumps({"output": "reel.mp4"}))
            p = f.name
        with self.assertRaises(ValueError) as ctx:
            read_manifest(p)
        self.assertIn("clips", str(ctx.exception))

    def test_read_plain_path_strings(self):
        """Manifest clips as plain strings (not dicts) are accepted."""
        with tempfile.TemporaryDirectory() as tmp:
            manifest_path = Path(tmp) / "m.json"
            manifest_path.write_text(json.dumps({
                "output": "out.mp4",
                "clips": ["/a.mp4", "/b.mp4"],
            }))
            clips, _ = read_manifest(manifest_path)
        self.assertEqual(len(clips), 2)


# ---------------------------------------------------------------------------
# concat_videos
# ---------------------------------------------------------------------------

class TestConcatVideos(unittest.TestCase):

    def _run(self, num_clips=3, returncode=0, side_effect=None,
             re_encode=False, output="reel.mp4"):
        mock_result = _mock_run(returncode)
        run_kwargs = {"side_effect": side_effect} if side_effect else {"return_value": mock_result}

        with tempfile.TemporaryDirectory() as tmp:
            clips = []
            for i in range(num_clips):
                p = Path(tmp) / f"clip{i}.mp4"
                p.touch()
                clips.append(p)
            out = Path(tmp) / output

            with patch("mediatools.video.subprocess.run", **run_kwargs), \
                 patch("mediatools.video.Path.mkdir"):
                return concat_videos(clips, out, re_encode=re_encode)

    def test_returns_output_path(self):
        result = self._run()
        self.assertIsInstance(result, Path)
        self.assertEqual(result.name, "reel.mp4")

    def test_too_few_inputs(self):
        with self.assertRaises(ValueError) as ctx:
            self._run(num_clips=1)
        self.assertIn("2", str(ctx.exception))

    def test_missing_input_raises(self):
        with self.assertRaises(FileNotFoundError):
            concat_videos([Path("/nonexistent/a.mp4"), Path("/nonexistent/b.mp4")],
                          Path("/tmp/out.mp4"))

    def test_no_output_for_list_raises(self):
        with tempfile.TemporaryDirectory() as tmp:
            clips = [Path(tmp) / f"c{i}.mp4" for i in range(2)]
            for c in clips:
                c.touch()
            with self.assertRaises(ValueError) as ctx:
                concat_videos(clips, None)
            self.assertIn("output", str(ctx.exception))

    def test_ffmpeg_not_on_path(self):
        with self.assertRaises(VideoError) as ctx:
            self._run(side_effect=FileNotFoundError)
        self.assertIn("ffmpeg not found", str(ctx.exception))

    def test_ffmpeg_nonzero_exit(self):
        with self.assertRaises(VideoError):
            self._run(returncode=1)

    def test_re_encode_uses_libx264(self):
        captured = []

        def capture(cmd, **kwargs):
            captured.append(cmd)
            return _mock_run()

        with tempfile.TemporaryDirectory() as tmp:
            clips = [Path(tmp) / f"c{i}.mp4" for i in range(2)]
            for c in clips:
                c.touch()
            with patch("mediatools.video.subprocess.run", side_effect=capture), \
                 patch("mediatools.video.Path.mkdir"):
                concat_videos(clips, Path(tmp) / "out.mp4", re_encode=True)

        cmd = captured[0]
        self.assertIn("libx264", cmd)
        self.assertIn("aac", cmd)

    def test_stream_copy_uses_c_copy(self):
        captured = []

        def capture(cmd, **kwargs):
            captured.append(cmd)
            return _mock_run()

        with tempfile.TemporaryDirectory() as tmp:
            clips = [Path(tmp) / f"c{i}.mp4" for i in range(2)]
            for c in clips:
                c.touch()
            with patch("mediatools.video.subprocess.run", side_effect=capture), \
                 patch("mediatools.video.Path.mkdir"):
                concat_videos(clips, Path(tmp) / "out.mp4")

        cmd = captured[0]
        self.assertIn("copy", cmd)
        self.assertNotIn("libx264", cmd)

    def test_manifest_input(self):
        with tempfile.TemporaryDirectory() as tmp:
            clips = [Path(tmp) / f"c{i}.mp4" for i in range(3)]
            for c in clips:
                c.touch()
            manifest_path = Path(tmp) / "manifest.json"
            out_path = Path(tmp) / "reel.mp4"

            entries = [
                VideoEntry(
                    path=c, duration_ms=5000, size_bytes=1000,
                    width=1920, height=1080, fps=30.0, codec="h264",
                )
                for c in clips
            ]
            write_manifest(entries, manifest_path, output_video=out_path)

            with patch("mediatools.video.subprocess.run", return_value=_mock_run()), \
                 patch("mediatools.video.Path.mkdir"):
                result = concat_videos(manifest_path)

        self.assertEqual(result.name, "reel.mp4")


if __name__ == "__main__":
    unittest.main()
