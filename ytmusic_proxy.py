# ytmusic_proxy.py

from ytmusicapi import YTMusic

class YTMusicClient:
    def __init__(self):
        try:
            self.ytmusic = YTMusic()
            print("[YTMusicClient] YTMusic initialized successfully.")
        except Exception as e:
            print(f"[YTMusicClient] Initialization failed: {e}")
            self.ytmusic = None

    def search(self, query):
        """
        Perform a metadata-only search using ytmusicapi.
        No proxy involved.
        """
        if not self.ytmusic:
            print("[YTMusicClient] YTMusic client is not initialized.")
            return []

        try:
            print(f"[YTMusicClient] Searching: {query}")
            return self.ytmusic.search(query)
        except Exception as e:
            print(f"[YTMusicClient] Search failed: {e}")
            return []

# Example usage
if __name__ == "__main__":
    client = YTMusicClient()
    results = client.search("Arijit Singh")
    print("Results:", results if results else "No results found.")
