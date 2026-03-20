# Shell Scripts

Ready-made scripts for users who prefer the terminal over writing Python.
Each script wraps the `mediatools` CLI, accepts the same parameters, and prints
the output file path so scripts can be chained together.

Scripts live in the `scripts/` folder of the repo.

---

## pull_video

Downloads a video from any supported URL.

=== "Bash"

    **Script:** `scripts/pull_video.sh`

    ```bash
    # Basic download — saves to ~/Downloads
    ./scripts/pull_video.sh "https://youtube.com/watch?v=dQw4w9WgXcQ"

    # Custom output folder
    ./scripts/pull_video.sh "https://youtube.com/watch?v=dQw4w9WgXcQ" \
      --output-dir ~/Videos/research

    # Custom filename
    ./scripts/pull_video.sh "https://youtube.com/watch?v=dQw4w9WgXcQ" \
      --output-dir ~/Videos \
      --filename "rick-astley"

    # Audio only
    ./scripts/pull_video.sh "https://youtube.com/watch?v=dQw4w9WgXcQ" \
      --quality "bestaudio/best"

    # Max 1080p
    ./scripts/pull_video.sh "https://youtube.com/watch?v=dQw4w9WgXcQ" \
      --quality "bestvideo[height<=1080]+bestaudio/best"

    # With browser cookies (recommended for YouTube)
    ./scripts/pull_video.sh "https://youtube.com/watch?v=dQw4w9WgXcQ" \
      --cookies-from-browser chrome

    # With cookies file
    ./scripts/pull_video.sh "https://youtube.com/watch?v=dQw4w9WgXcQ" \
      --cookies ~/youtube-cookies.txt
    ```

    **Parameters:**

    | Parameter | Description |
    | --- | --- |
    | `<url>` | Video URL (required, first positional argument) |
    | `--output-dir <dir>` | Destination folder (default: `~/Downloads`) |
    | `--filename <name>` | Output filename without extension |
    | `--quality <fmt>` | yt-dlp format selector |
    | `--cookies <file>` | Path to Netscape cookies.txt |
    | `--cookies-from-browser <name>` | Browser: `chrome`, `firefox`, `edge`, `safari` |

=== "PowerShell"

    **Script:** `scripts/pull_video.ps1`

    ```powershell
    # Basic download — saves to ~/Downloads
    .\scripts\pull_video.ps1 -Url "https://youtube.com/watch?v=dQw4w9WgXcQ"

    # Custom output folder
    .\scripts\pull_video.ps1 -Url "https://youtube.com/watch?v=dQw4w9WgXcQ" `
      -OutputDir "$HOME\Videos\research"

    # Custom filename
    .\scripts\pull_video.ps1 -Url "https://youtube.com/watch?v=dQw4w9WgXcQ" `
      -OutputDir "$HOME\Videos" `
      -Filename "rick-astley"

    # Audio only
    .\scripts\pull_video.ps1 -Url "https://youtube.com/watch?v=dQw4w9WgXcQ" `
      -Quality "bestaudio/best"

    # Max 1080p
    .\scripts\pull_video.ps1 -Url "https://youtube.com/watch?v=dQw4w9WgXcQ" `
      -Quality "bestvideo[height<=1080]+bestaudio/best"

    # With browser cookies (recommended for YouTube)
    .\scripts\pull_video.ps1 -Url "https://youtube.com/watch?v=dQw4w9WgXcQ" `
      -CookiesFromBrowser chrome

    # With cookies file
    .\scripts\pull_video.ps1 -Url "https://youtube.com/watch?v=dQw4w9WgXcQ" `
      -Cookies "$HOME\youtube-cookies.txt"
    ```

    **Parameters:**

    | Parameter | Description |
    | --- | --- |
    | `-Url` | Video URL (required) |
    | `-OutputDir` | Destination folder (default: `~/Downloads`) |
    | `-Filename` | Output filename without extension |
    | `-Quality` | yt-dlp format selector |
    | `-Cookies` | Path to Netscape cookies.txt |
    | `-CookiesFromBrowser` | Browser: `chrome`, `firefox`, `edge`, `safari` |

---

## Output and chaining

Each script prints two things:

- **stderr** — status messages (`Downloading: ...`, `Saved: ...`)
- **stdout** — the path to the downloaded file

This separation lets you capture the output path for the next step in a workflow:

=== "Bash"

    ```bash
    # Capture the path
    VIDEO=$(./scripts/pull_video.sh "$URL" --cookies-from-browser chrome)

    # Use it in the next step
    echo "Downloaded to: $VIDEO"
    ```

=== "PowerShell"

    ```powershell
    # Capture the path
    $video = .\scripts\pull_video.ps1 -Url $url -CookiesFromBrowser chrome

    # Use it in the next step
    Write-Host "Downloaded to: $video"
    ```

See [Chaining Workflows](workflows.md) for full pipeline examples.

---

## First-time setup

=== "Bash"

    Make the script executable (one time):

    ```bash
    chmod +x scripts/pull_video.sh
    ```

    Or run without making executable:

    ```bash
    bash scripts/pull_video.sh "https://youtube.com/watch?v=..."
    ```

=== "PowerShell"

    Allow local scripts to run (one time, run as Administrator):

    ```powershell
    Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
    ```
