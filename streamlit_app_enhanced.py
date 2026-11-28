"""
AI Virtual Gym Trainer - Production Web App (Streamlit + WebRTC + MediaPipe)
"""

import time
import cv2
import streamlit as st
from mediapipe import Image as MpImage, ImageFormat
from streamlit_webrtc import WebRtcMode, webrtc_streamer

from gymsense.config import CONFIG, get_logger
from gymsense.constants import EXERCISES
from gymsense.export_service import build_session_entry
from gymsense.model_loader import create_pose_landmarker, draw_landmarks
from gymsense.pose_analyzer import ANALYZERS, get_points_from_landmarks, initial_stage_for
from gymsense.ui.components import (
    render_exercise_grid,
    render_feedback,
    render_header,
    render_history,
    render_instructions,
    render_sidebar,
)
from gymsense.ui.styles import inject_styles
from gymsense.webrtc_processor import PoseVideoProcessor, RTC_CONFIGURATION

logger = get_logger(__name__)

st.set_page_config(
    page_title=CONFIG.app_title,
    page_icon=CONFIG.app_icon,
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        "Get Help": CONFIG.help_url,
        "Report a bug": CONFIG.issues_url,
        "About": f"{CONFIG.app_title} - Real-time form analysis with MediaPipe",
    },
)

inject_styles()


def init_state():
    defaults = {
        "app_state": {
            "exercise": None,
            "cap": None,
            "pose": None,
            "start_time": 0,
            "stage": "up",
            "reps": 0,
            "min_angle": 180,
            "max_angle": 0,
            "current_angle": 0,
            "hold_seconds": 0.0,
            "last_tick": 0.0,
            "last_ts_ms": 0,
            "_smooth_angle": None,
            "feedback": "Select an exercise to begin",
            "feedback_color": "#888899",
            "running": False,
            "camera_error": None,
            "camera_initialized": False,
            "camera_mode": "Browser (WebRTC)",
        },
        "exercises": EXERCISES,
        "session_history": [],
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


def release_camera():
    s = st.session_state.app_state
    if s.get("cap"):
        s["cap"].release()
        s["cap"] = None
    if s.get("pose"):
        try:
            s["pose"].close()
        except Exception:
            logger.debug("Ignoring pose.close() error during cleanup", exc_info=True)
        s["pose"] = None


def reset_exercise(ex_name):
    release_camera()
    st.session_state.app_state.update({
        "exercise": ex_name,
        "cap": None,
        "pose": None,
        "start_time": time.time(),
        "stage": initial_stage_for(ex_name),
        "reps": 0,
        "min_angle": 180,
        "max_angle": 0,
        "current_angle": 0,
        "hold_seconds": 0.0,
        "last_tick": time.time(),
        "last_ts_ms": 0,
        "_smooth_angle": None,
        "feedback": "Get in position...",
        "feedback_color": "#f6ae2d",
        "running": False,
        "camera_error": None,
        "camera_initialized": False,
    })


def init_local_camera():
    try:
        if not hasattr(cv2, "VideoCapture"):
            return False, "OpenCV VideoCapture is unavailable. Install opencv-python-headless."
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            return False, "Cannot access local camera. Use 'Browser (WebRTC)' mode for cloud/browser access."
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        cap.set(cv2.CAP_PROP_FPS, 30)

        landmarker, err = create_pose_landmarker()
        if err:
            cap.release()
            return False, err
        return True, (cap, landmarker)
    except Exception as exc:
        logger.exception("Failed to initialize local camera")
        return False, f"Camera/Model error: {exc}"


def start_local_camera():
    s = st.session_state.app_state
    ok, result = init_local_camera()
    if ok:
        cap, pose = result
        s.update({
            "cap": cap,
            "pose": pose,
            "running": True,
            "start_time": time.time(),
            "last_tick": time.time(),
            "camera_error": None,
            "camera_initialized": True,
        })
        return True
    s.update({"camera_error": result, "running": False, "camera_initialized": False})
    return False


def process_local_frame():
    s = st.session_state.app_state
    cap, landmarker = s["cap"], s["pose"]
    cfg = st.session_state.exercises[s["exercise"]]

    if not cap or not cap.isOpened():
        return None, "Camera disconnected", "#e94560"

    ret, frame = cap.read()
    if not ret:
        return None, "Camera read failed", "#e94560"

    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    h, w, _ = frame.shape

    feedback, fcolor = "No person detected — step into frame", "#f6ae2d"
    mp_image = MpImage(image_format=ImageFormat.SRGB, data=rgb)
    ts_ms = max(s.get("last_ts_ms", 0) + 1, int(time.time() * 1000))
    s["last_ts_ms"] = ts_ms
    result = landmarker.detect_for_video(mp_image, ts_ms)

    if result.pose_landmarks and len(result.pose_landmarks) > 0:
        landmarks = result.pose_landmarks[0]
        draw_landmarks(frame, landmarks, w, h)
        pts = get_points_from_landmarks(landmarks, w, h)
        feedback, fcolor = ANALYZERS[s["exercise"]](pts, s)
        if s.get("current_angle"):
            cv2.putText(frame, f"Angle: {s['current_angle']:.0f} deg", (16, 36), cv2.FONT_HERSHEY_SIMPLEX, 0.85, (255, 255, 255), 2, cv2.LINE_AA)
    elif cfg["type"] == "hold":
        s["last_tick"] = time.time()

    s["feedback"] = feedback
    s["feedback_color"] = fcolor
    return cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), feedback, fcolor


def _sync_webrtc_snapshot(s, webrtc_ctx):
    if webrtc_ctx and webrtc_ctx.video_processor:
        snap = webrtc_ctx.video_processor.get_snapshot()
        s.update({
            "reps": snap["reps"],
            "hold_seconds": snap["hold_seconds"],
            "min_angle": snap["min_angle"],
            "max_angle": snap["max_angle"],
            "current_angle": snap["current_angle"],
            "stage": snap["stage"],
            "feedback": snap["feedback"],
            "feedback_color": snap["feedback_color"],
        })
        if snap.get("model_error"):
            st.error(snap["model_error"])


def render_webrtc_camera(s, cfg):
    st.markdown("### 📹 Live Camera (WebRTC)")
    st.markdown(f'<div class="camera-badge">📷 Camera: {cfg["camera_hint"]}</div>', unsafe_allow_html=True)

    webrtc_ctx = webrtc_streamer(
        key="gym-webrtc",
        mode=WebRtcMode.SENDRECV,
        rtc_configuration=RTC_CONFIGURATION,
        video_processor_factory=PoseVideoProcessor,
        media_stream_constraints={"video": True, "audio": False},
        async_processing=True,
    )
    if webrtc_ctx.video_processor:
        webrtc_ctx.video_processor.set_exercise(s["exercise"])
        _sync_webrtc_snapshot(s, webrtc_ctx)
    else:
        st.info("Click **START** above and allow browser camera access to begin live pose analysis.")
    return webrtc_ctx


def render_local_camera(s, cfg):
    st.markdown("### 📹 Live Camera (Local OpenCV)")
    st.markdown(f'<div class="camera-badge">📷 Camera: {cfg["camera_hint"]}</div>', unsafe_allow_html=True)

    if s["camera_error"]:
        st.error(f"📷 {s['camera_error']}")
        if st.button("🔄 Retry Camera", key="retry_cam"):
            s.update({"camera_error": None, "running": False, "camera_initialized": False})
            st.rerun()
        return None

    if not s["running"] and not s["camera_initialized"]:
        start_local_camera()

    video_placeholder = st.empty()
    if not (s["running"] and s["cap"] and s["pose"]):
        msg = "Camera paused — press Start Camera" if s["camera_initialized"] else "Initializing camera..."
        video_placeholder.markdown(
            f'<div class="camera-wrap" style="height:360px;display:flex;flex-direction:column;align-items:center;justify-content:center;">'
            f'<div style="font-size:4rem;margin-bottom:1rem;">📷</div>'
            f'<div style="color:var(--text-dim);font-size:1.1rem;">{msg}</div></div>',
            unsafe_allow_html=True,
        )
    return video_placeholder


def _save_session(s):
    entry = build_session_entry(s)
    st.session_state.session_history.insert(0, entry)
    st.session_state.session_history = st.session_state.session_history[: CONFIG.history_limit]


def render_controls(s, webrtc_ctx=None):
    st.markdown("---")
    if s.get("camera_mode", "Browser (WebRTC)") == "Browser (WebRTC)":
        c1, c2, c3 = st.columns(3)
        with c1:
            if st.button("🔄 Sync Stats", use_container_width=True, key="w_sync"):
                _sync_webrtc_snapshot(s, webrtc_ctx)
                st.rerun()
        with c2:
            if st.button("🔁 Reset", use_container_width=True, key="w_reset"):
                if webrtc_ctx and webrtc_ctx.video_processor:
                    webrtc_ctx.video_processor.reset_counters()
                    _sync_webrtc_snapshot(s, webrtc_ctx)
                st.rerun()
        with c3:
            if st.button("💾 Save Session", type="primary", use_container_width=True, key="w_save"):
                _sync_webrtc_snapshot(s, webrtc_ctx)
                _save_session(s)
                st.success("Session saved! Check History tab.")
        return

    c1, c2, c3 = st.columns(3)
    with c1:
        if not s["running"]:
            if st.button("▶️ Start Camera", type="primary", use_container_width=True, key="b_start"):
                if start_local_camera():
                    st.rerun()
        else:
            st.button("🟢 Camera Active", disabled=True, use_container_width=True)
    with c2:
        if s["running"]:
            if st.button("⏸️ Pause", use_container_width=True, key="b_pause"):
                s["running"] = False
                st.rerun()
        else:
            st.button("⏸️ Pause", disabled=True, use_container_width=True)
    with c3:
        if s["running"]:
            if st.button("⏹️ Stop & Save", use_container_width=True, type="secondary", key="b_stop"):
                _save_session(s)
                release_camera()
                st.success("Session saved! Check History tab.")
                st.rerun()
        else:
            st.button("⏹️ Stop", disabled=True, use_container_width=True, type="secondary")


def main():
    init_state()
    render_header()
    s = st.session_state.app_state

    if not s["exercise"]:
        render_exercise_grid(st.session_state.exercises, s["exercise"], reset_exercise)
        st.markdown("---")
        st.markdown("### ✨ Features")
        cols = st.columns(4)
        feats = [
            ("🎯", "Real-time Analysis", "33-keypoint MediaPipe pose detection"),
            ("📊", "Form Feedback", "Instant visual & text cues per rep"),
            ("📈", "Progress Tracking", "Reps, hold time, angle measurement"),
            ("📥", "Data Export", "CSV & JSON for analysis"),
        ]
        for col, (ic, title, desc) in zip(cols, feats):
            with col:
                st.markdown(
                    f'<div class="metric-card" style="text-align:center;"><div style="font-size:2.5rem;margin-bottom:.5rem;">{ic}</div>'
                    f'<div style="font-weight:600;margin-bottom:.25rem;">{title}</div>'
                    f'<div style="color:var(--text-dim);font-size:.85rem;">{desc}</div></div>',
                    unsafe_allow_html=True,
                )
        render_sidebar(s, st.session_state.exercises, st.session_state.session_history, reset_exercise, release_camera)
        return

    cfg = {**st.session_state.exercises[s["exercise"]], "exercise": s["exercise"]}
    tab1, tab2 = st.tabs(["🏋️ Workout", "📜 History"])

    video_placeholder = None
    feedback_placeholder = None
    webrtc_ctx = None
    use_webrtc = s.get("camera_mode", "Browser (WebRTC)") == "Browser (WebRTC)"

    with tab1:
        left, right = st.columns([2.2, 1], gap="large")
        with left:
            if use_webrtc:
                webrtc_ctx = render_webrtc_camera(s, cfg)
            else:
                video_placeholder = render_local_camera(s, cfg)
        with right:
            feedback_placeholder = st.empty()
            render_feedback(s, cfg, s.get("feedback", "Get in position..."), s.get("feedback_color", "#f6ae2d"), placeholder=feedback_placeholder)
            render_instructions(cfg)
            render_controls(s, webrtc_ctx=webrtc_ctx)

    with tab2:
        render_history(st.session_state.session_history)

    render_sidebar(s, st.session_state.exercises, st.session_state.session_history, reset_exercise, release_camera)

    if (not use_webrtc) and video_placeholder is not None and s.get("running") and s.get("cap") and s.get("pose"):
        while st.session_state.app_state.get("running", False):
            frame_rgb, fb, fc = process_local_frame()
            if frame_rgb is None:
                s["running"] = False
                s["camera_error"] = fb
                st.rerun()
                break
            video_placeholder.image(frame_rgb, channels="RGB", use_container_width=True, caption=f"🟢 {cfg['exercise']} - Live Analysis")
            render_feedback(s, cfg, fb, fc, placeholder=feedback_placeholder)
            time.sleep(0.03)


if __name__ == "__main__":
    main()
