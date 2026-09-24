# Upstream projects

Watch Link is MIT-licensed integration code. External applications retain their own licenses.
No player, Syncplay source, or installer binary is vendored here.

| Project | Reused interface |
|---|---|
| [IINA](https://github.com/iina/iina) | Official DMG, Homebrew cask, app launch and iina-cli |
| [VLC](https://www.videolan.org/vlc/) | Installed player and WinGet package |
| [mpv](https://mpv.io/) | Existing executable |
| [Syncplay](https://github.com/Syncplay/syncplay) | Official installers, CLI and upstream player adapters |
| [Caddy](https://caddyserver.com/docs/) | HTTPS reverse proxy and file server |
| [Gluetun](https://github.com/qdm12/gluetun) | VPN container, health checks and firewall |
| [qBittorrent](https://www.qbittorrent.org/) | Torrent client and native Web API |
| [Radarr](https://radarr.video/) / [Prowlarr](https://prowlarr.com/) | Existing apps and native APIs |
| [LinuxServer](https://docs.linuxserver.io/) | Radarr/Prowlarr/qBittorrent container images |
| [Homebrew](https://brew.sh/) / [WinGet](https://github.com/microsoft/winget-cli) | Existing package installation |
| [rsnapshot](https://rsnapshot.org/) | Optional backup retention |

Server templates originated in [drPod/vps-workspaces](https://github.com/drPod/vps-workspaces),
MIT, copyright 2026 Darsh Poddar. That project's cmux PR references belong to workspace
integration; this media launcher doesn't integrate cmux or claim those changes as its own.
