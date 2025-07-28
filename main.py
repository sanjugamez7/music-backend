from flask import Flask, request, jsonify
from pytube import YouTube
from youtubesearchpython import VideosSearch
import re

app = Flask(__name__)

def extract_metadata(video):
    thumbnails = video.get('thumbnails') or video.get('thumbnail', {}).get('thumbnails')
    return {
        'id': video.get('id'),
        'title': video.get('title'),
        'artist': video.get('channel', {}).get('name') or '',
        'thumbnailUrl': thumbnails[-1]['url'] if thumbnails else '',
    }

@app.route('/search')
def search():
    query = request.args.get('q')
    if not query:
        return jsonify({'error': 'Missing query'}), 400

    try:
        results = VideosSearch(query, limit=10).result()
        songs = []

        for video in results.get('result', []):
            if video.get('type') != 'video':
                continue
            song = extract_metadata(video)
            songs.append(song)

        return jsonify(songs)
    except Exception as e:
        print(f"[ERROR] Search failed: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/metadata')
def metadata():
    video_id = request.args.get('id')
    if not video_id:
        return jsonify({'error': 'Missing video ID'}), 400

    try:
        url = f'https://www.youtube.com/watch?v={video_id}'
        yt = YouTube(url)
        return jsonify({
            'id': video_id,
            'title': yt.title,
            'artist': yt.author,
            'thumbnailUrl': yt.thumbnail_url,
            'duration': yt.length,
        })
    except Exception as e:
        print(f"[ERROR] Metadata fetch failed: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/stream')
def stream():
    video_id = request.args.get('id')
    if not video_id:
        return jsonify({'error': 'Missing video ID'}), 400

    try:
        url = f'https://www.youtube.com/watch?v={video_id}'
        yt = YouTube(url)
        audio_stream = yt.streams.filter(only_audio=True).order_by('abr').desc().first()
        return jsonify({'url': audio_stream.url})
    except Exception as e:
        print(f"[ERROR] Stream fetch failed: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
