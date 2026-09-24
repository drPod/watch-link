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

Jellyfin's native M3U tuner reads the maintained worldwide playlist directly from
`https://iptv-org.github.io/iptv/index.m3u`. Its guide refresh reloads the source without a
custom playlist updater. At expansion on September 24 it contained 10,909 stream entries.
These are not 10,909 verified, distinct channels: alternative feeds, regional restrictions,
offline sources and incompatible codecs occur. Use Jellyfin search and favorites to find and
keep useful channels. Importing a listing does not download or play every stream.

The original 14-channel test playlist remains in `iptv/channels.m3u` as a rollback option;
`iptv/channels.json` describes only that test selection, not the full catalogue. The private
pre-expansion configuration backup is recorded in the deployment runbook.

An M3U playlist does not supply a TV schedule. The filtered XMLTV provider at `/iptv/guide.xml`
still covers only the selected guide IDs; the full catalogue does not have full guide coverage.
Channel IDs must match exactly. Channels without listings remain accessible from Channels/search.

Programme data currently comes from the community feed `https://iptv-epg.org/files/epg-us.xml.gz`.
The initial selection had 11 matching channel IDs. Channels without guide data remain playable.
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
03:30 UTC. Failed refreshes preserve the previous complete guide. This timer updates schedules. Jellyfin independently reloads the upstream playlist during its
native guide refresh; neither refresh proves every source can play.

## Large catalogues and browser layout

Jellyfin 12.1.0's modern channel-list request omits `limit` in this deployment. Rendering the
worldwide catalogue exhausted a headless browser's 768 MiB cap. Jellyfin itself did not restart.
The built-in **Desktop (Legacy)** layout requests 100 channels per page and passed the same test.
Choose it under user Settings → Display → Layout before opening the full Channels list. This
is a per-browser preference; changing server display preferences does not force it on every device.
Keep Library page size at 100 or lower; zero disables pagination. The modern view did not honor
that setting in the observed request. Search/favorites avoid paging through the whole catalogue.

No browser bundle is patched. The upstream legacy layout is the current workaround; do not call
the default modern view safe for this catalogue. Related upstream report:
https://github.com/jellyfin/jellyfin-web/issues/7603 (guide performance, not the identical channel-view bug).

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
