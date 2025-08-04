import logging
import re
from pathlib import Path
from typing import List, Optional
import csv

from common.cookies import load_edge_cookies
from aiohttp import ClientSession

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

BOOTCAMP_MODULES_MD = Path(r"C:\Users\crisc\Downloads\bootcamp_modules.md")
CSV_OUT_PATH = Path("data/bootcamp_lessons.csv")

# Regex patterns
_MODULE_HEADER_RE = re.compile(r"^##\s+Module\s*0*(\d+)\s*-\s*(.+)$")
_LINK_IN_LIST_RE = re.compile(r"\[([^\]]+)\]\((https?://[^\s)]+)\)")
_LESSON_URL_RE = re.compile(r"https?://[^)]+lesson[^)]*", re.IGNORECASE)

YOUTUBE_RE = re.compile(r"https?://(?:www\.)?youtube\.com/watch\?v=([A-Za-z0-9_-]{11})")
SRC_FLINK_LAB_RE = re.compile(r'src="\./Flink Lab Setup_files/([A-Za-z0-9_-]{11})\.html"')
VIDEO_FILE_RE = re.compile(r'"(?:raw_)?video_url"\s*:\s*"([^"]+?)"')
COURSE_ID_RE = lambda title: re.compile(
    rf'"course_id"\s*:\s*(\d+),"title"\s*:\s*"{re.escape(title.split('.')[-1].strip())}"'
)
BASE_CDN = "https://content.techcreator.io/"
BASE_COURSE_CDN = "https://content.techcreator.io/academy/5/course/"


def parse_lessons(md_path: Path) -> List[dict]:
    lessons, current_module = [], None
    for line in md_path.read_text('utf-8').splitlines():
        h = _MODULE_HEADER_RE.match(line)
        if h:
            num, title = h.groups()
            current_module = f"Module {int(num):02d} - {title.strip()}"
            continue
        if current_module:
            m = _LINK_IN_LIST_RE.search(line)
            if m and _LESSON_URL_RE.search(m.group(2)) and not m.group(1).lower().startswith("view "):
                lessons.append({'title': m.group(1).strip(), 'lesson_url': m.group(2), 'module': current_module})
    return lessons


def write_lessons_csv(lessons: List[dict], csv_path: Path) -> None:
    # Flatten video_urls: one row per URL or None
    fieldnames = ['title', 'lesson_url', 'module', 'video_url']
    with csv_path.open('w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=';')
        writer.writeheader()
        for lesson in lessons:
            urls = lesson.get('video_urls') or []
            if urls:
                for url in urls:
                    writer.writerow({
                        'title': lesson['title'],
                        'lesson_url': lesson['lesson_url'],
                        'module': lesson['module'],
                        'video_url': url
                    })
            else:
                writer.writerow({
                    'title': lesson['title'],
                    'lesson_url': lesson['lesson_url'],
                    'module': lesson['module'],
                    'video_url': ''
                })


def extract_video_urls(html: str, title: str) -> List[str]:
    urls = [f"https://www.youtube.com/watch?v={vid}" for vid in YOUTUBE_RE.findall(html)]
    urls += [f"https://www.youtube.com/watch?v={vid}" for vid in SRC_FLINK_LAB_RE.findall(html)]
    for p in VIDEO_FILE_RE.findall(html):
        urls.append(p if p.startswith('http') else BASE_CDN + p)
    urls += [BASE_COURSE_CDN + cid for cid in COURSE_ID_RE(title).findall(html)]
    return list(dict.fromkeys(urls))

async def fetch_html(session: ClientSession, url: str) -> Optional[str]:
    try:
        async with session.get(url) as resp:
            resp.raise_for_status()
            return await resp.text()
    except Exception:
        logging.warning("Failed to fetch %s", url)
        return None

async def main():
    lessons = parse_lessons(BOOTCAMP_MODULES_MD)
    if not lessons:
        logging.warning("No lessons parsed; exiting.")
        return
    jar = load_edge_cookies()
    async with ClientSession(cookie_jar=jar) as session:
        for lesson in lessons:
            html = await fetch_html(session, lesson['lesson_url']) or ""
            vids = extract_video_urls(html, lesson['title'])
            lesson['video_urls'] = vids
            if vids:
                logging.info("✅ %s -> %s", lesson['title'], vids)
            else:
                logging.info("❌ No videos for %s", lesson['title'])
    write_lessons_csv(lessons, CSV_OUT_PATH)
    logging.info("Processed %d lessons", len(lessons))

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
