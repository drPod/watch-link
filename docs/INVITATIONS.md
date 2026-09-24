# Invitations

Create one invitation per movie/group using `uv run python -m watch_link invite`.
The output directory must be the directory Caddy serves at the configured base URL.
Keep it outside the repository and outside source synchronization. Back it up privately.

The generated Mac command ends with `| bash`. To override a mode, change that to:

```sh
# Append to the invitation's curl command:
# | bash -s -- --sync
# | bash -s -- --solo
# | bash -s -- --install-player
# | bash -s -- --dry-run
```

Windows commands invoke a downloaded PowerShell script block. Append `-Sync`, `-Solo`,
`-InstallPlayer` or `-DryRun`. No execution-policy change is needed or performed.
`--solo` / `-Solo` overrides a shared invitation for independent playback. Use the same
invitation for both viewers; independently generated invitations have different rooms.

The default Syncplay server is `syncplay.pl:8999`. Choose another with `--server host:port`.
Syncplay coordinates playback only; Caddy serves bytes independently to every viewer.
Public Syncplay servers are external services. A random room is not an authentication
boundary; use a trusted/private Syncplay server if room metadata is sensitive.

The Mac launcher reads Syncplay's existing settings but uses `--no-store` and explicit
room/server/player arguments, so it does not overwrite a user's normal configuration.
It runs Syncplay in console mode to avoid its initial configuration dialog. Keep the
terminal open; quit Syncplay normally when finished. Each run gets a random viewer name.

## Inspect, revoke and rotate

Open the invitation's `/mac` or `/windows.ps1` URL in a browser to inspect its source.
Only invite people who trust the host to serve code. HTTPS protects transport; it does
not replace trust in the server. The short pipeline executes downloaded code locally.
For a download-first workflow, save that script, inspect it, then run it explicitly.

```sh
uv run python -m watch_link revoke TOKEN --output "$HOME/deploy/www/watch-link"
```

Revocation removes both launcher files. It **does not revoke a movie URL already received**.
The current media URL grants access under the shared Caddy path, which can include the
whole library. Rotate that path and regenerate invitations to revoke media access.
No per-viewer authorization, expiry or download prevention is claimed.

Invitation tokens use 144 bits of randomness. Scripts contain movie access links and
must never be committed, pasted into public issues or included in public CI fixtures.

## Player selection

Mac: `/Applications` and `~/Applications` IINA first, then VLC; mpv on PATH afterward.
Windows: Program Files, Program Files (x86), and user Programs VLC, then VLC/mpv on PATH.
Only supported players are selected for both solo and shared viewing. Existing players
are not upgraded or removed. A broken installation reports an error; it is not replaced
silently. Syncplay's upstream adapters handle player communication and VLC's Lua interface.

No supported player + solo: system browser. No supported player + install/shared mode:
IINA on Mac, VLC on Windows. No Homebrew: official prebuilt IINA, never a source build or
an automatic Homebrew installation. Direct Mac DMGs are checksum-checked and quarantined.
An unapproved Syncplay download may need Privacy & Security approval and a second run.

Windows auto-install requires WinGet (Microsoft App Installer). Missing WinGet results in
an actionable error rather than installing a package manager or weakening security policy.
