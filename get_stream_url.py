# get_stream_url.py

import yt_dlp
from proxy_manager import ProxyManager

def get_stream_url(video_id, proxy=None):
    ydl_opts = {
        'quiet': True,
        'format': 'bestaudio',
        'noplaylist': True,
        'proxy': proxy,  # ✅ Proxy passed directly to yt_dlp
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(f"https://www.youtube.com/watch?v={video_id}", download=False)
        return info['url']

def get_stream_url_with_proxy_rotation(video_id, proxy_manager, max_retries=5):
    """
    Tries multiple proxies to get the video stream URL.
    If all proxies fail, raises an exception.
    """
    for _ in range(max_retries):
        proxy = proxy_manager.get_proxy()
        if not proxy:
            break  # No proxies left
        try:
            print(f"[yt_dlp] Trying proxy: {proxy}")
            return get_stream_url(video_id, proxy=proxy)
        except Exception as e:
            print(f"[yt_dlp] Proxy failed: {proxy} | Error: {e}")
            proxy_manager.remove_proxy(proxy)

    # Optional: Try once without proxy as fallback
    try:
        print("[yt_dlp] Trying without proxy...")
        return get_stream_url(video_id)
    except Exception as e:
        raise Exception(f"[yt_dlp] All attempts failed. Final error: {e}")
