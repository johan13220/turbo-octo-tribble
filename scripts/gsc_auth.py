"""
One-time script to authenticate with Google Search Console via OAuth2.

Steps:
  1. Go to https://console.cloud.google.com/
  2. Create a project → Enable "Google Search Console API"
  3. Create OAuth2 credentials (type: Desktop app) → Download credentials.json
  4. Run: python scripts/gsc_auth.py
  5. Copy the printed GSC_* lines into your .env file

After setup, the dashboard will refresh the token automatically.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

SCOPES = ["https://www.googleapis.com/auth/webmasters.readonly"]
DEFAULT_TOKEN_PATH = "~/.seo_dashboard/gsc_token.json"


def main() -> None:
    print("=== Google Search Console OAuth2 Setup ===\n")

    credentials_path = input("Path to credentials.json (downloaded from Google Cloud): ").strip()
    if not credentials_path:
        print("Error: credentials path is required.")
        sys.exit(1)

    credentials_path = os.path.expanduser(credentials_path)
    if not Path(credentials_path).exists():
        print(f"Error: file not found: {credentials_path}")
        sys.exit(1)

    token_input = input(f"Where to save the token [{DEFAULT_TOKEN_PATH}]: ").strip()
    token_path = os.path.expanduser(token_input or DEFAULT_TOKEN_PATH)

    try:
        from google_auth_oauthlib.flow import InstalledAppFlow
    except ImportError:
        print("Error: run `pip install google-auth-oauthlib` first.")
        sys.exit(1)

    print("\nOpening browser for authorization...")
    flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
    creds = flow.run_local_server(port=0)

    Path(token_path).parent.mkdir(parents=True, exist_ok=True)
    Path(token_path).write_text(creds.to_json())

    print(f"\nToken saved to: {token_path}")
    print("\nAdd these lines to your .env file:")
    print(f"GSC_CREDENTIALS_PATH={credentials_path}")
    print(f"GSC_TOKEN_PATH={token_path}")
    print("\nSetup complete.")


if __name__ == "__main__":
    main()
