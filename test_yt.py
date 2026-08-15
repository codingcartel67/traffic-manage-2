import yt_dlp
import cv2
import time

def extract_youtube_stream_url(youtube_url):
    ydl_opts = {
        'format': 'best[ext=mp4][height<=720]/best[height<=720]/best',
        'quiet': True,
        'no_warnings': True,
        'noplaylist': True,
        'extract_flat': False,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(youtube_url, download=False)
        # Check if live stream
        is_live = info.get('is_live', False) or info.get('live_status') == 'is_live'
        title = info.get('title', 'YouTube Stream')
        url = info.get('url')
        if not url:
            # check formats
            formats = info.get('formats', [])
            for f in reversed(formats):
                if f.get('url') and f.get('vcodec') != 'none':
                    url = f['url']
                    break
        return {
            'stream_url': url,
            'title': title,
            'is_live': is_live,
            'duration': info.get('duration')
        }

if __name__ == '__main__':
    # Test with a known public video URL
    test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
    print("Extracting...")
    res = extract_youtube_stream_url(test_url)
    print("Result:", res['title'], "is_live:", res['is_live'], "URL found:", bool(res['stream_url']))
    
    if res['stream_url']:
        print("Testing OpenCV VideoCapture on stream URL...")
        cap = cv2.VideoCapture(res['stream_url'])
        ret, frame = cap.read()
        print("Frame read success:", ret, "Frame shape:", frame.shape if ret else None)
        cap.release()
