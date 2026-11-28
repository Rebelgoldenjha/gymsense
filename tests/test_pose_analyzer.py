"""
Unit tests for gymsense core modules (pose_analyzer, export_service, config, webrtc_processor).
Compatible with both `pytest` and direct execution (`python tests/test_pose_analyzer.py`).
"""

import json
import time

from gymsense.config import CONFIG
from gymsense.export_service import build_session_entry, serialize_sessions
from gymsense.pose_analyzer import (
    analyze_glute_bridge,
    analyze_jumping_jack,
    analyze_lunge,
    analyze_plank,
    analyze_pushup,
    analyze_situp,
    analyze_squat,
    calculate_angle,
)


def _base_pts(w=640, h=480, vis=1.0):
    return {
        "l_shoulder": [w * 0.4, h * 0.3, vis], "r_shoulder": [w * 0.6, h * 0.3, vis],
        "l_elbow": [w * 0.3, h * 0.4, vis], "r_elbow": [w * 0.7, h * 0.4, vis],
        "l_wrist": [w * 0.2, h * 0.5, vis], "r_wrist": [w * 0.8, h * 0.5, vis],
        "l_hip": [w * 0.4, h * 0.5, vis], "r_hip": [w * 0.6, h * 0.5, vis],
        "l_knee": [w * 0.35, h * 0.7, vis], "r_knee": [w * 0.65, h * 0.7, vis],
        "l_ankle": [w * 0.3, h * 0.9, vis], "r_ankle": [w * 0.7, h * 0.9, vis],
    }


def _feed(fn, pts, state, n=6):
    res = None
    for _ in range(n):
        res = fn(pts, state)
    return res


def test_calculate_angle():
    assert abs(calculate_angle([0, 0], [1, 0], [2, 0]) - 180) < 0.01
    assert abs(calculate_angle([0, 1], [0, 0], [1, 0]) - 90) < 0.01
    assert abs(calculate_angle([1, 1], [0, 0], [1, 0]) - 45) < 0.01
    assert abs(calculate_angle([0, -1], [0, 0], [1, 0]) - 90) < 0.01


def test_squat_multi_rep_and_shallow():
    w, h = 640, 480
    pts = _base_pts(w, h)
    state = {"stage": "up", "reps": 0, "min_angle": 180, "max_angle": 0}

    for rep in range(1, 3):
        _feed(analyze_squat, pts, state)
        assert state["stage"] == "up"

        pts["l_knee"] = [w * 0.25, h * 0.55, 1.0]
        pts["r_knee"] = [w * 0.75, h * 0.55, 1.0]
        pts["l_ankle"] = [w * 0.3, h * 0.85, 1.0]
        pts["r_ankle"] = [w * 0.7, h * 0.85, 1.0]
        _feed(analyze_squat, pts, state)
        assert state["stage"] == "down"

        pts["l_knee"] = [w * 0.35, h * 0.7, 1.0]
        pts["r_knee"] = [w * 0.65, h * 0.7, 1.0]
        pts["l_ankle"] = [w * 0.3, h * 0.9, 1.0]
        pts["r_ankle"] = [w * 0.7, h * 0.9, 1.0]
        _feed(analyze_squat, pts, state)
        assert state["reps"] == rep
        assert state["stage"] == "up"

    pts["l_knee"] = [w * 0.28, h * 0.63, 1.0]
    pts["r_knee"] = [w * 0.72, h * 0.63, 1.0]
    _feed(analyze_squat, pts, state)
    assert state["stage"] == "down"

    pts["l_knee"] = [w * 0.35, h * 0.7, 1.0]
    pts["r_knee"] = [w * 0.65, h * 0.7, 1.0]
    _feed(analyze_squat, pts, state)
    assert state["reps"] == 2
    assert state["stage"] == "up"


def test_bilateral_and_visibility_gating():
    w, h = 640, 480
    pts = _base_pts(w, h, vis=0.95)
    for k in ("l_hip", "l_knee", "l_ankle"):
        pts[k][2] = 0.1

    state = {"stage": "up", "reps": 0, "min_angle": 180, "max_angle": 0}
    _feed(analyze_squat, pts, state)
    pts["r_knee"] = [w * 0.75, h * 0.55, 0.95]
    pts["r_ankle"] = [w * 0.7, h * 0.85, 0.95]
    _feed(analyze_squat, pts, state)
    assert state["stage"] == "down"

    pts["r_knee"] = [w * 0.65, h * 0.7, 0.95]
    pts["r_ankle"] = [w * 0.7, h * 0.9, 0.95]
    _feed(analyze_squat, pts, state)
    assert state["reps"] == 1

    for k in pts:
        pts[k][2] = 0.1
    text, _ = analyze_squat(pts, state)
    assert "visible" in text.lower()


def test_pushup_multi_rep():
    w, h = 640, 480
    pts = _base_pts(w, h)
    state = {"stage": "up", "reps": 0, "min_angle": 180, "max_angle": 0}

    for rep in range(1, 3):
        pts["l_elbow"] = [w * 0.45, h * 0.25, 1.0]
        pts["l_wrist"] = [w * 0.5, h * 0.15, 1.0]
        _feed(analyze_pushup, pts, state)
        assert state["stage"] == "up"

        pts["l_elbow"] = [w * 0.4, h * 0.4, 1.0]
        pts["l_wrist"] = [w * 0.35, h * 0.4, 1.0]
        _feed(analyze_pushup, pts, state)
        assert state["stage"] == "down"

        pts["l_elbow"] = [w * 0.45, h * 0.25, 1.0]
        pts["l_wrist"] = [w * 0.5, h * 0.15, 1.0]
        _feed(analyze_pushup, pts, state)
        assert state["reps"] == rep
        assert state["stage"] == "up"


def test_plank_sag_and_pike():
    w, h = 640, 480
    pts = _base_pts(w, h)
    pts["l_shoulder"] = [w * 0.2, h * 0.5, 1.0]
    pts["l_hip"] = [w * 0.5, h * 0.5, 1.0]
    pts["l_ankle"] = [w * 0.8, h * 0.5, 1.0]
    state = {"stage": "down", "hold_seconds": 0.0, "last_tick": time.time() - 0.5}

    text, _ = _feed(analyze_plank, pts, state, n=4)
    assert "holding" in text.lower() or "good" in text.lower()
    assert state["hold_seconds"] > 0

    pts["l_hip"] = [w * 0.5, h * 0.7, 1.0]
    prev_hold = state["hold_seconds"]
    text, _ = _feed(analyze_plank, pts, state, n=6)
    assert "sagging" in text.lower()
    assert state["hold_seconds"] == prev_hold

    pts["l_hip"] = [w * 0.5, h * 0.3, 1.0]
    text, _ = _feed(analyze_plank, pts, state, n=8)
    assert "high" in text.lower()


def test_lunge_situp_jj_bridge():
    w, h = 640, 480
    pts = _base_pts(w, h)
    s_lunge = {"stage": "up", "reps": 0, "min_angle": 180}
    _feed(analyze_lunge, pts, s_lunge)
    pts["l_knee"] = [w * 0.25, h * 0.55, 1.0]
    pts["l_ankle"] = [w * 0.3, h * 0.85, 1.0]
    _feed(analyze_lunge, pts, s_lunge)
    pts["l_knee"] = [w * 0.35, h * 0.7, 1.0]
    pts["l_ankle"] = [w * 0.3, h * 0.9, 1.0]
    _feed(analyze_lunge, pts, s_lunge)
    assert s_lunge["reps"] == 1

    pts = _base_pts(w, h)
    pts["l_hip"] = [w * 0.45, h * 0.5, 1.0]
    pts["l_knee"] = [w * 0.5, h * 0.7, 1.0]
    s_su = {"stage": "up", "reps": 0, "min_angle": 180}
    _feed(analyze_situp, pts, s_su)
    pts["l_shoulder"] = [w * 0.4, h * 0.6, 1.0]
    _feed(analyze_situp, pts, s_su)
    pts["l_shoulder"] = [w * 0.4, h * 0.3, 1.0]
    _feed(analyze_situp, pts, s_su)
    assert s_su["reps"] == 1

    pts = _base_pts(w, h)
    pts["l_wrist"] = [w * 0.3, h * 0.4, 1.0]
    pts["r_wrist"] = [w * 0.7, h * 0.4, 1.0]
    pts["l_ankle"] = [w * 0.4, h * 0.9, 1.0]
    pts["r_ankle"] = [w * 0.6, h * 0.9, 1.0]
    s_jj = {"stage": "closed", "reps": 0}
    analyze_jumping_jack(pts, s_jj)
    pts["l_wrist"][1] = h * 0.2
    pts["r_wrist"][1] = h * 0.2
    pts["l_ankle"][0] = w * 0.2
    pts["r_ankle"][0] = w * 0.8
    analyze_jumping_jack(pts, s_jj)
    pts["l_wrist"][1] = h * 0.4
    pts["r_wrist"][1] = h * 0.4
    pts["l_ankle"][0] = w * 0.4
    pts["r_ankle"][0] = w * 0.6
    analyze_jumping_jack(pts, s_jj)
    assert s_jj["reps"] == 1

    pts = _base_pts(w, h)
    pts["l_shoulder"] = [w * 0.4, h * 0.2, 1.0]
    pts["l_hip"] = [w * 0.4, h * 0.7, 1.0]
    pts["l_knee"] = [w * 0.5, h * 0.85, 1.0]
    s_gb = {"stage": "down", "reps": 0, "max_angle": 0}
    _feed(analyze_glute_bridge, pts, s_gb)
    pts["l_hip"] = [w * 0.4, h * 0.28, 1.0]
    _feed(analyze_glute_bridge, pts, s_gb)
    pts["l_hip"] = [w * 0.4, h * 0.7, 1.0]
    _feed(analyze_glute_bridge, pts, s_gb)
    assert s_gb["reps"] == 1


def test_export_service_and_config():
    assert CONFIG.history_limit > 0
    entry = build_session_entry({
        "exercise": "Squat",
        "reps": 10,
        "hold_seconds": 0.0,
        "min_angle": 88.4,
        "max_angle": 175.0,
        "stage": "up",
        "feedback": "Excellent depth!",
        "start_time": time.time() - 30,
    })
    csv_out, mime, ext = serialize_sessions([entry], "CSV")
    assert ext == "csv" and mime == "text/csv" and "Squat" in csv_out
    json_out, jmime, jext = serialize_sessions([entry], "JSON")
    assert jext == "json" and jmime == "application/json"
    parsed = json.loads(json_out)
    assert parsed[0]["reps"] == 10


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print(f"  [PASS] {name}")
    print("ALL TESTS PASSED!")
