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
            try:
                video_id = r.get("videoId")
                title = r.get("title")
                artist_list = r.get("artists", [])
                album_info = r.get("album") or {}

                # ✅ Safe thumbnail extraction
                thumbnails = r.get("thumbnails") or []
                thumbnail_url = None
                for thumb in reversed(thumbnails):
                    if thumb and thumb.get("url"):
                        thumbnail_url = thumb["url"]
                        break

                # ✅ Ensure valid song data
                if not video_id or not title or not artist_list:
                    continue

                artists = ", ".join([a.get("name", "") for a in artist_list if a.get("name")])

                results.append({
                    "videoId": video_id,
                    "title": title,
                    "artist": artists,
                    "thumbnailUrl": thumbnail_url,
                    "duration": r.get("duration"),
                    "album": album_info.get("name")
                })
            except Exception as inner_e:
                print(f"[WARN] Skipped malformed result: {inner_e}")
                continue

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

        # ✅ Safe thumbnail from metadata
        thumbnails = song_info.get("thumbnail", {}).get("thumbnails", [])
        thumbnail_url = thumbnails[-1]["url"] if thumbnails else None

        result = {
            "videoId": song_info.get("videoId"),
            "title": song_info.get("title"),
            "artist": song_info.get("author"),
            "album": microformat.get("title"),
            "duration": song_info.get("lengthSeconds"),
            "thumbnailUrl": thumbnail_url,
            "description": microformat.get("description"),
            "viewCount": song_info.get("viewCount"),
            "publishDate": microformat.get("publishDate"),
            "availableCountries": microformat.get("availableCountries", [])
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
