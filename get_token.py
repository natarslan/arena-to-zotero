#!/usr/bin/env python3
"""
One-time helper to exchange an Are.na OAuth code for an access token.

Usage:
    python get_token.py
"""

import os
import sys
import requests

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

ARENA_TOKEN_URL = "https://www.are.na/oauth/token"


def main():
    client_id = os.environ.get("ARENA_CLIENT_ID", "").strip()
    client_secret = os.environ.get("ARENA_CLIENT_SECRET", "").strip()

    if not client_id or not client_secret:
        print("Add these two lines to your .env file first:")
        print()
        print("  ARENA_CLIENT_ID=your_client_id")
        print("  ARENA_CLIENT_SECRET=your_client_secret")
        print()
        print("Both are on the OAuth application page at dev.are.na/oauth/applications")
        sys.exit(1)

    auth_url = (
        f"https://www.are.na/oauth/authorize"
        f"?client_id={client_id}"
        f"&redirect_uri=https%3A%2F%2Flocalhost"
        f"&response_type=code"
        f"&scope=write"
    )

    print("Step 1: Open this URL in your browser and click Authorize:")
    print()
    print(f"  {auth_url}")
    print()
    print("Step 2: The browser will redirect to https://localhost?code=XXXXXX")
    print("        The page won't load — that's fine.")
    print("        Copy just the code value from the address bar.")
    print()

    code = input("Paste the code here: ").strip()
    if not code:
        print("No code entered. Exiting.")
        sys.exit(1)

    print("\nExchanging code for access token…")
    resp = requests.post(ARENA_TOKEN_URL, data={
        "client_id": client_id,
        "client_secret": client_secret,
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": "https://localhost",
    })

    if resp.status_code != 200:
        print(f"Error {resp.status_code}: {resp.text}")
        sys.exit(1)

    data = resp.json()
    token = data.get("access_token")

    if not token:
        print(f"Unexpected response: {data}")
        sys.exit(1)

    print("\nSuccess! Your Are.na access token:")
    print()
    print(f"  {token}")
    print()
    print("Add this to your .env file as:")
    print()
    print(f"  ARENA_ACCESS_TOKEN={token}")


if __name__ == "__main__":
    main()
