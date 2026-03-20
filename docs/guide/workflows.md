# Chaining Workflows

Each script prints the output file path to stdout and status messages to stderr.
This lets you capture the result of one step and pass it directly to the next.

---

## How chaining works

=== "Bash"

    Use `$()` to capture output and `&&` to chain on success:

    ```bash
    # Step 1 output becomes step 2 input
    VIDEO=$(./scripts/pull_video.sh "$URL")
    AUDIO=$(./scripts/extract_audio.sh "$VIDEO")
    ```

    Or in a single pipeline:

    ```bash
    ./scripts/extract_audio.sh \
      "$(./scripts/pull_video.sh "$URL" --cookies-from-browser chrome)"
    ```

=== "PowerShell"

    Assign to variables and chain with `-ErrorAction Stop`:

    ```powershell
    $video = .\scripts\pull_video.ps1 -Url $url -CookiesFromBrowser chrome
    $audio = .\scripts\extract_audio.ps1 -InputFile $video
    ```

---

## Example workflows

### Download + extract audio

=== "Bash"

    ```bash
    URL="https://youtube.com/watch?v=dQw4w9WgXcQ"

    VIDEO=$(./scripts/pull_video.sh "$URL" --cookies-from-browser chrome)
    AUDIO=$(./scripts/extract_audio.sh "$VIDEO" --output-dir ~/Music)

    echo "Video: $VIDEO"
    echo "Audio: $AUDIO"
    ```

=== "PowerShell"

    ```powershell
    $url = "https://youtube.com/watch?v=dQw4w9WgXcQ"

    $video = .\scripts\pull_video.ps1 -Url $url -CookiesFromBrowser chrome
    $audio = .\scripts\extract_audio.ps1 -InputFile $video -OutputDir "$HOME\Music"

    Write-Host "Video: $video"
    Write-Host "Audio: $audio"
    ```

### Download + clip to a segment

=== "Bash"

    ```bash
    URL="https://youtube.com/watch?v=dQw4w9WgXcQ"

    VIDEO=$(./scripts/pull_video.sh "$URL")
    CLIP=$(./scripts/clip.sh "$VIDEO" --start-ms 30000 --end-ms 90000 \
            --output-dir ~/Videos/clips)

    echo "Clip: $CLIP"
    ```

=== "PowerShell"

    ```powershell
    $url = "https://youtube.com/watch?v=dQw4w9WgXcQ"

    $video = .\scripts\pull_video.ps1 -Url $url
    $clip  = .\scripts\clip.ps1 -InputFile $video -StartMs 30000 -EndMs 90000 `
               -OutputDir "$HOME\Videos\clips"

    Write-Host "Clip: $clip"
    ```

### Download + clip + extract audio

=== "Bash"

    ```bash
    URL="https://youtube.com/watch?v=dQw4w9WgXcQ"
    OUT=~/research/rick-astley

    VIDEO=$(./scripts/pull_video.sh "$URL" --output-dir "$OUT")
    CLIP=$(./scripts/clip.sh "$VIDEO" --start-ms 0 --end-ms 30000 --output-dir "$OUT")
    AUDIO=$(./scripts/extract_audio.sh "$CLIP" --output-dir "$OUT")

    echo "Done."
    echo "  Video:  $VIDEO"
    echo "  Clip:   $CLIP"
    echo "  Audio:  $AUDIO"
    ```

=== "PowerShell"

    ```powershell
    $url = "https://youtube.com/watch?v=dQw4w9WgXcQ"
    $out = "$HOME\research\rick-astley"

    $video = .\scripts\pull_video.ps1    -Url $url -OutputDir $out
    $clip  = .\scripts\clip.ps1          -InputFile $video -StartMs 0 -EndMs 30000 -OutputDir $out
    $audio = .\scripts\extract_audio.ps1 -InputFile $clip -OutputDir $out

    Write-Host "Done."
    Write-Host "  Video:  $video"
    Write-Host "  Clip:   $clip"
    Write-Host "  Audio:  $audio"
    ```

### Batch download from a list

=== "Bash"

    ```bash
    # urls.txt — one URL per line
    while IFS= read -r url; do
        echo "--- $url"
        ./scripts/pull_video.sh "$url" \
          --output-dir ~/Videos/batch \
          --cookies-from-browser chrome || echo "FAILED: $url"
    done < urls.txt
    ```

=== "PowerShell"

    ```powershell
    # urls.txt — one URL per line
    Get-Content urls.txt | ForEach-Object {
        $url = $_.Trim()
        if ($url -eq "") { return }
        Write-Host "--- $url"
        try {
            .\scripts\pull_video.ps1 -Url $url `
              -OutputDir "$HOME\Videos\batch" `
              -CookiesFromBrowser chrome
        } catch {
            Write-Warning "FAILED: $url"
        }
    }
    ```

---

## Error handling

Scripts exit with code `1` on failure. Use this to stop a pipeline on error:

=== "Bash"

    ```bash
    set -e   # stop on first error

    VIDEO=$(./scripts/pull_video.sh "$URL") || { echo "Download failed"; exit 1; }
    AUDIO=$(./scripts/extract_audio.sh "$VIDEO") || { echo "Audio extraction failed"; exit 1; }
    ```

=== "PowerShell"

    ```powershell
    $ErrorActionPreference = "Stop"

    $video = .\scripts\pull_video.ps1 -Url $url
    $audio = .\scripts\extract_audio.ps1 -InputFile $video
    ```

---

!!! note "Coming soon"
    `extract_audio.sh`, `clip.sh`, and their PowerShell equivalents follow the same
    pattern and will be added as those features are built out.
