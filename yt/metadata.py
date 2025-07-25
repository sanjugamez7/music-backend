from ytmusicapi import YTMusic

ytmusic = YTMusic()

def get_metadata(query):
    query = query.strip().lower()

    print(f"[Metadata] Fetching from YouTube Music for: {query}")
    results = ytmusic.search(query, filter="songs")
    if not results:
        return {}

    first = results[0]
    metadata = {
        "title": first.get("title"),
        "artist": ", ".join(a["name"] for a in first.get("artists", [])),
        "videoId": first.get("videoId"),
        "thumbnail": first.get("thumbnails", [{}])[-1].get("url")
    }

    return metadata
