#!/usr/bin/env python3
"""One-time Garmin Connect authentication.

Prompts for credentials interactively, authenticates via Garmin SSO,
and saves OAuth tokens to ~/.garminconnect. Credentials are never stored.
"""

from __future__ import annotations

import getpass
import sys
from pathlib import Path

from garminconnect import Garmin  # type: ignore[import-untyped]

TOKEN_STORE = Path.home() / ".garminconnect"


def main() -> None:
    print("Garmin Connect — one-time login")
    print(f"Tokens will be saved to: {TOKEN_STORE}")
    print()

    email = input("Email: ").strip()
    password = getpass.getpass("Password: ")

    def prompt_mfa() -> str:
        return input("MFA code: ").strip()

    TOKEN_STORE.mkdir(mode=0o700, parents=True, exist_ok=True)

    print("\nAuthenticating...")
    try:
        client = Garmin(email=email, password=password, prompt_mfa=prompt_mfa)
        client.login(str(TOKEN_STORE))  # saves tokens to the store on success
    except Exception as exc:
        print(f"Login failed: {exc}", file=sys.stderr)
        sys.exit(1)

    for token_file in TOKEN_STORE.iterdir():
        token_file.chmod(0o600)

    print(f"\nTokens saved to {TOKEN_STORE}")
    print("You can now run the MCP server — no credentials required.")


if __name__ == "__main__":
    main()
