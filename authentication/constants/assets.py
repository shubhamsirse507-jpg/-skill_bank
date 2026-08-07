import os
import shutil
import urllib.request
from pathlib import Path

# Media & Asset URLs Configuration
# Contains direct links to external video and image assets used across authentication pages.

USER_DOWNLOADED_VIDEO = Path(r"C:\Users\Shubham\Downloads\10066-222361320_small.mp4")
CONSTANTS_DIR = Path(__file__).resolve().parent
LOCAL_VIDEO_PATH = CONSTANTS_DIR / "bg_video.mp4"


def ensure_bg_video():
    """
    Copies the user's downloaded Pixabay video from Downloads into the static directory
    so Django can serve it locally as /static/bg_video.mp4.
    """
    # 1. Check if user's downloaded video file exists in Downloads folder
    if USER_DOWNLOADED_VIDEO.exists():
        try:
            shutil.copyfile(USER_DOWNLOADED_VIDEO, LOCAL_VIDEO_PATH)
            return "/static/bg_video.mp4"
        except Exception:
            pass

    # 2. If already copied previously
    if LOCAL_VIDEO_PATH.exists() and LOCAL_VIDEO_PATH.stat().st_size > 10000:
        return "/static/bg_video.mp4"

    # 3. Fallbacks
    urls_to_try = [
        "https://pixabay.com/videos/download/video-10066_medium.mp4",
        "https://videos.pexels.com/video-files/8675543/8675543-hd_1920_1080_30fps.mp4"
    ]

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': '*/*',
        'Referer': 'https://pixabay.com/'
    }

    for url in urls_to_try:
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=15) as response:
                content = response.read()
                if len(content) > 10000:
                    with open(LOCAL_VIDEO_PATH, 'wb') as f:
                        f.write(content)
                    return "/static/bg_video.mp4"
        except Exception:
            continue

    return "https://videos.pexels.com/video-files/8675543/8675543-hd_1920_1080_30fps.mp4"


# Set static video URL on module load
AUTH_BACKGROUND_VIDEO_URL = ensure_bg_video()

# Skill Bank Lightbulb/Puzzle Logo Image
BRAND_LOGO_IMAGE_NAME = "logo.svg"
