# Working on Watch Link

Read README.md, docs/OPERATIONS.md and docs/VERIFICATION.md first.

## Find the implementation

| Task | Start here |
|---|---|
| Private service home / workspace link | `watch_link/dashboard.py`, `watch_link/templates/dashboard.html` |
| Playback invitations and scripts | `watch_link/cli.py`, `watch_link/templates/launch.sh`, `launch.ps1` |
| Containers, VPN and proxy | `deploy/`, `docs/SERVER.md` |
| Jellyfin channels and guide refresh | `docs/JELLYFIN.md`, `watch_link/guide.py`, `deploy/systemd/` |
| Verification and known limitations | `docs/VERIFICATION.md` |
| Live installation and private links | `~/.local/state/watch-link/OPERATIONS.md` (never publish) |

## Change the deployed start page

1. Read the private runbook. On the original VPS, `~/deploy/media-stack/dashboard.json` owns
   service labels/URLs and movie invitations; `dashboard-links.json` records private entry links.
2. Edit the source template here or the private config as appropriate. Regenerate with
   `uv run python -m watch_link.dashboard --config /PRIVATE/dashboard.json --output /PRIVATE/TOKEN/index.html`.
   Preserve the deployed token/output path unless intentionally rotating access.
3. Verify page HTML, service destinations, Mac/Windows solo/together copy/download controls and
   unknown-path rejection. Static page edits need no Caddy reload. Proxy edits require validation.
4. Keep `PRIVATE-LINKS.md`, the Mac shortcut and private runbook current if URLs change. Preserve
   both-machine configuration backups. Source synchronization alone does not regenerate the page.

The workspace link is owned by VPS Workspaces: use its `remote.py link <workspace>` command.
Check the registry's `hapi_session` against the intended conversation before changing that link.
Do not fork or restart the agent just to add a browser link.

## Working rules

- Reuse Caddy, Syncplay, upstream players, WinGet/Homebrew and official installers.
  Do not implement a player, synchronization engine, scraper or VPN firewall.
- Preserve the player-first policy in both modes. Solo defaults to browser fallback;
  installation is opt-in except when shared playback requires it. Never install Homebrew.
- Python host code is typed and managed with uv. Match the committed Ruff rules (120 columns,
  shared with VPS Workspaces/Sixtyfive). Keep comments/docstrings to non-obvious constraints.
- Templates are Bash 3.2-compatible for macOS and Windows PowerShell 5.1-compatible.
  Quote invitation data as data; never evaluate URL/room content as commands. No eval.
- Runtime invitations, credentials, app databases, private URLs and user media stay outside Git.
  Do not weaken Gatekeeper, remove quarantine, disable CSRF or expose torrent traffic outside Gluetun.
- In the original deployment ~/Coding is bidirectionally synchronized by Mutagen, including Git.
  Edit one checkout, check sync conflicts, and deploy explicitly. Source sync is not deployment.
- Back up affected private configuration before deployment. Validate Caddy before reloading.
  Preserve existing workspace services and Mac originals; restart only affected media services.
- Preserve unencrypted snapshots on both machines. Media itself is excluded unless explicitly selected.
- Run uv sync --locked, Ruff lint/format, mypy, unittest, and shell/PowerShell syntax checks.
  Use focused behavioral tests for URL quoting, player reuse, browser fallback and no unexpected installs.
  Report Windows/fresh-machine checks as unverified until actually run on those platforms.

Code: watch_link/cli.py creates/revokes static invitations; templates/ owns local launchers.
Deployment: deploy/ contains reusable Compose/Caddy examples; docs/SERVER.md is the server guide.
Private local runbook, when present: ~/.local/state/watch-link/OPERATIONS.md. Never publish it.

Private dashboard links, when configured, are in `~/deploy/media-stack/PRIVATE-LINKS.md`
and `dashboard-links.json`; Mac copy `~/Movies/VPS-Media/PRIVATE-LINKS.md`. Read locally,
never put their contents in commits. See docs/OPERATIONS.md for cookie access and rotation.

Guide refresh uses `watch_link/guide.py` and resource-limited native systemd units in
`deploy/systemd/`. Read docs/JELLYFIN.md. Never parse the full community XMLTV feed into memory.

Private service start page: `watch_link/dashboard.py` renders `templates/dashboard.html` from a
private JSON config. Never commit generated HTML containing capability links. Browser buttons
copy/download launchers; they must not imply they can execute shell commands directly.

Start-page configuration examples: `deploy/dashboard.example.json` and
`deploy/start-page.Caddyfile.example`. Keep all reusable media implementation in this repository;
VPS Workspaces remains responsible only for the linked workspace and shared backup infrastructure.
