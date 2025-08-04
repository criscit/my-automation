import yt_dlp
import argparse
from pathlib import Path
import sys

def download_video(url: str, output_path: Path):
    ydl_opts = {
        'outtmpl': str(output_path / '%(title)s.%(ext)s'),
        'format': 'bestvideo+bestaudio/best',
        'merge_output_format': 'mp4',
        'cookiefile': str(Path(__file__).with_name('cookies.txt'))
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

def load_urls(urls_from_args, file_path):
    urls = urls_from_args or []

    if file_path:
        urls.extend(
            line.strip() for line in Path(file_path).read_text().splitlines()
            if line.strip()
        )

    return urls

def main():
    parser = argparse.ArgumentParser(description="Download YouTube videos via yt-dlp")
    parser.add_argument("urls", nargs="*", help="One or more video URLs")
    parser.add_argument("-f", "--file", help="Path to file containing URLs (one per line)")
    parser.add_argument("-o", "--output", default="downloads", help="Output directory")

    args = parser.parse_args()
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    urls = load_urls(args.urls, args.file)

    if not urls:
        print("❌ No URLs provided.")
        sys.exit(1)

    for url in urls:
        print(f"⬇ Downloading: {url}")
        try:
            download_video(url, output_dir)
        except Exception as e:
            print(f"⚠️ Failed to download {url}: {e}")

if __name__ == "__main__":
    main()
