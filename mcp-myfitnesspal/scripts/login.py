#!/usr/bin/env python3
"""MyFitnessPal cookie-based authentication setup.

1. Opens your browser to the MFP login page.
2. Guides you to export cookies with the appropriate browser extension.
3. Watches ~/Downloads for the exported file, then installs it automatically.
"""

from __future__ import annotations

import os
import plistlib
import shutil
import sys
import time
import webbrowser
from pathlib import Path

MFP_URL = "https://www.myfitnesspal.com/account/login"

# Extension details per browser
_CHROME_EXTENSION = {
    "name": "Get cookies.txt LOCALLY",
    "url": (
        "https://chromewebstore.google.com/detail/"
        "get-cookiestxt-locally/cclelndahbckbenkjhflpdbgdldlbecc"
    ),
    "instructions": (
        "Click the extension icon, set the site to 'myfitnesspal.com',\n"
        "     then click 'Export'. Save the file to your Downloads folder."
    ),
}
_FIREFOX_EXTENSION = {
    "name": "cookies.txt",
    "url": "https://addons.mozilla.org/en-US/firefox/addon/cookies-txt/",
    "instructions": (
        "Click the extension icon, then click 'Current Site' to export\n"
        "     cookies for myfitnesspal.com. Save the file to your Downloads folder."
    ),
}

# macOS bundle IDs → extension info
_BUNDLE_EXTENSIONS: dict[str, dict[str, str]] = {
    "org.mozilla.firefox": _FIREFOX_EXTENSION,
    "org.mozilla.nightly": _FIREFOX_EXTENSION,
    "com.google.chrome": _CHROME_EXTENSION,
    "com.google.chrome.beta": _CHROME_EXTENSION,
    "com.microsoft.edgemac": _CHROME_EXTENSION,  # Chromium-based, same store
    "com.brave.browser": _CHROME_EXTENSION,
}

DEFAULT_COOKIE_PATH = Path.home() / ".mfp" / "cookies.txt"
DOWNLOADS_DIR = Path.home() / "Downloads"
POLL_INTERVAL = 1.0  # seconds
TIMEOUT = 300  # 5 minutes


def main() -> None:
    cookie_path = Path(os.environ.get("MFP_COOKIE_PATH", str(DEFAULT_COOKIE_PATH)))

    print("MyFitnessPal — cookie setup")
    print(f"Cookies will be saved to: {cookie_path}")
    print()

    extension = _BUNDLE_EXTENSIONS.get(_default_browser_bundle_id(), _CHROME_EXTENSION)

    existing = _snapshot_downloads()

    print("Opening MyFitnessPal login page in your browser...")
    webbrowser.open(MFP_URL)
    time.sleep(1)

    print()
    print("Steps:")
    print("  1. Log in to MyFitnessPal in the browser window that just opened.")
    print()
    print(f"  2. Install the '{extension['name']}' extension if needed:")
    print(f"     {extension['url']}")
    print()
    print(f"  3. {extension['instructions']}")
    print()
    print("Watching ~/Downloads for the cookie file... (Ctrl-C to cancel)")
    print()

    cookie_file = _wait_for_cookie_file(existing)
    if cookie_file is None:
        print("\nTimed out waiting for cookie file.", file=sys.stderr)
        sys.exit(1)

    print(f"\nDetected: {cookie_file.name}")
    _install_cookie_file(cookie_file, cookie_path)

    print(f"Installed to: {cookie_path}")
    print()
    print("Next — register the MCP server with Claude Code:")
    project_dir = Path(__file__).parent.parent.resolve()
    poetry_path = shutil.which("poetry") or "/opt/homebrew/bin/poetry"
    print(
        f"  claude mcp add myfitnesspal"
        f" -e MFP_COOKIE_PATH={cookie_path}"
        f" -- {poetry_path}"
        f" --directory {project_dir}"
        f" run mcp-myfitnesspal"
    )


def _default_browser_bundle_id() -> str:
    """Return the macOS bundle ID of the default HTTPS handler, or '' on failure."""
    plist_path = Path.home() / (
        "Library/Preferences/com.apple.LaunchServices/"
        "com.apple.launchservices.secure.plist"
    )
    try:
        with plist_path.open("rb") as f:
            data = plistlib.load(f)
        for handler in data.get("LSHandlers", []):
            if handler.get("LSHandlerURLScheme") == "https":
                return str(handler.get("LSHandlerRoleAll", "")).lower()
    except Exception:  # noqa: BLE001
        pass
    return ""


def _snapshot_downloads() -> set[Path]:
    if not DOWNLOADS_DIR.exists():
        return set()
    return set(DOWNLOADS_DIR.glob("*.txt"))


def _wait_for_cookie_file(existing: set[Path]) -> Path | None:
    deadline = time.monotonic() + TIMEOUT
    dots = 0
    while time.monotonic() < deadline:
        current = set(DOWNLOADS_DIR.glob("*.txt"))
        for f in current - existing:
            if _is_mfp_cookie_file(f):
                return f
        dots = (dots % 3) + 1
        print(f"\r  Waiting{'.' * dots}   ", end="", flush=True)
        time.sleep(POLL_INTERVAL)
    print()
    return None


_MAX_COOKIE_FILE_BYTES = 1024 * 1024  # 1 MB guard


def _is_mfp_cookie_file(path: Path) -> bool:
    try:
        if path.stat().st_size > _MAX_COOKIE_FILE_BYTES:
            return False
        text = path.read_text(errors="replace")
        return "# Netscape HTTP Cookie File" in text and "myfitnesspal" in text.lower()
    except OSError:
        return False


def _install_cookie_file(src: Path, dest: Path) -> None:
    dest.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    content = src.read_text()
    dest.write_text(content)
    dest.chmod(0o600)
    try:
        src.unlink()
    except OSError as e:
        print(f"Note: could not remove source file {src}: {e}", file=sys.stderr)


if __name__ == "__main__":
    main()
