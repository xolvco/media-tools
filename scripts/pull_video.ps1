<#
.SYNOPSIS
    Download a video using mediatools.

.DESCRIPTION
    Downloads a video from YouTube, Vimeo, or any yt-dlp supported site.
    Saves the video and a .credits.json sidecar to the output folder.
    Prints the path to the downloaded file so it can be chained into workflows.

.PARAMETER Url
    The video URL to download (required).

.PARAMETER OutputDir
    Destination folder. Defaults to the user's Downloads folder.

.PARAMETER Filename
    Output filename without extension. Defaults to the video title.

.PARAMETER Quality
    yt-dlp format selector. Default: bestvideo+bestaudio/best
    Examples:
      "bestaudio/best"                      # audio only
      "bestvideo[height<=1080]+bestaudio"   # max 1080p

.PARAMETER Cookies
    Path to a Netscape-format cookies.txt file.

.PARAMETER CookiesFromBrowser
    Browser to extract cookies from automatically.
    Supported: chrome, firefox, edge, safari

.EXAMPLE
    .\scripts\pull_video.ps1 -Url "https://youtube.com/watch?v=dQw4w9WgXcQ"

.EXAMPLE
    .\scripts\pull_video.ps1 -Url "https://youtube.com/watch?v=..." `
        -OutputDir "$HOME\Videos\research" `
        -CookiesFromBrowser chrome

.EXAMPLE
    # Chain: download then extract audio
    $video = .\scripts\pull_video.ps1 -Url "https://youtube.com/watch?v=..."
    .\scripts\extract_audio.ps1 -InputFile $video

.NOTES
    Requires: mediatools installed (pip install mediatools[download])
    Requires: ffmpeg on PATH
#>

param(
    [Parameter(Mandatory = $true)]
    [string]$Url,

    [string]$OutputDir = "",
    [string]$Filename = "",
    [string]$Quality = "",
    [string]$Cookies = "",
    [string]$CookiesFromBrowser = ""
)

$ErrorActionPreference = "Stop"

# ── build argument list ───────────────────────────────────────────────────────
$args_list = @("pull-video", $Url)

if ($OutputDir)           { $args_list += @("--output-dir", $OutputDir) }
if ($Filename)            { $args_list += @("--filename", $Filename) }
if ($Quality)             { $args_list += @("--quality", $Quality) }
if ($Cookies)             { $args_list += @("--cookies", $Cookies) }
if ($CookiesFromBrowser)  { $args_list += @("--cookies-from-browser", $CookiesFromBrowser) }

# ── run ───────────────────────────────────────────────────────────────────────
Write-Host "Downloading: $Url" -ForegroundColor Cyan

try {
    $output = & mediatools @args_list 2>&1
} catch {
    Write-Error "mediatools not found. Install with: pip install 'mediatools[download]'"
    exit 1
}

if ($LASTEXITCODE -ne 0) {
    Write-Error "Download failed:`n$output"
    exit 1
}

# Parse path from JSON output
try {
    $result = $output | ConvertFrom-Json
    $saved_path = $result.path
} catch {
    Write-Error "Could not parse JSON output:`n$output"
    exit 1
}

if (-not $saved_path) {
    Write-Error "Download completed but path not found in output.`n$output"
    exit 1
}

Write-Host "Saved: $saved_path" -ForegroundColor Green

# Return the path — can be captured by the caller for chaining
Write-Output $saved_path
