import io
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from watch_link.guide import refresh


class Guide(unittest.TestCase):
    def test_filters_feed_and_preserves_last_good_on_failure(self) -> None:
        feed = b'<tv><channel id="a"><display-name>A</display-name></channel><channel id="b"/>'
        feed += b'<programme channel="a"><desc>Before title</desc><title>A show</title></programme>'
        feed += b'<programme channel="b"><title>Other</title></programme></tv>'
        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp) / "guide.xml"
            with patch("watch_link.guide.urlopen", return_value=io.BytesIO(feed)):
                self.assertEqual(refresh("https://example.com/guide.xml", {"a"}, target), (1, 1))
            original = target.read_bytes()
            self.assertIn(b"A show", original)
            self.assertNotIn(b"Other", original)
            with patch("watch_link.guide.urlopen", return_value=io.BytesIO(b"<tv/>")), self.assertRaises(ValueError):
                refresh("https://example.com/guide.xml", {"a"}, target)
            self.assertEqual(target.read_bytes(), original)
            self.assertEqual(list(Path(temp).iterdir()), [target])
