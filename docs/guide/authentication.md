# YouTube Authentication

YouTube requires authentication for:

- Age-restricted videos
- Members-only content
- Private videos you own
- Videos that serve ads in ways that block unauthenticated downloaders

The recommended approach is **cookies from your browser** — no password needed, works as long as you are logged in to YouTube in your browser.

---

## Method 1 — Cookies from browser (recommended)

yt-dlp reads your session cookies directly from an installed browser. No export step required.

=== "CLI"

    ```bash
    # Chrome
    mediatools pull-video "https://youtube.com/watch?v=..." \
      --cookies-from-browser chrome

    # Firefox
    mediatools pull-video "https://youtube.com/watch?v=..." \
      --cookies-from-browser firefox

    # Edge
    mediatools pull-video "https://youtube.com/watch?v=..." \
      --cookies-from-browser edge

    # Safari (macOS only)
    mediatools pull-video "https://youtube.com/watch?v=..." \
      --cookies-from-browser safari
    ```

=== "Python"

    ```python
    from mediatools import pull_video

    path = pull_video(
        "https://youtube.com/watch?v=...",
        cookies_from_browser="chrome",   # or "firefox", "edge", "safari"
    )
    ```

=== "Bash script"

    ```bash
    ./scripts/pull_video.sh "https://youtube.com/watch?v=..." \
      --cookies-from-browser chrome
    ```

=== "PowerShell script"

    ```powershell
    .\scripts\pull_video.ps1 -Url "https://youtube.com/watch?v=..." `
      -CookiesFromBrowser chrome
    ```

!!! tip "Chrome on Windows"
    Chrome may lock its cookie database while running. If you get a database error,
    close Chrome first, then run the download. You can reopen Chrome immediately after.

---

## Method 2 — Cookies file

Export your cookies to a Netscape-format `.txt` file and pass the path.

### Step 1 — Install the browser extension

Install [Get cookies.txt LOCALLY](https://chromewebstore.google.com/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc) (Chrome/Edge) or [cookies.txt](https://addons.mozilla.org/en-US/firefox/addon/cookies-txt/) (Firefox).

### Step 2 — Export cookies for youtube.com

1. Log in to YouTube in your browser
2. Click the extension icon
3. Select `youtube.com`
4. Save as `youtube-cookies.txt`

### Step 3 — Pass the file

=== "CLI"

    ```bash
    mediatools pull-video "https://youtube.com/watch?v=..." \
      --cookies ~/youtube-cookies.txt
    ```

=== "Python"

    ```python
    path = pull_video(
        "https://youtube.com/watch?v=...",
        cookies="~/youtube-cookies.txt",
    )
    ```

=== "Bash script"

    ```bash
    ./scripts/pull_video.sh "https://youtube.com/watch?v=..." \
      --cookies ~/youtube-cookies.txt
    ```

=== "PowerShell script"

    ```powershell
    .\scripts\pull_video.ps1 -Url "https://youtube.com/watch?v=..." `
      -Cookies "$HOME\youtube-cookies.txt"
    ```

!!! warning "Keep your cookies file private"
    The cookies file contains your session tokens. Treat it like a password.
    Do not commit it to git — add `*.cookies.txt` and `*-cookies.txt` to `.gitignore`.

---

## Troubleshooting

**`ERROR: Sign in to confirm you're not a bot`**
: YouTube is blocking the request. Add `--cookies-from-browser chrome` (or your browser of choice).

**`Unable to open cookie database`**
: Chrome is running and has the database locked. Close Chrome and retry.

**`This video is not available`**
: The video may be region-locked or deleted. A VPN can help with region locks.

**`Members-only content`**
: You must be a member of the channel. Log in with an account that has membership, then use cookies.
