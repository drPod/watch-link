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
