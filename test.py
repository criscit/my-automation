import os
from yt_dlp import YoutubeDL
import rookiepy


def save_edge_cookies_to_file(file_path: str):
    """
    Fetch cookies from Edge via rookiepy and save them in Netscape cookie file format for yt-dlp.
    """
    raw_cookies = rookiepy.edge()
    with open(file_path, 'w', encoding='utf-8') as f:
        # Header for Netscape cookie format
        f.write('# Netscape HTTP Cookie File\n')
        for cookie in raw_cookies:
            domain = cookie.get('domain', '')
            include_subdomains = 'TRUE' if domain.startswith('.') else 'FALSE'
            path = cookie.get('path', '/')
            secure_flag = 'TRUE' if cookie.get('secure', False) else 'FALSE'
            # Some cookie dicts use 'expirationDate' or 'expires' for expiry timestamp
            expiry = cookie.get('expirationDate') or cookie.get('expires') or 0
            name = cookie.get('name', '')
            value = cookie.get('value', '')
            # Compose line: domain, include_subdomains, path, secure_flag, expiry, name, value
            f.write(f"{domain}\t{include_subdomains}\t{path}\t{secure_flag}\t{expiry}\t{name}\t{value}\n")


# List of video URLs to download
urls = [
    # "https://www.youtube.com/watch?v=HU2T03ckAno",
    # "https://www.youtube.com/watch?v=9Ng5juIg7LY",
    "https://content.techcreator.io/academy/5/course/658/dimensional_data_modeling_day_1_lec/dimensional_data_modeling_day_1_lec.m3u8",
    "https://content.techcreator.io/academy/5/course/659/dimensional_data_modeling_day_1_lab/dimensional_data_modeling_day_1_lab.m3u8",
    "https://content.techcreator.io/academy/5/course/660/dimensional_data_modeling_day_2_lecture/dimensional_data_modeling_day_2_lecture.m3u8",
    "https://content.techcreator.io/academy/5/course/661/dimensional_data_modeling_day_2_lab/dimensional_data_modeling_day_2_lab.m3u8",
    "https://content.techcreator.io/academy/5/course/666/dimensional_data_modeling_day_3_lec/dimensional_data_modeling_day_3_lec.m3u8",
    "https://content.techcreator.io/academy/5/course/667/dimensional_data_modeling_day_3_lab_1/dimensional_data_modeling_day_3_lab_1.m3u8",
    "https://content.techcreator.io/academy/5/course/662/fact_modeling_day_1_lecture.mp4",
    "https://content.techcreator.io/academy/5/course/663/fact_data_modeling_day_1_lab.mp4",
    "https://content.techcreator.io/academy/5/course/664/fact_modeling_day_2_lecture.mp4",
    "https://content.techcreator.io/academy/5/course/665/fact_data_modeling_day_2_lab.mp4",
    "https://content.techcreator.io/academy/5/course/668/fact_modeling_day_3_lecture.mp4",
    "https://content.techcreator.io/academy/5/course/669/fact_modeling_day_3_lab.mp4",
    "https://content.techcreator.io/academy/5/course/678/sparks_basics_lecture.mp4",
    "https://content.techcreator.io/academy/5/course/679/sparks_basic_lab.mp4",
    "https://content.techcreator.io/academy/5/course/680/advanced_spark_lecture.mp4",
    "https://content.techcreator.io/academy/5/course/681/advanced_spark_lab.mp4",
    "https://content.techcreator.io/academy/5/course/706/unit_testing_lecture.mp4",
    "https://content.techcreator.io/academy/5/course/707/unit_integration_lab.mp4",
    "https://content.techcreator.io/academy/5/course/670/ap_patterns_day_1_lecture.mp4",
    "https://content.techcreator.io/academy/5/course/671/ap_day_1_lab/ap_day_1_lab.m3u8",
    "https://content.techcreator.io/academy/5/course/672/ap_day_2_lecture/ap_day_2_lecture.m3u8",
    "https://content.techcreator.io/academy/5/course/673/ap_day_2_lab.mp4",
    "https://www.youtube.com/watch?v=dzB0HMtMIfI",
    "https://content.techcreator.io/academy/5/course/674/straming_pipelines_day_1_lecture.mp4",
    "https://content.techcreator.io/academy/5/course/675/streaming_pipelines_day_1_lab.mp4",
    "https://content.techcreator.io/academy/5/course/676/streaming_pipelines_day_2_lecture.mp4",
    "https://content.techcreator.io/academy/5/course/677/streaming_pipelines_day_2_lab.mp4",
    "https://content.techcreator.io/academy/5/course/690/visualization_day_1_lecture.mp4",
    "https://content.techcreator.io/academy/5/course/691/visualization_day_1_lab.mp4",
    "https://content.techcreator.io/academy/5/course/692/visualization_day_2_lecture.mp4",
    "https://content.techcreator.io/academy/5/course/693/visualization_day_2_lab.mp4",
    "https://content.techcreator.io/academy/5/course/686/data_maint._day_1_lecture/data_maint._day_1_lecture.m3u8",
    "https://content.techcreator.io/academy/5/course/688/data_maint._day_2.mp4",
    "https://content.techcreator.io/academy/5/course/694/kpi_day_1_lecture.mp4",
    "https://content.techcreator.io/academy/5/course/695/kpi_day_1_lab/kpi_day_1_lab.m3u8",
    "https://content.techcreator.io/academy/5/course/696/kpi_day_2_lecture.mp4",
    "https://content.techcreator.io/academy/5/course/698/spec_building_lecture.mp4",
    "https://content.techcreator.io/academy/5/course/699/spec_building_lab.mp4",
    "https://content.techcreator.io/academy/5/course/700/master_data_contracts_in_25_minutes_-_dataexpert.io_boot_camp_week_3_day_2_analytics.mp4"
]

# Create output directory
os.makedirs('downloaded_videos', exist_ok=True)

# Save cookies to file
cookies_file = 'edge_cookies.txt'
save_edge_cookies_to_file(cookies_file)

# Configure yt-dlp options using cookiefile
ydl_opts = {
    'outtmpl': 'downloaded_videos/%(title)s.%(ext)s',  # Save with video title
    'format': 'best',  # Download best available quality
    'merge_output_format': 'mp4',  # Merge formats into mp4 when needed
    'noplaylist': True,  # Download single videos only
    'cookiefile': cookies_file,  # Load cookies from file
}

# Download all videos
with YoutubeDL(ydl_opts) as ydl:
    ydl.download(urls)

print("Download complete. Videos are saved in the 'downloaded_videos' folder.")
