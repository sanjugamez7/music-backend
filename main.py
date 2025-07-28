import os
from flask import Flask, jsonify, request
from flask_cors import CORS
from ytmusicapi import YTMusic

app = Flask(__name__)
CORS(app)

# ✅ Initialize YTMusic
try:
    print("⚙️ Initializing YTMusic...")
    ytmusic = YTMusic()  # Anonymous auth headers
    print("✅ YTMusic initialized")
except Exception as e:
    print(f"❌ YTMusic init failed: {e}")
    ytmusic = None

# ✅ Root route
@app.route("/")
def index():
    return jsonify({"status": "✅ music-backend is running"}), 200

# ✅ Favicon route
@app.route("/favicon.ico")
def favicon():
    return '', 204

# 🔍 Search songs
@app.route("/search", methods=["GET"])
def search():
    query = request.args.get("q")
    print(f"[SEARCH] Searching for: {query}")

    if not query:
        return jsonify({"error": "Missing search query"}), 400

    try:
        raw_results = ytmusic.search(query, filter="songs", limit=25)
        results = []

        for r in raw_results:
            if "videoId" in r:
                results.append({
                    "videoId": r["videoId"],
                    "title": r["title"],
                    "artist": ", ".join([a["name"] for a in r.get("artists", [])]),
                    "thumbnailUrl": r["thumbnails"][-1]["url"] if r.get("thumbnails") else None,
                    "duration": r.get("duration"),
                    "album": r.get("album", {}).get("name"),
                })

        return jsonify(results)
    except Exception as e:
        print(f"[ERROR] Search failed: {e}")
        return jsonify({"error": str(e)}), 500

# 🎵 Get song metadata by videoId
@app.route("/metadata", methods=["GET"])
def fetch_metadata():
    video_id = request.args.get("q")
    print(f"[METADATA] Fetching for video ID: {video_id}")

    if not video_id:
        return jsonify({'error': 'Missing video ID'}), 400

    try:
        data = ytmusic.get_song(video_id)
        song_info = data.get("videoDetails", {})
        microformat = data.get("microformat", {}).get("microformatDataRenderer", {})

        result = {
            "videoId": song_info.get("videoId"),
            "title": song_info.get("title"),
            "artist": song_info.get("author"),
            "album": data.get("microformat", {}).get("microformatDataRenderer", {}).get("title"),
            "duration": song_info.get("lengthSeconds"),
            "thumbnailUrl": song_info.get("thumbnail", {}).get("thumbnails", [{}])[-1].get("url"),
            "description": microformat.get("description"),
            "viewCount": song_info.get("viewCount"),
            "publishDate": microformat.get("publishDate"),
            "availableCountries": microformat.get("availableCountries", []),
        }

        print(f"[METADATA RESULT] {result}")
        return jsonify(result)
    except Exception as e:
        print(f"[ERROR] Metadata fetch failed: {e}")
        return jsonify({'error': str(e)}), 500

# 🔥 Trending charts
@app.route("/trending", methods=["GET"])
def trending():
    print("[TRENDING] Fetching charts")
    try:
        charts = ytmusic.get_charts()
        return jsonify(charts)
    except Exception as e:
        print(f"[ERROR] Trending fetch failed: {e}")
        return jsonify({"error": str(e)}), 500

# 📃 Playlist details
@app.route("/playlist", methods=["GET"])
def get_playlist():
    playlist_id = request.args.get("id")
    print(f"[PLAYLIST] Fetching: {playlist_id}")

    if not playlist_id:
        return jsonify({"error": "Missing playlist ID"}), 400

    try:
        playlist = ytmusic.get_playlist(playlist_id)
        return jsonify(playlist)
    except Exception as e:
        print(f"[ERROR] Playlist fetch failed: {e}")
        return jsonify({"error": str(e)}), 500

# 💿 Album details
@app.route("/album", methods=["GET"])
def get_album():
    album_id = request.args.get("id")
    print(f"[ALBUM] Fetching: {album_id}")

    if not album_id:
        return jsonify({"error": "Missing album ID"}), 400

    try:
        album = ytmusic.get_album(album_id)
        return jsonify(album)
    except Exception as e:
        print(f"[ERROR] Album fetch failed: {e}")
        return jsonify({"error": str(e)}), 500

# 👤 Artist details
@app.route("/artist", methods=["GET"])
def get_artist():
    artist_id = request.args.get("id")
    print(f"[ARTIST] Fetching: {artist_id}")

    if not artist_id:
        return jsonify({"error": "Missing artist ID"}), 400

    try:
        artist = ytmusic.get_artist(artist_id)
        return jsonify(artist)
    except Exception as e:
        print(f"[ERROR] Artist fetch failed: {e}")
        return jsonify({"error": str(e)}), 500

# 🌐 Catch-all fallback
@app.route("/<path:path>")
def catch_all(path):
    return jsonify({"catch": path}), 200

# 🛠️ Run the server
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    print(f"👟 Starting development server on port {port}")
    app.run(host="0.0.0.0", port=port)
