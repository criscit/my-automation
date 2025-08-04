import logging
import re
from pathlib import Path
from typing import Dict, Optional

import rookiepy
from aiohttp import ClientSession, CookieJar, ClientError
from yarl import URL

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s"
)

_MODULE_HEADER_RE = re.compile(r"^##\s+Module\s*0*(\d+)\s*-\s*(.+)$", re.MULTILINE)
_LINK_IN_LIST_RE = re.compile(r"\[([^\]]+)\]\((https?://[^\s)]+)\)")
_LESSON_URL_RE = re.compile(r"https?://[^)]+lesson[^)]*", re.IGNORECASE)

YOUTUBE_RE = re.compile(
    r'https?://(?:www\.)?youtube\.com/watch\?v=([A-Za-z0-9_-]{11})'
)
SRC_FLINK_LAB_SETUP_FILES_RE = re.compile(r'src="\./Flink Lab Setup_files/([A-Za-z0-9_-]{11})\.html"')
VIDEO_FILE_RE = re.compile(
    r'"(?:raw_)?video_url"\s*:\s*"([^"]+)"'
)
BASE_CDN = "https://content.techcreator.io/"
BASE_COURSE_CDN = "https://content.techcreator.io/academy/5/course/"


def lessons_dict(md_text: str) -> Dict[str, dict]:
    lessons = {}
    current_module = None

    for line in md_text.splitlines():
        header_match = _MODULE_HEADER_RE.match(line)
        if header_match:
            module_number = int(header_match.group(1))
            module_title = header_match.group(2).strip()
            current_module = f"Module {module_number:02d} - {module_title}"
            continue

        if not current_module:
            continue

        link_match = _LINK_IN_LIST_RE.search(line)
        if not link_match:
            continue

        title = link_match.group(1).strip()
        url = link_match.group(2)

        if not _LESSON_URL_RE.search(url) or title.lower().startswith("view "):
            continue

        lessons[title] = {"link": url, "module": current_module}

    return lessons


def load_edge_cookies() -> CookieJar:
    raw_cookies = rookiepy.edge()
    cookie_jar = CookieJar()
    for cookie in raw_cookies:
        cookie_jar.update_cookies(
            {cookie["name"]: cookie["value"]},
            response_url=URL.build(
                scheme="https",
                host=cookie["domain"].lstrip("."),
            ),
        )
    return cookie_jar


def extract_video_url(html: str, title) -> Optional[str]:
    if match := YOUTUBE_RE.search(html):
        return f"https://www.youtube.com/watch?v={match[1]}"
    if match := SRC_FLINK_LAB_SETUP_FILES_RE.search(html):
        return f"https://www.youtube.com/watch?v={match[1]}"
    if match := VIDEO_FILE_RE.search(html):
        return BASE_CDN + match.group(1)
    pattern = rf'"course_id"\s*:\s*(\d+),"title"\s*:\s*"{title.split('.')[1].strip()}"'
    m = re.search(pattern, html, re.MULTILINE)
    return BASE_COURSE_CDN + str(m.group(1)) if m else None


async def fetch_html(session: ClientSession, url: str) -> Optional[str]:
    try:
        async with session.get(url) as response:
            response.raise_for_status()
            return await response.text()
    except ClientError as e:
        logging.warning("HTTP request failed for URL '%s': %s", url, e)
        return None
    except Exception as e:
        logging.error("Unexpected error while fetching '%s': %s", url, e)
        return None


async def main():
    md_path = Path(r"C:\Users\crisc\Downloads\bootcamp_modules.md")

    md_text = md_path.read_text(encoding="utf-8")
    lessons = lessons_dict(md_text)
    if not lessons:
        logging.warning("No valid lessons found in markdown file.")
        return

    cookies = load_edge_cookies()

    async with ClientSession(cookie_jar=cookies) as session:
        for title, info in lessons.items():
            # logging.info("Fetching: %s", title)
            html = await fetch_html(session, info["link"])

            if not html:
                logging.warning("Failed to fetch HTML for: %s", title)
                continue

            video_url = extract_video_url(html, title)
            print(video_url)
            # if video_url:
            #     logging.info("✅ Video URL for '%s': %s", title, video_url)
            # else:
            #     logging.info("❌ No video URL found for: %s", title)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
