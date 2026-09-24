# Generated from https://github.com/drPod/watch-link. Inspect before running.
param([switch]$Sync, [switch]$Solo, [switch]$InstallPlayer, [switch]$DryRun)
$ErrorActionPreference = 'Stop'
$movie = @@MOVIE@@
$room = @@ROOM@@
$server = @@SERVER@@
$useSync = @@SYNC@@
if ($Sync) { $useSync = $true }
if ($Solo) { $useSync = $false }
if ($env:OS -ne 'Windows_NT') { throw 'Use the Mac launcher on macOS.' }

function Find-Player {
    foreach ($root in @($env:ProgramFiles, ${env:ProgramFiles(x86)}, "$env:LOCALAPPDATA\Programs")) {
        if (-not $root) { continue }
        $candidate = Join-Path $root 'VideoLAN\VLC\vlc.exe'
        if (Test-Path $candidate) { return $candidate }
    }
    foreach ($name in @('vlc.exe', 'mpv.exe')) {
        $cmd = Get-Command $name -ErrorAction SilentlyContinue
        if ($cmd) { return $cmd.Source }
    }
    return $null
}
function Find-Syncplay {
    foreach ($root in @($env:ProgramFiles, ${env:ProgramFiles(x86)}, "$env:LOCALAPPDATA\Programs")) {
        if (-not $root) { continue }
        $candidate = Join-Path $root 'Syncplay\Syncplay.exe'
        if (Test-Path $candidate) { return $candidate }
    }
    $cmd = Get-Command syncplay.exe -ErrorAction SilentlyContinue
    if ($cmd) { return $cmd.Source }
    return $null
}
function Install-PackageId([string]$Id) {
    if (-not (Get-Command winget -ErrorAction SilentlyContinue)) {
        throw 'Windows App Installer (WinGet) is required for automatic installation. Install it from Microsoft Store and rerun.'
    }
    & winget install --id $Id --exact --source winget --accept-source-agreements --accept-package-agreements
    if ($LASTEXITCODE -ne 0) { throw "Installation failed: $Id" }
}
$player = Find-Player
if ($DryRun) {
    Write-Output "Player: $player; Syncplay: $useSync; Install if missing: $($InstallPlayer -or $useSync)"
    return
}
if (-not $player -and ($InstallPlayer -or $useSync)) {
    Install-PackageId 'VideoLAN.VLC'
    $player = Find-Player
    if (-not $player) { throw 'VLC was not found after installation.' }
}
if ($useSync) {
    $syncplay = Find-Syncplay
    if (-not $syncplay) {
        Install-PackageId 'Syncplay.Syncplay'
        $syncplay = Find-Syncplay
        if (-not $syncplay) { throw 'Syncplay was not found after installation.' }
    }
    Write-Output 'Joining watch-together. Keep this terminal open; use the player to play/pause.'
    & $syncplay --no-gui --no-store --host $server --room $room --name "Viewer-$(Get-Random -Maximum 99999)" --player-path $player $movie
} elseif ($player) {
    & $player $movie
} else {
    Write-Output 'Opening your browser without installing anything. If unsupported, rerun with -InstallPlayer.'
    Start-Process $movie
}
