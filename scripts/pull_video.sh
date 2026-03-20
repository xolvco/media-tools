#!/usr/bin/env bash
# pull_video.sh — download a video using mediatools
#
# Usage:
#   ./scripts/pull_video.sh <url> [options]
#
# Options:
#   --output-dir <dir>            Destination folder (default: ~/Downloads)
#   --filename <name>             Output filename without extension
#   --quality <fmt>               yt-dlp format selector (default: bestvideo+bestaudio/best)
#   --cookies <file>              Path to Netscape-format cookies.txt
#   --cookies-from-browser <name> Browser to read cookies from (chrome, firefox, edge, safari)
#
# Output:
#   Prints the path to the downloaded file on stdout.
#   Prints status messages on stderr.
#   Exits 0 on success, 1 on error.
#
# Chaining:
#   VIDEO=$(./scripts/pull_video.sh "$URL" --cookies-from-browser chrome) && \
#   ./scripts/extract_audio.sh "$VIDEO"

set -euo pipefail

# ── argument parsing ────────────────────────────────────────────────────────
URL=""
OUTPUT_DIR=""
FILENAME=""
QUALITY=""
COOKIES=""
COOKIES_FROM_BROWSER=""

if [[ $# -eq 0 ]]; then
    echo "Usage: pull_video.sh <url> [options]" >&2
    echo "Run with --help for full usage." >&2
    exit 1
fi

URL="$1"
shift

while [[ $# -gt 0 ]]; do
    case "$1" in
        --output-dir)       OUTPUT_DIR="$2";           shift 2 ;;
        --filename)         FILENAME="$2";             shift 2 ;;
        --quality)          QUALITY="$2";              shift 2 ;;
        --cookies)          COOKIES="$2";              shift 2 ;;
        --cookies-from-browser) COOKIES_FROM_BROWSER="$2"; shift 2 ;;
        --help|-h)
            sed -n '2,20p' "$0" | sed 's/^# \?//'
            exit 0
            ;;
        *)
            echo "Unknown option: $1" >&2
            exit 1
            ;;
    esac
done

# ── build mediatools command ─────────────────────────────────────────────────
CMD=(mediatools pull-video "$URL")

[[ -n "$OUTPUT_DIR" ]]           && CMD+=(--output-dir "$OUTPUT_DIR")
[[ -n "$FILENAME" ]]             && CMD+=(--filename "$FILENAME")
[[ -n "$QUALITY" ]]              && CMD+=(--quality "$QUALITY")
[[ -n "$COOKIES" ]]              && CMD+=(--cookies "$COOKIES")
[[ -n "$COOKIES_FROM_BROWSER" ]] && CMD+=(--cookies-from-browser "$COOKIES_FROM_BROWSER")

# ── run ──────────────────────────────────────────────────────────────────────
echo "Downloading: $URL" >&2
JSON=$("${CMD[@]}" 2>&1)
EXIT_CODE=$?

if [[ $EXIT_CODE -ne 0 ]]; then
    echo "Error: $JSON" >&2
    exit 1
fi

# Parse path from JSON output — use jq if available, else Python
if command -v jq &>/dev/null; then
    SAVED_PATH=$(echo "$JSON" | jq -r '.path')
else
    SAVED_PATH=$(echo "$JSON" | python3 -c "import sys,json; print(json.load(sys.stdin)['path'])")
fi

if [[ -z "$SAVED_PATH" || "$SAVED_PATH" == "null" ]]; then
    echo "Download completed but could not parse output path." >&2
    echo "$JSON" >&2
    exit 1
fi

echo "Saved: $SAVED_PATH" >&2

# Print the path to stdout for chaining
echo "$SAVED_PATH"
