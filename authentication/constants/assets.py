import os
import shutil
from pathlib import Path

# Media & Asset URLs Configuration
# Contains direct links to external video and image assets used across authentication pages.

CONSTANTS_DIR = Path(__file__).resolve().parent
LOCAL_VIDEO_PATH = CONSTANTS_DIR / "bg_video.mp4"

# Fallback CDN URL — used when no local video is available (e.g., on production/Render)
_FALLBACK_VIDEO_URL = "https://videos.pexels.com/video-files/8675543/8675543-hd_1920_1080_30fps.mp4"


def _get_bg_video_url():
    """
    Returns the best available background video URL.

    Resolution order:
      1. Already-copied local file (served via Django static)
      2. Windows Downloads folder (developer machine only — copied silently)
      3. External CDN URL (safe fallback — no blocking I/O at import time)

    This function is intentionally lightweight and NEVER performs any
    network requests, so it is safe to call at module import time.
    """
    # 1. Local cached copy already exists inside the constants package
    try:
        if LOCAL_VIDEO_PATH.exists() and LOCAL_VIDEO_PATH.stat().st_size > 10_000:
            return "/static/bg_video.mp4"
    except Exception:
        pass

    # 2. Developer machine: copy from Downloads (Windows-only, silent fail on Linux/Render)
    try:
        _win_download = Path(r"C:\Users\Shubham\Downloads\10066-222361320_small.mp4")
        if _win_download.exists():
            shutil.copyfile(_win_download, LOCAL_VIDEO_PATH)
            return "/static/bg_video.mp4"
    except Exception:
        pass

    # 3. Safe CDN fallback — no network I/O, just a URL string
    return _FALLBACK_VIDEO_URL


# Resolved once at module load — lightweight, no blocking network calls
AUTH_BACKGROUND_VIDEO_URL = _get_bg_video_url()

# Skill Bank Logo Image
BRAND_LOGO_IMAGE_NAME = "logo.svg"

