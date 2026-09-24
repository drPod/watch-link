import argparse
import fcntl
import json
import secrets
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import quote
from urllib.request import Request, urlopen

from .cli import Invitation, create, https_url
from .dashboard import render, write_private


@dataclass(frozen=True)
class Library:
    jellyfin_url: str
    auth_file: str
    movie_root: str
    media_base: str
    invitation_base: str
    invitation_output: str
    dashboard_config: str
    dashboard_output: str
    state_file: str
    jellyfin_root: str = "/media/movies"
    syncplay_server: str = "syncplay.pl:8999"

    def movies(self) -> list[tuple[str, str]]:
        auth = json.loads(Path(self.auth_file).read_text())
        request = Request(
            self.jellyfin_url.rstrip("/") + "/Items?Recursive=true&IncludeItemTypes=Movie&Fields=Path",
            headers={"Authorization": f'MediaBrowser Token="{auth["token"]}"'},
        )
        with urlopen(request, timeout=30) as response:
            inventory = json.load(response)
        root = Path(self.movie_root).resolve(strict=True)
        movies = []
        for item in inventory["Items"]:
            if not item.get("Path"):
                continue
            try:
                relative = Path(item["Path"]).relative_to(self.jellyfin_root)
                local = (root / relative).resolve()
                local.relative_to(root)
            except ValueError:
                continue
            if not local.is_file() or not local.stat().st_size:
                continue
            name = str(item["Name"])
            if item.get("ProductionYear"):
                name += f" ({item['ProductionYear']})"
            movies.append((relative.as_posix(), name))
        return sorted(set(movies), key=lambda movie: (movie[1].casefold(), movie[0]))

    def refresh(self) -> int:
        state_path = Path(self.state_file)
        state_path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        with state_path.with_suffix(".lock").open("w") as lock:
            fcntl.flock(lock, fcntl.LOCK_EX)
            inventory = self.movies()
            state: dict[str, dict[str, str]] = json.loads(state_path.read_text()) if state_path.exists() else {}
            dashboard = json.loads(Path(self.dashboard_config).read_text())
            movies = []
            for relative, name in inventory:
                if relative not in state:
                    entry = {"name": name}
                    room = secrets.token_urlsafe(18)
                    for mode in ("solo", "sync"):
                        token = secrets.token_urlsafe(18)
                        create(
                            Invitation(
                                https_url(self.media_base).rstrip("/") + "/" + quote(relative),
                                room,
                                self.syncplay_server,
                                mode == "sync",
                            ),
                            Path(self.invitation_output),
                            token,
                        )
                        entry[mode] = https_url(self.invitation_base).rstrip("/") + "/" + token
                    state[relative] = entry
                    write_private(state_path, json.dumps(state, indent=2) + "\n")
                state[relative]["name"] = name
                movies.append(state[relative])
            dashboard["movies"] = movies
            page = render(dashboard)
            write_private(state_path, json.dumps(state, indent=2) + "\n")
            write_private(Path(self.dashboard_config), json.dumps(dashboard, indent=2) + "\n")
            write_private(Path(self.dashboard_output), page)
            return len(movies)


def main() -> None:
    parser = argparse.ArgumentParser(description="Refresh playback invitations from Jellyfin's available movies")
    parser.add_argument("--config", type=Path, required=True)
    args = parser.parse_args()
    library = Library(**json.loads(args.config.read_text()))
    print(f"Available movies: {library.refresh()}")


if __name__ == "__main__":
    main()
