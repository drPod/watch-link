import os
import subprocess
import tempfile
import unittest
from pathlib import Path

from watch_link.cli import Invitation, create, token_value


class Invitations(unittest.TestCase):
    def test_rejects_non_https_and_bad_rooms(self) -> None:
        for movie in ("file:///etc/passwd", "http://example.com/a", "https://x/a\nb", "https://u:p@x/a"):
            with self.assertRaises(ValueError):
                Invitation(movie, "room")
        for room in ("x\ny", "$(whoami)", "a b"):
            with self.assertRaises(ValueError):
                Invitation("https://example.com/a", room)
        with self.assertRaises(ValueError):
            token_value("../escape")

    def test_unique_private_files_and_no_overwrite(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            invite = Invitation("https://example.com/a.mp4", "room")
            path = create(invite, root, "a" * 24)
            self.assertEqual((path / "mac").stat().st_mode & 0o777, 0o600)
            self.assertEqual(path.stat().st_mode & 0o777, 0o700)
            with self.assertRaises(FileExistsError):
                create(invite, root, "a" * 24)
            self.assertIn("movie=https://", (path / "mac").read_text())

    def run_mac_fallback(self, movie: str, *args: str) -> tuple[subprocess.CompletedProcess[str], str]:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            bin_path = root / "bin"
            bin_path.mkdir()
            calls = root / "calls"
            for name, body in {
                "uname": "printf Darwin",
                "open": 'printf "%s" "$1" > "$CALLS"',
            }.items():
                path = bin_path / name
                path.write_text("#!/bin/sh\n" + body + "\n")
                path.chmod(0o700)
            env = dict(os.environ, HOME=temp, PATH=f"{bin_path}:/usr/bin:/bin", CALLS=str(calls))
            result = subprocess.run(
                ["/bin/bash", "-s", "--", *args],
                input=Invitation(movie, "room").render(),
                text=True,
                capture_output=True,
                env=env,
                check=False,
            )
            return result, calls.read_text() if calls.exists() else ""

    def test_browser_fallback_passes_url_literally(self) -> None:
        movie = "https://example.com/a'$(id);$HOME.mp4?foo=bar&x=1"
        result, called = self.run_mac_fallback(movie)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(called, movie)
        self.assertIn("without installing", result.stdout)

    def test_dry_run_and_unknown_flags_do_not_launch(self) -> None:
        for args, status in ((["--dry-run", "--sync"], 0), (["--oops"], 2)):
            result, called = self.run_mac_fallback("https://example.com/a.mp4", *args)
            self.assertEqual(result.returncode, status)
            self.assertEqual(called, "")

    def test_existing_players_reused_in_solo_and_sync(self) -> None:
        for app, binary in (("IINA", "iina-cli"), ("VLC", "VLC"), ("mpv", "mpv")):
            for sync in (False, True):
                with self.subTest(player=app, sync=sync), tempfile.TemporaryDirectory() as temp:
                    root = Path(temp)
                    bin_path = root / "bin"
                    bin_path.mkdir()
                    calls = root / "calls"
                    player = (
                        bin_path / "mpv" if app == "mpv" else root / f"Applications/{app}.app/Contents/MacOS/{binary}"
                    )
                    syncplay = root / "Applications/Syncplay.app/Contents/MacOS/Syncplay"
                    for path, body in {
                        bin_path / "uname": "printf Darwin",
                        bin_path / "open": 'printf "%s\\n" "$@" > "$CALLS"',
                        bin_path / "brew": "echo unexpected-install >&2; exit 99",
                        player: 'printf "%s\\n" "$@" > "$CALLS"',
                        syncplay: 'printf "%s\\n" "$@" > "$CALLS"',
                    }.items():
                        path.parent.mkdir(parents=True, exist_ok=True)
                        path.write_text("#!/bin/sh\n" + body + "\n")
                        path.chmod(0o700)
                    launcher = root / "launch.sh"
                    launcher.write_text(Invitation("https://example.com/movie.mp4", "room", sync=sync).render())
                    env = dict(os.environ, HOME=temp, PATH=f"{bin_path}:/usr/bin:/bin", CALLS=str(calls))
                    result = subprocess.run(
                        ["script", "-qec", f"bash {launcher}", "/dev/null"],
                        env=env,
                        text=True,
                        capture_output=True,
                        check=False,
                        timeout=10,
                    )
                    self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
                    recorded = calls.read_text()
                    self.assertIn("https://example.com/movie.mp4", recorded)
                    if sync:
                        self.assertIn(str(player), recorded)
                        self.assertIn("--no-store", recorded)

    def test_syntax_and_powershell_escaping(self) -> None:
        invite = Invitation("https://example.com/a'b.mp4", "room", sync=True)
        result = subprocess.run(["bash", "-n"], input=invite.render(), text=True, capture_output=True, check=False)
        self.assertEqual(result.returncode, 0, result.stderr)
        script = invite.render(True)
        self.assertIn("a''b.mp4", script)
        self.assertIn("$useSync = $true", script)
        self.assertNotIn("@@", script)


if __name__ == "__main__":
    unittest.main()
