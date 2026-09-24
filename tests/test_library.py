import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from watch_link.library import Library


class AvailableMovies(unittest.TestCase):
    def test_add_remove_stable_links_and_failure_preservation(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            media = root / "movies"
            media.mkdir()
            movie = media / "A & B.mp4"
            movie.write_bytes(b"movie fixture")
            auth = root / "auth.json"
            auth.write_text('{"token":"test"}')
            config = root / "dashboard.json"
            config.write_text('{"services":[],"movies":[]}')
            page = root / "index.html"
            library = Library(
                "http://localhost:8096",
                str(auth),
                str(media),
                "https://example.com/media",
                "https://example.com/i",
                str(root / "invitations"),
                str(config),
                str(page),
                str(root / "state.json"),
            )
            feed = json.dumps(
                {"Items": [{"Name": "A & B", "ProductionYear": 2000, "Path": "/media/movies/A & B.mp4"}]}
            ).encode()
            for _ in range(2):
                with patch("watch_link.library.urlopen", return_value=io.BytesIO(feed)):
                    self.assertEqual(library.refresh(), 1)
                self.assertEqual(len(list((root / "invitations").iterdir())), 2)
            self.assertIn("A &amp; B (2000)", page.read_text())
            before = page.read_bytes()
            with patch("watch_link.library.urlopen", side_effect=OSError("offline")), self.assertRaises(OSError):
                library.refresh()
            self.assertEqual(page.read_bytes(), before)
            movie.unlink()
            with patch("watch_link.library.urlopen", return_value=io.BytesIO(feed)):
                self.assertEqual(library.refresh(), 0)
            self.assertEqual(json.loads(config.read_text())["movies"], [])
            self.assertIn("No movies are available", page.read_text())
