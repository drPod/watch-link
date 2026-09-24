import argparse
import json
import os
import re
import secrets
import shlex
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlsplit

TEMPLATES = Path(__file__).with_name("templates")


def https_url(value: str) -> str:
    parsed = urlsplit(value)
    if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
        raise ValueError("Use an absolute HTTPS URL without embedded login credentials")
    if any(ord(c) < 33 for c in value) or "\\" in value:
        raise ValueError("URL must be encoded and contain no whitespace or backslashes")
    return value


def token_value(value: str) -> str:
    if not re.fullmatch(r"[A-Za-z0-9_-]{16,128}", value):
        raise ValueError("Invitation tokens must contain 16–128 URL-safe letters, digits, underscores or hyphens")
    return value


@dataclass(frozen=True)
class Invitation:
    movie: str
    room: str
    server: str = "syncplay.pl:8999"
    sync: bool = False

    def __post_init__(self) -> None:
        https_url(self.movie)
        if not re.fullmatch(r"[A-Za-z0-9_-]{1,128}", self.room):
            raise ValueError("Room must contain only letters, digits, underscores and hyphens")
        if not re.fullmatch(r"[A-Za-z0-9.-]+:[0-9]{1,5}", self.server):
            raise ValueError("Syncplay server must be hostname:port")
        if not 1 <= int(self.server.rsplit(":", 1)[1]) <= 65535:
            raise ValueError("Invalid server port")

    def render(self, windows: bool = False) -> str:
        if windows:
            quote = lambda s: "'" + s.replace("'", "''") + "'"
            values = {
                "MOVIE": quote(self.movie),
                "ROOM": quote(self.room),
                "SERVER": quote(self.server),
                "SYNC": "$true" if self.sync else "$false",
            }
        else:
            values = {
                "MOVIE": shlex.quote(self.movie),
                "ROOM": shlex.quote(self.room),
                "SERVER": shlex.quote(self.server),
                "SYNC": "1" if self.sync else "0",
            }
        source = (TEMPLATES / ("launch.ps1" if windows else "launch.sh")).read_text()
        return re.sub(r"@@(MOVIE|ROOM|SERVER|SYNC)@@", lambda m: values[m[1]], source)


def create(invite: Invitation, output: Path, token: str) -> Path:
    token_value(token)
    output.mkdir(parents=True, exist_ok=True, mode=0o700)
    target = output / token
    target.mkdir(mode=0o700)
    try:
        for name, content in (("mac", invite.render()), ("windows.ps1", invite.render(True))):
            path = target / name
            path.write_text(content)
            path.chmod(0o600)
    except BaseException:
        for path in target.iterdir():
            path.unlink()
        target.rmdir()
        raise
    return target


def main() -> None:
    parser = argparse.ArgumentParser(description="Create static, private playback invitations for Caddy")
    commands = parser.add_subparsers(dest="command", required=True)
    new = commands.add_parser("invite")
    new.add_argument("--movie", required=True, help="Original HTTPS media URL")
    new.add_argument("--base-url", required=True, help="Public invitation prefix, e.g. https://watch.example.com/i")
    new.add_argument("--output", type=Path, required=True, help="Private directory served by Caddy")
    new.add_argument("--sync", action="store_true")
    new.add_argument("--room", default=None)
    new.add_argument("--server", default="syncplay.pl:8999")
    revoke = commands.add_parser("revoke")
    revoke.add_argument("token")
    revoke.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        if args.command == "revoke":
            target = args.output / token_value(args.token)
            for name in ("mac", "windows.ps1"):
                (target / name).unlink(missing_ok=True)
            target.rmdir()
            print("Invitation removed. Already-received movie URLs remain valid; rotate media access to revoke those.")
            return
        base = https_url(args.base_url).rstrip("/")
        if urlsplit(base).query or urlsplit(base).fragment:
            raise ValueError("Base URL cannot contain a query or fragment")
        token = secrets.token_urlsafe(18)
        invitation = Invitation(args.movie, args.room or secrets.token_urlsafe(18), args.server, args.sync)
        os.umask(0o077)
        create(invitation, args.output, token)
        url = f"{base}/{token}"
        print(
            json.dumps(
                {
                    "token": token,
                    "room": invitation.room,
                    "sync": invitation.sync,
                    "mac": f"curl -fsSL {shlex.quote(url + '/mac')} | bash",
                    "windows": "& ([scriptblock]::Create((Invoke-RestMethod '"
                    + (url + "/windows.ps1").replace("'", "''")
                    + "')))",
                },
                indent=2,
            )
        )
    except (ValueError, OSError) as error:
        parser.exit(1, f"Error: {error}\n")
