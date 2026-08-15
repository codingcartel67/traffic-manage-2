import yt_dlp
import cv2
import time

def extract_youtube_info(url):
    ydl_opts = {
        'format': 'best[ext=mp4][height<=720]/best[height<=720]/bestvideo[height<=720]+bestaudio/best',
        'quiet': True,
        'no_warnings': True,
        'noplaylist': True,
        'extract_flat': False,
        'socket_timeout': 10,
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            is_live = bool(info.get('is_live') or info.get('live_status') == 'is_live')
            stream_url = info.get('url')
            
            # If format is HLS (m3u8) or manifest:
            if not stream_url and 'formats' in info:
                # Find best video format
                for f in reversed(info['formats']):
                    if f.get('url') and (f.get('vcodec') != 'none' or f.get('ext') == 'mp4' or 'm3u8' in f.get('url', '')):
                        stream_url = f['url']
                        break
            
            return {
                'success': True,
                'title': info.get('title', 'YouTube Video'),
                'is_live': is_live,
                'stream_url': stream_url,
                'duration': info.get('duration')
            }
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }

if __name__ == '__main__':
    # Test invalid URL
    print("Testing invalid URL:")
    res_inv = extract_youtube_info("https://www.youtube.com/watch?v=invalid_id_12345")
    print("Invalid URL result:", res_inv)
    
    # Test valid URL
    print("\nTesting valid URL:")
    res_val = extract_youtube_info("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
    print("Valid URL result:", res_val['title'], "Success:", res_val['success'])
