# Browser movies and live TV

Jellyfin is the existing interface for movies, channels, search, favorites and programme guides.
Radarr/qBittorrent still manage downloads; Watch Link still provides native-player invitations.
The movie mount is read-only and shares existing files, with no second library copy.

## Deploy

Copy `deploy/compose.jellyfin.yml` beside the private media Compose file, create
`config/jellyfin`, `cache/jellyfin` and `iptv`, then run:

```sh
MEDIA_ROOT=/srv/media docker compose -f compose.yml -f compose.jellyfin.yml up -d jellyfin
```

This rootless Docker example limits Jellyfin to 1 GiB RAM and 1.5 CPUs. Configure it over
localhost:18096 before exposing it. Finish the native setup wizard, create an administrator,
and add a Movies library at `/media/movies`. Disable trickplay/chapter image extraction to
avoid background processing. Native real-time monitoring discovers imported movies.

Use Caddy to proxy a separate hostname to `media-stack-jellyfin-1:8096`. The private cookie
route in `dashboard-access.Caddyfile.example` can protect the whole hostname, including its
WebSocket and streaming routes. Validate both redirects and nonempty page assets. Keep the
backend bound to loopback. Native apps that cannot supply this cookie need a different
access arrangement; this route is intended for browsers.

In the original deployment, select the **Watch** user (no password) after opening the private
link; if the sign-in form appears, leave its password empty and click **Sign In**. This viewer cannot administer the server or delete media. The admin user retains a
password. A passwordless viewer must never be exposed outside the private-link gate.

For both users, disable audio/video transcoding and permit remuxing (container changes with
no codec re-encoding). Supported streams retain their original quality. An incompatible
browser/audio codec can fail instead of being converted. Use a native player for those files.

## Channel sources

Jellyfin's native M3U tuner reads `/iptv/channels.m3u`. An M3U file supplies addresses and
channel IDs; it does not include a TV schedule. Add the filtered XMLTV guide at `/iptv/guide.xml`
as a native XMLTV listings provider and match channel IDs exactly.

The initial deployment has 14 streams selected from iptv-org's sports/news/movie playlists:
ACC Digital Network, beIN SPORTS XTRA, FloHockey, FloRacing, FUEL TV US, Pac-12 Insider,
RACER International, SportsGrid, World of Freesports, CBS News Bay Area, DW English,
France 24 English, LiveNOW from FOX and MovieSphere. These are a starting selection, not a
complete channel catalogue or a promise of particular live sporting events. Addresses and
regional availability can change. The original deployment's metadata is in `iptv/channels.json`.

Programme data currently comes from the community feed `https://iptv-epg.org/files/epg-us.xml.gz`.
Only 11 selected channel IDs have matching listings. Channels without guide data remain playable.
The feed is large: do not load it into a Python tree or hand its entire contents to Jellyfin.
The standard XMLTV `tv_grep` utility was tried, but this feed's element ordering produced parser
warnings and lost fields. The small `watch_link.guide` adapter instead uses defusedxml's
streaming parser, keeps only selected top-level elements and atomically replaces the guide.
It does not scrape broadcasters or implement a guide/player UI.

```sh
uv run python -m watch_link.guide \
  --url https://iptv-epg.org/files/epg-us.xml.gz \
  --channels /PRIVATE/iptv/guide-channels.txt \
  --output /PRIVATE/iptv/guide.xml
```

`guide-channels.txt` is one XMLTV channel ID per line. Copy/adapt the three units in
`deploy/systemd/` to `~/.config/systemd/user`, then enable `watch-link-guide.timer`.
They cap the refresh at 256 MiB, one CPU and ten minutes, under an aggregate job slice.
The timer downloads daily at 03:00 UTC; configure Jellyfin's native Refresh Guide task for
03:30 UTC. Failed refreshes preserve the previous complete guide. M3U stream addresses are
currently curated manually; this timer updates schedules, not broken channel URLs.

## Verify and maintain

Check `/System/Info/Public`, library items, Live TV channels and current programmes using the
native API. Jellyfin 12 uses `Authorization: MediaBrowser Token="..."`; do not assume legacy
X-Emby-Token headers work. Keep API credentials and private links outside Git.

Test a real stream's media segments, not just the master playlist, and test the viewer's
PlaybackInfo response. A responsive manifest alone does not guarantee successful playback.
Check the selected movie is direct-playable and no video encoder is running during viewing.

Back up private proxy rules, application config/database, playlist, selected guide IDs and
refresh units on both machines. Exclude `cache/jellyfin` and temporary full guides. The existing
VPS Workspaces SQLite/rsnapshot jobs cover private deployment state; movie bytes stay excluded.
Stop only the Jellyfin service to restore its config. Keep rollback copies of proxy rules.

Sources: [Jellyfin containers](https://jellyfin.org/docs/general/installation/container/),
[Live TV setup](https://jellyfin.org/docs/general/server/live-tv/setup-guide/),
[iptv-org](https://github.com/iptv-org/iptv), [guide feed](https://iptv-epg.org/guides).
