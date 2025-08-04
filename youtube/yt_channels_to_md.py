#!/usr/bin/env python3
"""
Export **all channels you subscribe to** into a Markdown file.

- Uses OAuth 2.0 (same flow as the playlist script) so it works with *private*
  subscription lists.
- Produces one line per channel in the form:
    - [Channel Name](https://www.youtube.com/channel/CHANNEL_ID)
- Paginates until every subscription is retrieved.

Quick use
---------
1. Create (or reuse) a *Desktop‑app* OAuth client in Google Cloud.
2. Add your Google account to **OAuth → Test users**.
3. Install requirements:

   ```bash
   pip install google-api-python-client google-auth google-auth-oauthlib
   ```

4. Run:

   ```bash
   python youtube_channels_to_md_api.py \
       --client-secrets ~/client_secret.json \
       --output my_channels.md
   ```

The first run will pop a browser window for consent; subsequent runs reuse
`token.json`.
"""
from __future__ import annotations

import sys
from argparse import ArgumentParser, RawTextHelpFormatter
from pathlib import Path
from typing import List

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

API_SERVICE_NAME = "youtube"
API_VERSION = "v3"
SCOPES = ["https://www.googleapis.com/auth/youtube.readonly"]

# ── ▶︎ Default settings ────────────────────────────────────────────────────
OUTPUT_DEFAULT_FILE = "channels.md"
CLIENT_SECRETS_DEFAULT = r"C:\\Users\\crisc\\client_secret_666632475794-r3cdbl1nob8r908fu86hvl6r6hn4ep7l.apps.googleusercontent.com.json"  # Put your file here or pass --client-secrets
TOKEN_DEFAULT = "token.json"
# ───────────────────────────────────────────────────────────────────────────

def _get_authenticated_service(client_secrets: Path, token_path: Path):
    """Return an authorised YouTube API service object (OAuth 2 desktop flow)."""
    creds: Credentials | None = None
    if token_path.exists():
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(client_secrets, SCOPES)
            try:
                creds = flow.run_console()
            except AttributeError:
                # Newer google-auth-oauthlib removed run_console(): fall back
                creds = flow.run_local_server(port=0, prompt="consent")
        # cache
        token_path.write_text(creds.to_json())

    return build(API_SERVICE_NAME, API_VERSION, credentials=creds, cache_discovery=False)


def subscriptions_to_markdown(youtube) -> str:
    """Return Markdown listing every channel the user is subscribed to."""
    lines: List[str] = []
    page_token = None

    while True:
        resp = (
            youtube.subscriptions()
            .list(
                part="snippet",
                mine=True,
                maxResults=50,
                pageToken=page_token,
                order="alphabetical",
            )
            .execute()
        )

        for item in resp["items"]:
            snippet = item["snippet"]
            chan_title = snippet["title"]
            chan_id = snippet["resourceId"]["channelId"]
            lines.append(f"- [{chan_title}](https://www.youtube.com/channel/{chan_id})")

        page_token = resp.get("nextPageToken")
        if not page_token:
            break

    return "\n".join(lines) + "\n"


def main(argv: List[str] | None = None) -> None:
    parser = ArgumentParser(
        formatter_class=RawTextHelpFormatter,
        description="Generate a Markdown file of all channels you subscribe to.",
    )
    parser.add_argument(
        "-o",
        "--output",
        default=OUTPUT_DEFAULT_FILE,
        help="Path to output .md file (default: channels.md).",
    )
    parser.add_argument(
        "--client-secrets",
        default=CLIENT_SECRETS_DEFAULT,
        help="Path to OAuth client_secret.json (Desktop app).",
    )
    parser.add_argument(
        "--token",
        default=TOKEN_DEFAULT,
        help="Path to cache OAuth token (default token.json).",
    )
    ns = parser.parse_args(argv)

    client_secrets_path = Path(ns.client_secrets).expanduser().resolve()
    if not client_secrets_path.exists():
        sys.exit(f"Client secrets not found: {client_secrets_path}")

    youtube = _get_authenticated_service(client_secrets_path, Path(ns.token).expanduser())

    md_path = Path(ns.output).expanduser().resolve()
    md_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        md_content = subscriptions_to_markdown(youtube)
    except HttpError as e:
        sys.exit(f"YouTube API error: {e}\n")

    md_path.write_text(md_content, encoding="utf-8")
    print(f"Exported {md_content.count('\n') - 1} channels → {md_path}")


if __name__ == "__main__":
    main()
