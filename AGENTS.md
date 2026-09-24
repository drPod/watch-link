# Working on Watch Link

Read README.md, docs/OPERATIONS.md and docs/VERIFICATION.md first.

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
