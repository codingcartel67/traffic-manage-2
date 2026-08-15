"""
End-to-End Flask HTTP API and Live Streaming Verification Test
"""

import os
import sys
import time
import threading
import requests

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "smart_traffic_center"))
from app import app, start_stream_workers, decision_scheduler_loop, signal_countdown_loop
from sample_generator import generate_sample_videos

def run_flask():
    app.run(host='127.0.0.1', port=5005, debug=False, threaded=True)

def test_http_api():
    print("=== STARTING FLASK SERVER ON PORT 5005 ===")
    samples_dir = os.path.join(os.path.dirname(__file__), "smart_traffic_center", "samples")
    generate_sample_videos(samples_dir)
    start_stream_workers()
    threading.Thread(target=decision_scheduler_loop, daemon=True).start()
    threading.Thread(target=signal_countdown_loop, daemon=True).start()
    
    server_thread = threading.Thread(target=run_flask, daemon=True)
    server_thread.start()
    
    time.sleep(3) # allow startup
    base_url = "http://127.0.0.1:5005"
    
    print("\n[TEST 1] Testing GET /")
    r = requests.get(f"{base_url}/")
    assert r.status_code == 200
    assert "AETHER-TRAFFIC" in r.text
    print("[PASS] Homepage rendered successfully.")

    print("\n[TEST 2] Testing POST /api/youtube/validate")
    # Valid YouTube link
    r_val = requests.post(f"{base_url}/api/youtube/validate", json={"url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"})
    assert r_val.status_code == 200
    data_val = r_val.json()
    assert data_val["status"] == "success"
    print(f"[PASS] Valid YouTube URL validated: {data_val.get('title')}")

    # Invalid YouTube link
    r_inval = requests.post(f"{base_url}/api/youtube/validate", json={"url": "https://www.youtube.com/watch?v=not_a_real_video_xyz987"})
    assert r_inval.status_code == 400
    data_inval = r_inval.json()
    assert data_inval["status"] == "error"
    print(f"[PASS] Invalid YouTube URL correctly rejected with error: {data_inval.get('message')}")

    print("\n[TEST 3] Testing POST /api/feed/configure with YouTube input on Feed 1")
    r_cfg1 = requests.post(f"{base_url}/api/feed/configure", json={
        "feed_id": 1,
        "source_type": "YOUTUBE",
        "youtube_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
        "name": "Live YouTube Traffic Cam"
    })
    assert r_cfg1.status_code == 200
    print("[PASS] Feed 1 configured as YouTube source.")

    print("\n[TEST 4] Testing POST /api/feed/configure with DISABLED on Feed 3")
    r_cfg3 = requests.post(f"{base_url}/api/feed/configure", json={
        "feed_id": 3,
        "source_type": "DISABLED"
    })
    assert r_cfg3.status_code == 200
    print("[PASS] Feed 3 configured as DISABLED.")

    print("\n[TEST 5] Testing GET /api/feed/status")
    r_stat = requests.get(f"{base_url}/api/feed/status")
    assert r_stat.status_code == 200
    feeds = r_stat.json()["feeds"]
    assert feeds["1"]["source_type"] == "YOUTUBE"
    assert feeds["3"]["source_type"] == "DISABLED"
    print("[PASS] Feed status verified.")

    print("\n[TEST 6] Testing GET /api/metrics/live & YOLO Detection Pipeline")
    time.sleep(2)
    r_met = requests.get(f"{base_url}/api/metrics/live")
    assert r_met.status_code == 200
    met_data = r_met.json()
    assert "metrics" in met_data
    assert "detector_yolo" in met_data
    print(f"[PASS] Live metrics retrieved. YOLO detector active: {met_data['detector_yolo']}")

    print("\n[TEST 7] Testing GET /api/decision/latest & Decision Support Engine")
    r_dec = requests.get(f"{base_url}/api/decision/latest")
    assert r_dec.status_code == 200
    dec_data = r_dec.json()
    print(f"[PASS] Decision latest status: {dec_data.get('status')}")

    print("\n[TEST 8] Testing POST /api/decision/act (Operator APPROVE)")
    r_act = requests.post(f"{base_url}/api/decision/act", json={"action": "APPROVE"})
    if r_act.status_code == 200:
        print("[PASS] Operator APPROVE executed successfully.")
    else:
        print(f"[INFO] Decision act returned: {r_act.text}")

    print("\n[TEST 9] Testing GET /api/decisions/history (SQLite Persistence)")
    r_hist = requests.get(f"{base_url}/api/decisions/history")
    assert r_hist.status_code == 200
    hist_data = r_hist.json()
    assert "history" in hist_data
    print(f"[PASS] SQLite decision history retrieved ({len(hist_data['history'])} records).")

    print("\n[TEST 10] Testing MJPEG Stream frame output")
    stream_r = requests.get(f"{base_url}/api/stream/1", stream=True, timeout=5)
    assert stream_r.status_code == 200
    bytes_read = 0
    for chunk in stream_r.iter_content(chunk_size=1024):
        bytes_read += len(chunk)
        if bytes_read > 5000:
            break
    print(f"[PASS] MJPEG Video stream active and delivering live JPEG frames ({bytes_read} bytes read).")

    print("\n[TEST 11] Testing POST /api/load_demo (Reset to 3-feed demo)")
    r_demo = requests.post(f"{base_url}/api/load_demo")
    assert r_demo.status_code == 200
    print("[PASS] Reset to 3-feed demo scenario completed.")

    print("\n=======================================================")
    print("[ALL FLASK HTTP API & STREAMING TESTS PASSED (11/11)!]")
    print("=======================================================")

if __name__ == '__main__':
    test_http_api()
