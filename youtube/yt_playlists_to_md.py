#!/usr/bin/env python3
"""
Convert YouTube playlists (public **or PRIVATE**) to a Markdown file.

Why this version?
-----------------
Using a simple **API key** only allows access to *public* data. To fetch your
*private* playlists ("Unlisted", "Private", liked videos, etc.) we must use
**OAuth 2.0** user credentials with the scope `https://www.googleapis.com/auth/youtube.readonly`.

You will run through a one‑time browser flow: grant access → paste the code
back → we cache `token.json` for next time. After that, the script runs
non‑interactively.

Quick start
-----------
1. **Enable** *YouTube Data API v3* in the Google Cloud Console.
2. **Create credentials → OAuth client ID → Desktop app*. Download the
   JSON: `client_secret_XXXX.json`.
3. Install deps:

   ```bash
   pip install google-api-python-client google-auth google-auth-oauthlib
   ```

4. Run:

   ```bash
   python youtube_playlist_to_md_api.py \
       --client-secrets ~/client_secret_XXXX.json \
       --output playlists.md \
       https://www.youtube.com/playlist?list=PL... LL
   ```

The first run opens a URL—paste the auth code. From then on, your playlists
(cached token) are downloaded silently.
"""

from __future__ import annotations

import os
import sys
from argparse import ArgumentParser, RawTextHelpFormatter
from pathlib import Path
from typing import List
from urllib.parse import parse_qs, urlparse

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

API_SERVICE_NAME = "youtube"
API_VERSION = "v3"
SCOPES = ["https://www.googleapis.com/auth/youtube.readonly"]

# ── ▶︎ Default settings ────────────────────────────────────────────────────
OUTPUT_DEFAULT_FILE = r"C:\\Users\\crisc\\iCloudDrive\\iCloud~md~obsidian\\personal-info\\Routine\\Content to Clean.md"
CLIENT_SECRETS_DEFAULT = r"C:\\Users\\crisc\\client_secret_666632475794-r3cdbl1nob8r908fu86hvl6r6hn4ep7l.apps.googleusercontent.com.json"  # Put your file here or pass --client-secrets
TOKEN_DEFAULT = "token.json"

PLAYLIST_URLS = [
    "https://www.youtube.com/playlist?list=PLfIWBOpdRR6fXC5rv_znBdlBn6d7O5gAb",
    "https://www.youtube.com/playlist?list=PLfIWBOpdRR6femo0UVj-yqRHR4YUGgw8t",
    "https://www.youtube.com/playlist?list=PLfIWBOpdRR6e7otDbIzOMAuEpn2ixdGDS",
    "https://www.youtube.com/playlist?list=PLfIWBOpdRR6eo4VVjxitnNEGu6DbpFXWo",
    "https://www.youtube.com/playlist?list=PLfIWBOpdRR6ckegLLI3l4TEgAmn0vVjXK",
    "https://www.youtube.com/playlist?list=PLfIWBOpdRR6fzhdz5dlfYTvCzygWIEAx_",
    "https://www.youtube.com/playlist?list=PLfIWBOpdRR6deabz4B6DKdQxuCiG5qmwj",
    "https://www.youtube.com/playlist?list=PLfIWBOpdRR6f5FaVMpu_J2GT6KixhcWI-",
    "https://www.youtube.com/playlist?list=PLfIWBOpdRR6er0GABRPEFCzIhCjQB9vPx",
    "https://www.youtube.com/playlist?list=LL",
]
# ───────────────────────────────────────────────────────────────────────────


def _extract_playlist_id(url_or_id: str) -> str:
    """Return just the playlist ID, whether a bare ID or a full URL is given."""
    if url_or_id.startswith(("http://", "https://")):
        parsed = urlparse(url_or_id)
        query = parse_qs(parsed.query)
        playlist_id = query.get("list", [None])[0]
        if not playlist_id:
            raise ValueError(f"Cannot find 'list' parameter in URL: {url_or_id}")
        return playlist_id
    return url_or_id  # Assume caller already provided the ID


def _get_authenticated_service(client_secrets: Path, token_path: Path):
    """Return an authorised YouTube API service object."""
    creds: Credentials | None = None
    if token_path.exists():
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)
    # Refresh / re‑authenticate if needed
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(client_secrets, SCOPES)
            # Newer google-auth-oauthlib versions have both .run_console() and .run_local_server().
            # To stay compatible with older versions that *only* have .run_local_server(),
            # we attempt run_console() first, then fall back.
            try:
                creds = flow.run_console()
            except AttributeError:
                # Fallback for old versions: open a browser on localhost and wait for redirect
                creds = flow.run_local_server(port=0, prompt="consent")  # Opens URL, prompts for code
        # Cache
        token_path.write_text(creds.to_json())
    return build(API_SERVICE_NAME, API_VERSION, credentials=creds, cache_discovery=False)


def playlist_to_markdown(youtube, playlist_id: str) -> str:
    """Return a Markdown fragment for a single playlist (all items)."""
    # Fetch playlist title
    pl_resp = (
        youtube.playlists().list(part="snippet", id=playlist_id, maxResults=1).execute()
    )
    if not pl_resp["items"]:
        raise ValueError(f"No playlist found for ID {playlist_id}")
    title = pl_resp["items"][0]["snippet"]["title"]
    lines = [f"# {title}"]

    # Paginate through playlist items
    page_token = None
    while True:
        items_resp = (
            youtube.playlistItems()
            .list(
                part="snippet",
                playlistId=playlist_id,
                maxResults=50,
                pageToken=page_token,
            )
            .execute()
        )
        for item in items_resp["items"]:
            s = item["snippet"]
            vid_id = s["resourceId"]["videoId"]
            vid_title = s["title"]
            lines.append(f"- [{vid_title}](https://www.youtube.com/watch?v={vid_id})")
        page_token = items_resp.get("nextPageToken")
        if not page_token:
            break

    return "\n".join(lines) + "\n\n"


def main(argv: List[str] | None = None) -> None:
    parser = ArgumentParser(
        formatter_class=RawTextHelpFormatter,
        description=(
            "Generate a Markdown file from one or more YouTube playlists—public or *private*—"
            "using OAuth 2.0 credentials (YouTube Data API v3)."
        ),
    )
    parser.add_argument(
        "-o",
        "--output",
        default=OUTPUT_DEFAULT_FILE,
        help=f"Path to output .md file (default: {OUTPUT_DEFAULT_FILE!r}).",
    )
    parser.add_argument(
        "--client-secrets",
        default=CLIENT_SECRETS_DEFAULT,
        help="Path to your client_secret.json (desktop app credentials).",
    )
    parser.add_argument(
        "--token",
        default=TOKEN_DEFAULT,
        help="Path to cache the OAuth token (default token.json).",
    )
    parser.add_argument(
        "urls",
        nargs="*",
        help="Zero or more YouTube playlist URLs or IDs. Omit to use defaults.",
    )

    ns = parser.parse_args(argv)

    client_secrets_path = Path(ns.client_secrets).expanduser().resolve()
    if not client_secrets_path.exists():
        sys.exit(
            f"Client secrets file not found: {client_secrets_path}\n"
            "Download it from Google Cloud Console → Credentials → OAuth 2.0 Client IDs."
        )

    youtube = _get_authenticated_service(client_secrets_path, Path(ns.token).expanduser())

    raw_urls = ns.urls or PLAYLIST_URLS
    playlist_ids = [_extract_playlist_id(u) for u in raw_urls]

    md_path = Path(ns.output).expanduser().resolve()
    md_path.parent.mkdir(parents=True, exist_ok=True)

    with md_path.open("w", encoding="utf-8") as md_file:
        for pid, src in zip(playlist_ids, raw_urls):
            try:
                md_file.write(playlist_to_markdown(youtube, pid))
                print(f"✔ Added {src}")
            except (HttpError, Exception) as exc:
                print(f"✘ Failed {src}: {exc}", file=sys.stderr)

    print(f"\nAll done! Markdown saved to: {md_path}")


if __name__ == "__main__":
    main()
