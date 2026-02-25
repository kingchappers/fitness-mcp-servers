#!/usr/bin/env python3
"""One-time MyFitnessPal authentication via browser.

Opens a Chromium window. Log in to MyFitnessPal, then press Enter.
Saves cookies to the path set by MFP_COOKIE_PATH (default: ~/.mfp/cookies.txt).
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

MFP_URL = "https://www.myfitnesspal.com/account/login"
DEFAULT_COOKIE_PATH = Path.home() / ".mfp" / "cookies.txt"


def main() -> None:
    cookie_path = Path(os.environ.get("MFP_COOKIE_PATH", str(DEFAULT_COOKIE_PATH)))

    print("MyFitnessPal — one-time login")
    print(f"Cookies will be saved to: {cookie_path}")
    print()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        page.goto(MFP_URL)

        print("A browser window has opened.")
        print("Log in to MyFitnessPal, then press Enter here to save your cookies.")
        input()

        pw_cookies = context.cookies()
        browser.close()

    if not pw_cookies:
        print("No cookies captured. Did you log in?", file=sys.stderr)
        sys.exit(1)

    cookie_path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    _write_netscape_cookies(pw_cookies, cookie_path)
    cookie_path.chmod(0o600)

    print(f"\nCookies saved to {cookie_path}")
    print("Set MFP_COOKIE_PATH to this path and run the MCP server.")


def _write_netscape_cookies(cookies: list[dict], path: Path) -> None:
    """Write Playwright cookies to Netscape format (readable by MozillaCookieJar)."""
    lines = ["# Netscape HTTP Cookie File\n"]
    for c in cookies:
        domain = c.get("domain", "")
        flag = "TRUE" if domain.startswith(".") else "FALSE"
        path_val = c.get("path", "/")
        secure = "TRUE" if c.get("secure", False) else "FALSE"
        expires = int(c.get("expires", 0))
        if expires < 0:
            expires = 2147483647  # session cookies: use far-future expiry
        name = c.get("name", "")
        value = c.get("value", "")
        lines.append(f"{domain}\t{flag}\t{path_val}\t{secure}\t{expires}\t{name}\t{value}\n")
    path.write_text("".join(lines))


if __name__ == "__main__":
    main()
