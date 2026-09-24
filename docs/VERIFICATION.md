# Verification

## Automated

The test suite exercises URL/room validation, literal URL argument passing, private invitation
permissions, collision handling, browser fallback, dry-run/unknown flags, and Bash syntax.
Installed IINA, VLC and mpv are exercised in both solo and shared modes using isolated fixtures.
Ruff, mypy and PowerShell parsing cover project source. Windows CI runs the launcher in dry-run mode. CI does not download movies, use live
credentials or install applications on a person's device.

## Original deployment

The existing stack has verified HTTPS authentication, streaming range206, seeking/decoding,
qBittorrent VPN egress, blocked egress during a VPN stop, recovery, an official Debian test
torrent with matching checksum, and Radarr hardlink imports. One selected Mac movie was
copied/resumed and SHA256-verified, preserving the Mac original. Configuration snapshots are
stored unencrypted on the VPS and Mac. Media files are excluded from those snapshots.

The actual generated Mac launcher was tested with installed IINA and Syncplay: it joined an
isolated room over TLS and loaded a three-second test stream without a configuration dialog.
Public invitation routes returned the exact generated source, no-store headers, and 404 for
unknown tokens and directory listings. Existing media services remained healthy.

## Limits

- Fresh Mac DMG/Homebrew installs and first-use Gatekeeper approvals need a clean-device test.
- Windows native playback and WinGet installation need a real Windows test.
- Two physical devices joining an invitation must be checked before claiming end-to-end sync.
- Browser codecs, HDR, audio passthrough and available bandwidth vary by device.
- Revoking a launcher doesn't invalidate an original media URL already disclosed.
- No custom URL handler or signed installer is installed. Run the invitation command each time.

## Jellyfin and resource limits (2026-09-24)

Authenticated browser playback passed in headless Chromium: ACC Digital Network played at
1920×1080 with its clock advancing; FFmpeg copied both video and audio (remux only).
The Truman Show played at 1918×1080 with no player error. This does not certify every channel
or Safari/device codec combination. Fourteen channel manifests were available; eleven have
matching guide listings (1,461 programmes at setup).

The filtered guide refresh completed under a 256 MiB job cap with approximately 15 MiB peak
memory. A disposable 64 MiB job was killed by its own cgroup on a 128 MiB allocation while the
interactive session remained available. Limits cover explicitly scoped jobs, not all agent commands.

### Worldwide catalogue expansion

The upstream M3U had 10,909 stream entries; they have not all been playback-tested. Native
channel-name search returned matches. The default modern Channels view omitted its page limit
and exhausted the test browser cgroup. The built-in Desktop (Legacy) view requested Limit=100
and displayed the first page successfully under the same 768 MiB cap. Jellyfin stayed running
without a container restart or OOM event. The large guide refresh was still running during this
check; initial import count can include stale entries until it completes.

### Private start page

Headless Chromium verified service links, Mac/Windows solo/together command copying and script
downloads. The layout fits a 390-pixel viewport. Unknown page tokens and directory requests return
404. The workspace link is matched to the active conversation in the private workspace registry.
