import time
from ytmusicapi import YTMusic
from proxy_manager import ProxyManager
import requests

proxy_manager = ProxyManager()
time.sleep(15)  # Wait for initial proxy load

def get_ytmusic_with_proxy():
    for _ in range(10):
        proxy = proxy_manager.get_proxy()
        if not proxy:
            print("[YTMusic] No proxies available.")
            return None

        try:
            session = requests.Session()
            session.proxies = {"http": proxy, "https": proxy}
            session.headers.update({
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                              "AppleWebKit/537.36 (KHTML, like Gecko) "
                              "Chrome/122.0.0.0 Safari/537.36"
            })

            yt = YTMusic(requests_session=session)  # Inject proxy-aware session
            test_result = yt.search("Arijit Singh")
            if test_result:
                print(f"[YTMusic] Proxy success: {proxy}")
                return yt

        except Exception as e:
            print(f"[YTMusic] Proxy failed ({proxy}): {e}")
            proxy_manager.remove_proxy(proxy)

    print("[YTMusic] All proxies failed.")
    return None


if __name__ == "__main__":
    yt = get_ytmusic_with_proxy()
    if yt:
        results = yt.search("Arijit Singh")
        for song in results[:5]:
            print(f"{song['title']} - {song['artists'][0]['name']}")
    else:
        print("No working proxy found.")
