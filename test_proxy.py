import time
import requests
from proxy_manager import ProxyManager

proxy_manager = ProxyManager()
time.sleep(15)  # wait for proxies to load

proxy = proxy_manager.get_random_proxy()

if proxy:
    print("Using proxy:", proxy)
    try:
        r = requests.get("https://httpbin.org/ip", proxies={"http": proxy, "https": proxy}, timeout=5)
        print("Your IP is:", r.json())
    except Exception as e:
        print("Request failed:", e)
else:
    print("No proxy available.")
