import csv
import logging
import re
from pathlib import Path

from yt_dlp import YoutubeDL
from common.cookies import load_edge_cookies  # your in-house cookie loader

# ——— CONFIG —————————————————————————————————————————————————————————
BASE_PATH = Path(r"C:\Users\crisc\Desktop\DataExpert.io Boot Camp")
CSV_FILE  = Path("data/bootcamp_lessons.csv")
YDL_FORMAT = "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best"
# ———————————————————————————————————————————————————————————————

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


def cookiejar_to_header(cj):
    """Serialize aiohttp.CookieJar into a single Cookie header."""
    return "; ".join(f"{c.key}={c.value}" for c in cj)


def load_lessons(csv_path: Path):
    lessons = {}
    with csv_path.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f, delimiter=";")
        for row in reader:
            mod   = row["module"].strip()
            title = row["title"].strip()
            url   = row["video_url"].strip()
            if not url:
                continue
            lessons.setdefault((mod, title), []).append(url)

    # — Simplified MP4-first ordering —
    for urls in lessons.values():
        urls.sort(key=lambda u: not u.lower().endswith(".mp4"))

    return lessons


async def main():
    # build headers from Edge cookies
    cj = load_edge_cookies()
    headers = {"Cookie": cookiejar_to_header(cj)}

    ydl_opts = {
        "format":    YDL_FORMAT,
        "http_headers": headers,
        # "quiet":     True,
        # "no_warnings": True,
    }

    lessons = load_lessons(CSV_FILE)
    if not lessons:
        logging.error("No lessons found in %s", CSV_FILE)
        return

    with YoutubeDL(ydl_opts) as ydl:
        for (module, title), urls in lessons.items():
            target_dir = BASE_PATH / module
            target_dir.mkdir(parents=True, exist_ok=True)

            safe_title = re.sub(r'\s+', ' ', re.sub(r'[^A-Za-z0-9 _-]+', ' ', title)).strip()
            outtmpl = str((target_dir / f"{safe_title}.mp4").resolve())
            ydl.params["outtmpl"] = outtmpl

            for url in urls:
                try:
                    print(url)
                    logging.info("Downloading %r from %s", title, url)
                    ydl.download([url])
                    logging.info("✅ Success: %s", outtmpl)
                    break
                except Exception as e:
                    logging.warning("❌ Failed (%s): %s", url, e)
            else:
                # only reached if no break occurred
                logging.error("⚠️  All URLs failed for %r", title)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
