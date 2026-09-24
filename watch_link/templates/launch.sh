#!/bin/bash
# Generated from https://github.com/drPod/watch-link. Inspect before running.
watch_main() (
    set -euo pipefail
    umask 077
    movie=@@MOVIE@@
    room=@@ROOM@@
    server=@@SERVER@@
    sync=@@SYNC@@
    install_player=0
    dry_run=0
    for arg in "$@"; do
        case "$arg" in
            --sync) sync=1 ;;
            --solo) sync=0 ;;
            --install-player) install_player=1 ;;
            --dry-run) dry_run=1 ;;
            *) printf 'Unknown option: %s\n' "$arg" >&2; exit 2 ;;
        esac
    done
    if [[ $(uname -s) != Darwin ]]; then
        echo 'This launcher is for macOS. On Windows use the Windows PowerShell command.' >&2
        exit 1
    fi
    export PATH="/opt/homebrew/bin:/usr/local/bin:$PATH"
    player=''
    for root in /Applications "$HOME/Applications"; do
        if [[ -x "$root/IINA.app/Contents/MacOS/iina-cli" ]]; then
            player="$root/IINA.app/Contents/MacOS/iina-cli"; break
        fi
    done
    if [[ -z "$player" ]]; then
        for root in /Applications "$HOME/Applications"; do
            if [[ -x "$root/VLC.app/Contents/MacOS/VLC" ]]; then
                player="$root/VLC.app/Contents/MacOS/VLC"; break
            fi
        done
    fi
    if [[ -z "$player" ]]; then player=$(command -v mpv || true); fi
    if ((dry_run)); then
        printf 'Player: %s\nSyncplay: %s\nInstall if missing: %s\n' "${player:-browser (solo only)}" "$sync" "$((install_player || sync))"
        exit 0
    fi
    tmp=$(mktemp -d)
    mounted=0
    # shellcheck disable=SC2329
    cleanup() {
        if ((mounted)); then hdiutil detach "$tmp/mount" -quiet || true; fi
        rm -rf "$tmp"
    }
    trap cleanup EXIT
    install_dmg() {
        local name=$1 url=$2 checksum=$3
        echo "Downloading $name from its official release…"
        curl --fail --location --proto '=https' --tlsv1.2 --retry 2 "$url" -o "$tmp/app.dmg"
        printf '%s  %s\n' "$checksum" "$tmp/app.dmg" | shasum -a 256 -c -
        mkdir -p "$tmp/mount" "$HOME/Applications"
        hdiutil attach "$tmp/app.dmg" -readonly -nobrowse -mountpoint "$tmp/mount" -quiet
        mounted=1
        if [[ -e "$HOME/Applications/$name.app" ]]; then
            echo "Existing $name app could not be used. Please repair it before rerunning." >&2; exit 1
        fi
        ditto "$tmp/mount/$name.app" "$HOME/Applications/$name.app"
        xattr -w com.apple.quarantine "0083;$(printf '%x' "$(date +%s)");Watch Link;" "$HOME/Applications/$name.app"
        hdiutil detach "$tmp/mount" -quiet
        mounted=0
        if ! spctl --assess --type execute "$HOME/Applications/$name.app"; then
            open "$HOME/Applications/$name.app" || true
            echo "macOS needs your approval for $name. Approve it in Privacy & Security, open it once, then rerun this invitation."
            exit 1
        fi
    }
    if [[ -z "$player" ]] && ((install_player || sync)); then
        if command -v brew >/dev/null; then
            brew install --cask --appdir="$HOME/Applications" iina </dev/tty
            player="$HOME/Applications/IINA.app/Contents/MacOS/iina-cli"
        else
            install_dmg IINA 'https://dl.iina.io/IINA.v1.4.4.dmg' 'dd0fc0bd4b37fb57a1c8d30d6e3201b3a64bafd29959fe56953964613237beb1'
            player="$HOME/Applications/IINA.app/Contents/MacOS/iina-cli"
        fi
        [[ -x "$player" ]] || { echo 'IINA installation did not yield a usable player.' >&2; exit 1; }
    fi
    if ((sync)); then
        syncplay=''
        for root in /Applications "$HOME/Applications"; do
            if [[ -x "$root/Syncplay.app/Contents/MacOS/Syncplay" ]]; then
                syncplay="$root/Syncplay.app/Contents/MacOS/Syncplay"; break
            fi
        done
        if [[ -z "$syncplay" ]]; then
            install_dmg Syncplay 'https://github.com/Syncplay/syncplay/releases/download/v1.7.6/Syncplay_1.7.6.dmg' 'b027d9ba402953db9fe66f2d3770d16e500f1f6ac7e5a5a6e9552310fe9febb7'
            syncplay="$HOME/Applications/Syncplay.app/Contents/MacOS/Syncplay"
        fi
        echo 'Joining watch-together. Keep this terminal open; use the player to play/pause.'
        "$syncplay" --no-gui --no-store --host "$server" --room "$room" \
            --name "Viewer-$RANDOM" --player-path "$player" "$movie" </dev/tty
    elif [[ -n "$player" ]]; then
        case "$player" in
            */IINA.app/*) open -a "${player%/Contents/MacOS/iina-cli}" "$movie" ;;
            */VLC.app/*) open -a "${player%/Contents/MacOS/VLC}" "$movie" ;;
            *) "$player" "$movie" </dev/tty ;;
        esac
    else
        echo 'No supported player installed. Opening your browser without installing anything.'
        echo 'If the browser cannot play this format, rerun with --install-player.'
        open "$movie"
    fi
)
watch_main "$@"
