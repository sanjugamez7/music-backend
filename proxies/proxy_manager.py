# proxy_manager.py

import requests
from bs4 import BeautifulSoup
import random
import threading
import time
import json
import os

class ProxyManager:
    def __init__(self, cache_file='working_proxies.json'):
        self.proxies = []
        self.working_proxies = []
        self.cache_file = cache_file
        self.lock = threading.Lock()

        self._load_cached_proxies()
        self.refresh_proxies()

        threading.Thread(target=self._auto_refresh, daemon=True).start()

    def _auto_refresh(self):
        while True:
            time.sleep(600)  # Refresh every 10 minutes
            self.refresh_proxies()

    def _load_cached_proxies(self):
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r') as f:
                    self.proxies = json.load(f)
                    self.working_proxies = self.proxies.copy()
                    print(f"[ProxyManager] Loaded {len(self.proxies)} cached proxies.")
            except Exception as e:
                print(f"[ProxyManager] Error loading cached proxies: {e}")
        else:
            print("[ProxyManager] No cached proxy file found.")

    def _save_cached_proxies(self):
        try:
            with open(self.cache_file, 'w') as f:
                json.dump(self.working_proxies, f)
            print(f"[ProxyManager] Saved {len(self.working_proxies)} working proxies.")
        except Exception as e:
            print(f"[ProxyManager] Error saving proxies: {e}")

    def refresh_proxies(self):
        print("[ProxyManager] Refreshing proxies...")
        url = "https://free-proxy-list.net/"
        try:
            response = requests.get(url, timeout=10)
            soup = BeautifulSoup(response.text, "html.parser")
            rows = soup.select("table tbody tr")

            new_proxies = []
            for row in rows:
                cols = row.find_all("td")
                if len(cols) < 7:
                    continue
                ip = cols[0].text
                port = cols[1].text
                https = cols[6].text
                if https.lower() == "yes":
                    proxy = f"http://{ip}:{port}"
                    if self._test_proxy(proxy):
                        new_proxies.append(proxy)

            with self.lock:
                self.proxies = new_proxies
                self.working_proxies = new_proxies.copy()
                self._save_cached_proxies()

            print(f"[ProxyManager] Found {len(new_proxies)} working proxies.")
        except Exception as e:
            print(f"[ProxyManager] Error fetching proxies: {e}")

    def _test_proxy(self, proxy):
        try:
            response = requests.get("https://httpbin.org/ip", proxies={"http": proxy, "https": proxy}, timeout=5)
            return response.status_code == 200
        except:
            return False

    def get_proxy(self):
        with self.lock:
            if not self.working_proxies:
                return None
            return random.choice(self.working_proxies)

    def remove_proxy(self, proxy):
        with self.lock:
            if proxy in self.working_proxies:
                self.working_proxies.remove(proxy)
            if proxy in self.proxies:
                self.proxies.remove(proxy)
            self._save_cached_proxies()
            print(f"[ProxyManager] Removed bad proxy: {proxy}")
