import yt_dlp
from cachetools import TTLCache
from proxies.proxy_manager import ProxyManager

# Initialize proxy manager
proxy_manager = ProxyManager()

# Cache: up to 1000 items, each expires after 30 minutes
stream_cache = TTLCache(maxsize=1000, ttl=1800)

def get_stream_url_with_proxy_rotation(video_id, proxy_manager: ProxyManager):
    # Check cache first
    if video_id in stream_cache:
        print(f"[CACHE HIT] Returning cached URL for video_id: {video_id}")
        return stream_cache[video_id]

    proxies_tried = set()
    max_attempts = 10

    for _ in range(max_attempts):
        proxy = proxy_manager.get_proxy()

        # No usable proxy left
        if not proxy or proxy in proxies_tried:
            break

        proxies_tried.add(proxy)
        print(f"[yt_dlp] Trying proxy: {proxy}")

        ydl_opts = {
            'quiet': False,
            'format': 'bestaudio/best',
            'noplaylist': True,
            'proxy': proxy,
        }

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(f"https://www.youtube.com/watch?v={video_id}", download=False)
                stream_url = info.get("url")
                if stream_url:
                    print(f"[yt_dlp] ✅ Success with proxy: {proxy}")
                    stream_cache[video_id] = stream_url
                    print(f"[CACHE SET] Stored stream URL for video_id: {video_id}")
                    return stream_url
                else:
                    print(f"[yt_dlp] ❌ Got info but no URL from proxy: {proxy}")
        except yt_dlp.utils.DownloadError as e:
            print(f"[yt_dlp] ❌ DownloadError with proxy {proxy}: {e}")
            proxy_manager.remove_proxy(proxy)
        except Exception as e:
            print(f"[yt_dlp] ❌ Unknown error with proxy {proxy}: {e}")
            proxy_manager.remove_proxy(proxy)

    # Final fallback: try without proxy
    print("[yt_dlp] ⚠️ All proxies failed. Trying direct connection.")

    try:
        ydl_opts = {
            'quiet': False,
            'format': 'bestaudio/best',
            'noplaylist': True,
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"https://www.youtube.com/watch?v={video_id}", download=False)
            stream_url = info.get("url")
            if stream_url:
                print("[yt_dlp] ✅ Success without proxy.")
                stream_cache[video_id] = stream_url
                print(f"[CACHE SET] Stored stream URL for video_id: {video_id}")
                return stream_url
            else:
                print("[yt_dlp] ❌ Got info but no URL (no proxy).")
    except yt_dlp.utils.DownloadError as e:
        print(f"[yt_dlp] ❌ Direct DownloadError: {e}")
    except Exception as e:
        print(f"[yt_dlp] ❌ Direct unknown error: {e}")

    return None
