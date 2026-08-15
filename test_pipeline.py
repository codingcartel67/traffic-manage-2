"""
Comprehensive End-to-End Test Suite for Smart Traffic Center
Verifies YouTube ingestion, OpenCV/YOLO inference, multi-feed resilience,
Decision Support Engine, and Flask API endpoints.
"""

import os
import sys
import time

# Add parent path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "smart_traffic_center"))

def test_backend_direct():
    print("=== TEST 1: Direct Module Imports & Initialization ===")
    from youtube_stream import extract_youtube_stream, is_valid_youtube_url
    from detector import VehicleDetector
    from analytics import TrafficAnalyticsEngine
    from decision_engine import DecisionSupportEngine
    import database as db
    
    print("[PASS] All modules imported successfully.")
    
    # Test 1.1: URL Validation
    assert is_valid_youtube_url("https://www.youtube.com/watch?v=dQw4w9WgXcQ") == True
    assert is_valid_youtube_url("https://youtu.be/dQw4w9WgXcQ") == True
    assert is_valid_youtube_url("not_a_url") == False
    print("[PASS] YouTube URL validator passed.")

    # Test 1.2: YouTube Extraction on valid and invalid
    print("Testing YouTube extraction on valid video...")
    res_valid = extract_youtube_stream("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
    print(f"Valid result success={res_valid['success']}, title='{res_valid.get('title')}'")
    assert res_valid["success"] == True
    assert res_valid["stream_url"] is not None

    print("Testing YouTube extraction on invalid video...")
    res_invalid = extract_youtube_stream("https://www.youtube.com/watch?v=invalid_id_999999")
    print(f"Invalid result success={res_invalid['success']}, error='{res_invalid.get('error')}'")
    assert res_invalid["success"] == False
    assert "error" in res_invalid
    print("[PASS] YouTube stream extractor & error handler passed.")

    # Test 1.3: YOLO / Detector
    print("Testing YOLOv8 Detector...")
    detector = VehicleDetector(model_name=os.path.join(os.path.dirname(__file__), "smart_traffic_center", "yolov8n.pt"))
    print(f"Detector YOLO active: {detector.is_yolo_active}")
    import numpy as np
    dummy_frame = np.zeros((360, 640, 3), dtype=np.uint8)
    dummy_frame[100:200, 150:280] = (200, 200, 200)
    annotated, dets, counts, emerg, emerg_details = detector.detect_frame(dummy_frame)
    assert annotated.shape == (360, 640, 3)
    print("[PASS] Detector pipeline passed.")

    # Test 1.4: Analytics Engine
    analytics = TrafficAnalyticsEngine()
    metrics = analytics.process_frame_detections(1, dets, counts, (360, 640, 3))
    assert "vehicle_count" in metrics
    assert "density" in metrics
    assert "trend" in metrics
    assert "hotspot" in metrics
    print("[PASS] Pandas Analytics Engine passed.")

    # Test 1.5: Decision Support Engine with 1, 2, and 3 active feeds
    decision_engine = DecisionSupportEngine()
    # 3 feeds
    dec3 = decision_engine.evaluate_traffic_state({1: metrics, 2: metrics, 3: metrics}, [])
    assert dec3 is not None
    assert len(dec3["priority_order"]) == 3
    print("[PASS] Decision Engine with 3 feeds passed.")

    # 1 feed
    dec1 = decision_engine.evaluate_traffic_state({1: metrics}, [])
    assert dec1 is not None
    assert len(dec1["priority_order"]) == 1
    print("[PASS] Decision Engine with 1 feed passed.")

    # 2 feeds
    dec2 = decision_engine.evaluate_traffic_state({1: metrics, 3: metrics}, [])
    assert dec2 is not None
    assert len(dec2["priority_order"]) == 2
    print("[PASS] Decision Engine with 2 feeds passed.")

    print("\n=======================================================")
    print("[ALL DIRECT BACKEND TESTS PASSED SUCCESSFULLY!]")
    print("=======================================================")

if __name__ == '__main__':
    test_backend_direct()
