# Operations

## Boundaries

| Component | Owns |
|---|---|
| Watch Link Python CLI | Generating/revoking private static invitations |
| Bash / PowerShell launcher | Player detection, upstream install, launch arguments |
| Caddy | HTTPS, original-file streaming, byte ranges, static invitations |
| Syncplay | Rooms and synchronized player controls |
| Radarr / Prowlarr | Library import and searches through configured sources |
| qBittorrent / Gluetun | Torrent transfers and VPN isolation with upstream kill switch |

There is no Watch Link daemon. Regenerate invitations to deploy launcher changes; existing
scripts are immutable snapshots of the version that created them. Keep the source checkout
separate from private deployment, app configuration and invitation directories.

## Caddy invitation route

Add this inside the existing watch hostname, before its fallback handler:

```caddy
handle_path /i/* {
    root * /srv/watch-link
    header Content-Type "text/plain; charset=utf-8"
    header Cache-Control "no-store"
    file_server
}
```

Mount the host invitation directory read-only at `/srv/watch-link`. Directory browsing must
remain off (the default). Reject unknown paths using the site's existing 404 handler.
The watch site should also set `Referrer-Policy: no-referrer`. Validate the full configuration
before reload. For rootless Docker, the container owner must be able to read the private files.

## Backups and migration

Back up private Compose/environment files, Caddy routes, invitations and application state.
Use Radarr/Prowlarr native backups or SQLite online backup for live databases. rsnapshot provides
retention and an SSH pull can keep a second unencrypted copy on the Mac. Plain rsync of a live
SQLite database is not a guaranteed consistent snapshot. Restore with services stopped.

The original deployment uses VPS Workspaces' existing rsnapshot jobs on both machines;
it is an optional integration, not a prerequisite. Keep `/srv/media` outside source sync and
configuration snapshots to avoid duplicating movie storage. Mac source files are preserved.

When moving an existing torrent, preserve its .torrent file and directory naming, add it
paused to qBittorrent, force a piece check, then resume. Compare full source/destination hashes
before declaring a migration complete. Keep torrent and Radarr library on one filesystem so
imports can be hardlinks. Revoke old invitations and rotate old stream URLs after migration.

## Troubleshooting

- Browser fails: check codecs; use install-player to get a desktop player, not automatic transcoding.
- Playback doesn't sync: both participants must use shared mode and the same room/server/movie.
- Syncplay won't start on Mac: approve the official app in Privacy & Security and rerun.
- Windows install fails: verify App Installer/WinGet and the official package identifiers.
- Streaming stalls: compare server-to-viewer bandwidth, not viewer upload speed. Check range206
  and actual seeking. Syncplay doesn't relay video or compensate for insufficient bandwidth.
- Torrent stopped: inspect Gluetun health first. Never temporarily bypass the VPN to fix downloads.
- Invitations are missing after restore: restore the private output directory, not only this repo.

## Updates and rollback

Image digests and direct Mac installer checksums are pinned. Update from upstream releases,
verify checksums and rerun checks before issuing new invitations. Homebrew/WinGet resolve their
current curated packages. Keep previous Caddy configuration and invitation directory snapshots.
Reverting source does not change already-issued launchers. Restore their snapshot or issue new ones.

## Optional password-free dashboard links

`deploy/dashboard-access.Caddyfile.example` uses only native Caddy path, cookie and
Origin matchers. Replace all secret placeholders with one cryptographically random token
(at least 32 random bytes) per hostname. The private `/access/TOKEN` link sets a Secure,
HttpOnly, host-only, SameSite=Lax cookie and redirects to `/`. Cookies last 30 days;
bookmark links remain valid until rotated. No directory or certificate record reveals
the token, but anyone receiving the link has dashboard administrator access.

Radarr can retain External authentication behind this gate. To apply the same pattern to
qBittorrent, use its hostname, a different token and upstream `gluetun:8080`. Preserve the
public Host/Origin headers. Keep CSRF enabled. qBittorrent's native **authentication subnet
whitelist** can trust only Caddy's exact transport IP (/32), with reverse-proxy IP handling
disabled; otherwise the forwarded viewer IP can defeat that matching. Keep native credentials
for Radarr and direct access. Never whitelist a whole subnet or publish the backend publicly.
A changed Caddy container IP requires an explicit whitelist update. Trust the Docker network.

Back up the proxy config and qBittorrent preferences before changing authentication. Validate
and reload Caddy's gate before enabling the proxy-only native-login bypass. Verify anonymous,
wrong-token and cross-origin requests fail; the private link reaches both UI and API; direct
unauthenticated qBittorrent API access fails; and Radarr's download-client test still passes.

Store actual links in `~/deploy/media-stack/PRIVATE-LINKS.md` and `dashboard-links.json`, mode600.
An optional Mac copy lives in `~/Movies/VPS-Media/PRIVATE-LINKS.md`. The private operations
runbook points there. Keep secrets out of this repository. Rotate both the entry path and
cookie comparison to invalidate a dashboard link and its existing browser cookies.

## Private start page

`python -m watch_link.dashboard --config /PRIVATE/dashboard.json --output /PRIVATE/TOKEN/index.html`
creates a static HTML page from `deploy/dashboard.example.json`'s shape. It lists service links
and existing movie invitations, with Mac/Windows and solo/together choices. Copy/download uses
the existing launchers; a browser cannot directly execute shell commands. For a manual page, add invitations to the private config and regenerate. For automatic movie
updates, use the library timer below. No application server is needed.

Use `deploy/start-page.Caddyfile.example` inside the existing watch site, preserving its media
streaming route. Mount the private output root read-only at `/srv/watch-link`. Generate the page
under the same random token used in the route.

Serve the page through an exact, random-token Caddy path, with HTML content type, no-store and
no-referrer headers. If it lives under the invitation file-server root, its directory name must
also be secret; never store it at a guessable `dashboard.html` there. Keep the generated page and
config outside Git. A personal page containing workspace and management links grants that access;
share individual movie invitation commands with viewers. Rotate the page token if disclosed.


## Automatic available movies

`watch_link.library` queries Jellyfin's native movie inventory, verifies each file exists under
its configured host movie root, and updates the page with solo/together invitations. It does not
scan download queues or label incomplete downloads as available. Jellyfin must discover a newly
imported movie first. If the API fails, the last successful page remains intact.

Copy `deploy/library.example.json` to a private location and fill in paths. `auth_file` contains
`{"token":"JELLYFIN_API_TOKEN"}`; use a native Jellyfin API token and keep it private. The
Jellyfin container path and host path may differ. `media_base` must serve the movie root through
Caddy. The state file preserves invitation URLs and Syncplay rooms across refreshes; preserve
it during migration. Removing a file removes its page entry but does not revoke previously
shared invitations. Files or renamed paths added later get new invitations.

Run `uv run python -m watch_link.library --config /PRIVATE/library.json`. Install/adapt
`deploy/systemd/watch-link-library.service` and `.timer`, then enable the timer. The original
installation runs every minute with a 128 MiB cap. The open start page checks for updated movie
entries every 30 seconds while visible, keeping the selected OS and existing playback choices.
Writes are atomic and overlapping refreshes are locked. The movie list in dashboard.json is
managed by this job; edit service links there, not the generated movie entries.

Back up the private configuration, state, invitations and generated page. No movie files are
copied by this job. The timer executes the source checkout, so pull/sync source changes and
refresh its uv environment before using new dependencies.

## Indexer coverage

Manage sources in Prowlarr using its built-in definitions and Test action, then use Sync App
Indexers to publish them to Radarr. Keep the chosen sync profile: adding sources need not
turn on automatic downloads. Test both the source and downstream application; a general
search can pass while a movie-category request fails. Disable unreliable sources rather
than forcing them through validation. Private sources require an existing membership.

General-purpose sources may classify everything as Other (8000). Include that category
in the Radarr application's Prowlarr sync categories when using those sources. Radarr
still matches search results to movies. Anime/TV sources without suitable movie results
can remain searchable in Prowlarr without appearing in Radarr.

Indexer counts and reported seed counts are not additive. Identical info hashes identify
the same torrent swarm; multiple trackers and DHT can discover overlapping peers for it.
Different releases cannot pool pieces just because their movie title matches. qBittorrent
handles peer discovery; this project does not merge magnets or implement a tracker.
