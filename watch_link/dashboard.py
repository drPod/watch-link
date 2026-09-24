import argparse
import json
import shlex
from html import escape
from pathlib import Path

from .cli import https_url


def render(config: dict[str, list[dict[str, str]]]) -> str:
    services = "".join(
        f'<a class="service" href="{escape(https_url(item["url"]), quote=True)}">'
        f"<strong>{escape(item['name'])}</strong><span>{escape(item['description'])}</span></a>"
        for item in config["services"]
    )
    movies = []
    for movie in config["movies"]:
        modes = []
        for key, label in (("solo", "Watch solo"), ("sync", "Watch together")):
            base = https_url(movie[key]).rstrip("/")
            mac = f"curl -fsSL {shlex.quote(base + '/mac')} | bash"
            windows_url = (base + "/windows.ps1").replace("'", "''")
            windows = f"& ([scriptblock]::Create((Invoke-RestMethod '{windows_url}')))"
            modes.append(
                f'<option data-mac="{escape(mac, quote=True)}" data-windows="{escape(windows, quote=True)}" '
                f'data-url="{escape(base, quote=True)}">{label}</option>'
            )
        movies.append(
            f'<article><h3>{escape(movie["name"])}</h3><label>Playback <select class="mode">'
            + "".join(modes)
            + '</select></label><pre><code></code></pre><div class="actions"><button class="copy">Copy command</button>'
            '<a class="inspect" target="_blank" rel="noopener">View script</a>'
            '<a class="download" download>Download script</a></div><p class="status" aria-live="polite"></p></article>'
        )
    template = Path(__file__).with_name("templates").joinpath("dashboard.html").read_text()
    return template.replace("@@SERVICES@@", services).replace("@@MOVIES@@", "".join(movies))


def main() -> None:
    parser = argparse.ArgumentParser(description="Build a private static media start page")
    parser.add_argument("--config", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    page = render(json.loads(args.config.read_text()))
    args.output.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    args.output.write_text(page)
    args.output.chmod(0o600)


if __name__ == "__main__":
    main()
