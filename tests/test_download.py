"""Tests for mediatools.download.pull_video and default_downloads_dir."""

import platform
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from mediatools.download import DownloadError, _write_credits, default_downloads_dir, fetch_info, pull_video


class TestDefaultDownloadsDir(unittest.TestCase):

    def test_windows(self):
        with patch("mediatools.download.platform.system", return_value="Windows"):
            result = default_downloads_dir()
        self.assertEqual(result, Path.home() / "Downloads")

    def test_macos(self):
        with patch("mediatools.download.platform.system", return_value="Darwin"):
            result = default_downloads_dir()
        self.assertEqual(result, Path.home() / "Downloads")

    def test_linux_default(self):
        with patch("mediatools.download.platform.system", return_value="Linux"), \
             patch.dict("os.environ", {}, clear=False), \
             patch("mediatools.download.os.environ.get", return_value=None), \
             patch("mediatools.download.Path.home", return_value=Path("/home/user")):
            result = default_downloads_dir()
        self.assertEqual(result, Path("/home/user/Downloads"))

    def test_linux_xdg(self):
        with patch("mediatools.download.platform.system", return_value="Linux"), \
             patch.dict("os.environ", {"XDG_DOWNLOAD_DIR": "/data/downloads"}):
            result = default_downloads_dir()
        self.assertEqual(result, Path("/data/downloads"))


class TestPullVideo(unittest.TestCase):

    def _make_ydl(self, downloaded_path: str | None = "/tmp/video.mp4"):
        """Build a mock yt_dlp.YoutubeDL context manager."""
        mock_ydl = MagicMock()
        mock_ydl.__enter__ = MagicMock(return_value=mock_ydl)
        mock_ydl.__exit__ = MagicMock(return_value=False)

        # Simulate progress hook firing with status=finished
        def fake_download(urls):
            # trigger the progress hook registered in pull_video
            pass

        mock_ydl.download = fake_download
        return mock_ydl

    def test_yt_dlp_not_installed(self):
        with patch.dict("sys.modules", {"yt_dlp": None}):
            with self.assertRaises(DownloadError) as ctx:
                pull_video("https://example.com/video")
            self.assertIn("yt-dlp is required", str(ctx.exception))

    def test_download_error_on_exception(self):
        mock_ydl = MagicMock()
        mock_ydl.__enter__ = MagicMock(return_value=mock_ydl)
        mock_ydl.__exit__ = MagicMock(return_value=False)
        mock_ydl.download = MagicMock(side_effect=Exception("network error"))

        mock_module = MagicMock()
        mock_module.YoutubeDL = MagicMock(return_value=mock_ydl)

        with patch.dict("sys.modules", {"yt_dlp": mock_module}), \
             patch("mediatools.download.Path.mkdir"):
            with self.assertRaises(DownloadError) as ctx:
                pull_video("https://example.com/video", output_dir="/tmp")
            self.assertIn("download failed", str(ctx.exception))

    def test_uses_default_downloads_dir_when_no_output(self):
        """pull_video with no output_dir calls default_downloads_dir()."""
        with patch("mediatools.download.default_downloads_dir",
                   return_value=Path("/fake/downloads")) as mock_default, \
             patch("mediatools.download.Path.mkdir"), \
             patch("mediatools.download.Path.iterdir",
                   return_value=iter([Path("/fake/downloads/video.mp4")])), \
             patch("mediatools.download.Path.stat",
                   return_value=MagicMock(st_mtime=1000)):
            mock_ydl = MagicMock()
            mock_ydl.__enter__ = MagicMock(return_value=mock_ydl)
            mock_ydl.__exit__ = MagicMock(return_value=False)
            mock_ydl.download = MagicMock()

            mock_module = MagicMock()
            mock_module.YoutubeDL = MagicMock(return_value=mock_ydl)

            with patch.dict("sys.modules", {"yt_dlp": mock_module}):
                pull_video("https://example.com/video")

            mock_default.assert_called_once()

    def test_custom_output_dir(self):
        """pull_video respects a custom output_dir."""
        mock_ydl = MagicMock()
        mock_ydl.__enter__ = MagicMock(return_value=mock_ydl)
        mock_ydl.__exit__ = MagicMock(return_value=False)
        mock_ydl.download = MagicMock()

        mock_module = MagicMock()
        mock_module.YoutubeDL = MagicMock(return_value=mock_ydl)

        captured_opts: list[dict] = []

        def capture_ydl(opts):
            captured_opts.append(opts)
            return mock_ydl

        mock_module.YoutubeDL = capture_ydl

        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            with patch.dict("sys.modules", {"yt_dlp": mock_module}), \
                 patch("mediatools.download.Path.mkdir"), \
                 patch("mediatools.download.Path.iterdir",
                       return_value=iter([Path(tmp) / "video.mp4"])), \
                 patch("mediatools.download.Path.stat",
                       return_value=MagicMock(st_mtime=1000)):
                pull_video("https://example.com/video", output_dir=tmp)

            self.assertIn(tmp, captured_opts[0]["outtmpl"])


class TestFetchInfo(unittest.TestCase):

    def _mock_module(self, info_data=None, side_effect=None):
        mock_ydl = MagicMock()
        mock_ydl.__enter__ = MagicMock(return_value=mock_ydl)
        mock_ydl.__exit__ = MagicMock(return_value=False)
        if side_effect:
            mock_ydl.extract_info = MagicMock(side_effect=side_effect)
        else:
            mock_ydl.extract_info = MagicMock(return_value=info_data or {
                "title": "Test Video",
                "uploader": "Test Channel",
                "channel": "Test Channel",
                "channel_url": "https://youtube.com/c/test",
                "upload_date": "20260101",
                "duration": 120.0,
                "description": "A description",
                "webpage_url": "https://youtube.com/watch?v=abc",
                "extractor": "youtube",
                "tags": ["tag1"],
                "view_count": 1000,
                "like_count": 50,
                "formats": [],
            })
        mock_module = MagicMock()
        mock_module.YoutubeDL = MagicMock(return_value=mock_ydl)
        return mock_module

    def test_returns_info_dict(self):
        with patch.dict("sys.modules", {"yt_dlp": self._mock_module()}):
            result = fetch_info("https://youtube.com/watch?v=abc")
        self.assertEqual(result["title"], "Test Video")
        self.assertEqual(result["source_url"], "https://youtube.com/watch?v=abc")
        self.assertEqual(result["creator"]["uploader"], "Test Channel")
        self.assertIn("formats", result)

    def test_yt_dlp_not_installed(self):
        with patch.dict("sys.modules", {"yt_dlp": None}):
            with self.assertRaises(DownloadError) as ctx:
                fetch_info("https://youtube.com/watch?v=abc")
            self.assertIn("yt-dlp is required", str(ctx.exception))

    def test_error_on_exception(self):
        mock_module = self._mock_module(side_effect=Exception("not found"))
        with patch.dict("sys.modules", {"yt_dlp": mock_module}):
            with self.assertRaises(DownloadError) as ctx:
                fetch_info("https://youtube.com/watch?v=abc")
            self.assertIn("could not fetch info", str(ctx.exception))

    def test_no_download_called(self):
        """extract_info must be called with download=False."""
        mock_module = self._mock_module()
        with patch.dict("sys.modules", {"yt_dlp": mock_module}):
            fetch_info("https://youtube.com/watch?v=abc")
        ydl_instance = mock_module.YoutubeDL.return_value.__enter__.return_value
        ydl_instance.extract_info.assert_called_once_with(
            "https://youtube.com/watch?v=abc", download=False
        )


class TestWriteCredits(unittest.TestCase):

    def test_credits_file_created(self):
        import json
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            video = Path(tmp) / "video.mp4"
            video.touch()
            info = {
                "title": "Test Video",
                "uploader": "Test Channel",
                "channel": "Test Channel",
                "channel_url": "https://youtube.com/c/test",
                "upload_date": "20260101",
                "duration": 120.0,
                "description": "A test video",
                "webpage_url": "https://youtube.com/watch?v=abc",
                "extractor": "youtube",
                "tags": ["test", "video"],
                "view_count": 1000,
                "like_count": 50,
                "license": "Creative Commons Attribution",
            }
            credits_path = _write_credits(video, "https://youtube.com/watch?v=abc", info)
            self.assertTrue(credits_path.exists())
            self.assertEqual(credits_path.name, "video.credits.json")
            data = json.loads(credits_path.read_text())
            self.assertEqual(data["title"], "Test Video")
            self.assertEqual(data["source_url"], "https://youtube.com/watch?v=abc")
            self.assertEqual(data["creator"]["uploader"], "Test Channel")
            self.assertEqual(data["license"], "Creative Commons Attribution")
            self.assertIn("downloaded_at", data)

    def test_credits_none_values_omitted(self):
        import json
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            video = Path(tmp) / "clip.mp4"
            video.touch()
            credits_path = _write_credits(video, "https://example.com/v", {"title": "Clip"})
            data = json.loads(credits_path.read_text())
            self.assertNotIn("uploader", data.get("creator", {}))
            self.assertNotIn("view_count", data)


if __name__ == "__main__":
    unittest.main()
