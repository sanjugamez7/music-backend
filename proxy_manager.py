import aiohttp
import asyncio
import random

class ProxyManager:
    def __init__(self):
        self.proxies = []
        self.source_url = "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt"

    async def fetch_proxies(self):
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(self.source_url) as resp:
                    if resp.status == 200:
                        text = await resp.text()
                        self.proxies = list(set(text.strip().split('\n')))
                        print(f"✅ Fetched {len(self.proxies)} proxies")
            except Exception as e:
                print(f"❌ Failed to fetch proxies: {e}")

    def get_random_proxy(self):
        if not self.proxies:
            return None
        return random.choice(self.proxies)

    def remove_bad_proxy(self, proxy):
        if proxy in self.proxies:
            self.proxies.remove(proxy)
