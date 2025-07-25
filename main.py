import time
from flask import Flask, request, jsonify
from flask_cors import CORS  # ✅ Added import
from yt.stream import get_stream_url_with_proxy_rotation
from yt.metadata import get_metadata
from proxies.proxy_manager import ProxyManager

app = Flask(__name__)
CORS(app)  # ✅ Enable CORS for all routes

# Initialize ProxyManager globally
proxy_manager = ProxyManager()

# ✅ In-memory cache for stream URLs
stream_cache = {}  # Format: {video_id: {"url": ..., "timestamp": ...}}
CACHE_TTL_SECONDS = 3600  # 1 hour

@app.route("/stream", methods=["GET"])
def stream():
    video_id = request.args.get("video_id")  # expects ?video_id=...
    print(f"[DEBUG] Received video_id: {video_id}")

    if not video_id:
        return jsonify({"error": "Missing video ID"}), 400

    # ✅ Check cached URL
    cached = stream_cache.get(video_id)
    if cached:
        age = time.time() - cached["timestamp"]
        if age < CACHE_TTL_SECONDS:
            print(f"[CACHE] Using cached URL for {video_id}")
            return jsonify({"url": cached["url"]})
        else:
            print(f"[CACHE] Expired URL for {video_id}")
            del stream_cache[video_id]

    # 🔄 Fetch new URL using proxy rotation
    try:
        url = get_stream_url_with_proxy_rotation(video_id, proxy_manager)
        if not url:
            return jsonify({"error": "Could not get stream URL"}), 500

        # ✅ Cache it
        stream_cache[video_id] = {
            "url": url,
            "timestamp": time.time()
        }
        print(f"[CACHE] Cached new URL for {video_id}")
        return jsonify({"url": url})
    except Exception as e:
        print(f"[ERROR] Stream error for {video_id}: {str(e)}")
        return jsonify({"error": f"Failed to get stream URL: {str(e)}"}), 500

@app.route("/metadata", methods=["GET"])
def metadata():
    query = request.args.get("q")
    if not query:
        return jsonify({"error": "Missing query"}), 400
    try:
        data = get_metadata(query)
        return jsonify(data)
    except Exception as e:
        print(f"[ERROR] Metadata fetch failed: {str(e)}")
        return jsonify({"error": f"Failed to fetch metadata: {str(e)}"}), 500

@app.route("/favicon.ico")
def favicon():
    return '', 204  # Empty 204 response for browser favicon

if __name__ == "__main__":
    app.run(debug=True, port=5000)
