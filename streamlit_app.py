"""
AI Virtual Gym Trainer - Web Demo
Streamlit-based web application for investor presentations.

Features:
- Real-time pose detection with MediaPipe
- Form analysis for 7 exercises
- Rep/hold tracking with visual feedback
- CSV/JSON data export
- Polished investor-grade UI
- Browser-based (no local install needed for viewers)
"""

import streamlit as st
import cv2
import mediapipe as mp
import numpy as np
from PIL import Image
import time
import json
import csv
import os
from datetime import datetime
import base64
from io import BytesIO

# Page configuration
st.set_page_config(
    page_title="AI Virtual Gym Trainer",
    page_icon="💪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for polished investor-grade UI
st.markdown("""
    <style>
    :root {
        --primary: #1a1a2e;
        --secondary: #16213e;
        --accent: #e94560;
        --accent-light: #f47c6f;
        --success: #07b38c;
        --warning: #f6ae2d;
        --text: #f1f1f1;
        --muted: #7d7d84;
        --card: #2a2a3a;
    }

    .main {
        background: var(--primary);
    }

    .stButton > button {
        background: var(--accent);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: 600;
        transition: all 0.2s;
    }

    .stButton > button:hover {
        background: var(--accent-light);
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(233, 69, 96, 0.3);
    }

    .stSelectbox > div > div > div {
        background: var(--card);
        color: var(--text);
    }

    .stSlider > div > div > div > div {
        background: var(--accent);
    }

    .stExpander {
        background: var(--card);
        border: 1px solid var(--muted);
        border-radius: 8px;
    }

    .stExpander > summary {
        color: var(--text);
        font-weight: 500;
    }

    .metric-card {
        background: var(--secondary);
        border: 1px solid var(--muted);
        border-radius: 10px;
        padding: 1rem;
        text-align: center;
        margin: 0.5rem 0;
    }

    .feedback-good {
        color: var(--success) !important;
        font-weight: 600;
    }

    .feedback-warning {
        color: var(--warning) !important;
        font-weight: 600;
    }

    .feedback-bad {
        color: var(--accent) !important;
        font-weight: 600;
    }

    h1, h2, h3 {
        color: var(--text) !important;
    }

    .stProgress > div > div > div > div {
        background: var(--accent);
    }

    .logo-text {
        font-size: 1.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, var(--accent), var(--accent-light));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'app_state' not in st.session_state:
    st.session_state.app_state = {
        'exercise': None,
        'cap': None,
        'pose': None,
        'start_time': 0,
        'stage': 'up',
        'reps': 0,
        'min_angle': 180,
        'max_angle': 0,
        'hold_seconds': 0,
        'last_tick': 0,
        'feedback': 'Step into frame',
        'feedback_color': '#f6ae2d',
        'data_log': [],
        'export_format': 'CSV',
        'running': False
    }

if 'exercises' not in st.session_state:
    st.session_state.exercises = {
        "Squat": {
            "type": "reps", "camera_hint": "Face the camera",
            "targets": ["Legs & Glutes"],
            "description": "A lower-body exercise that builds leg and glute strength.",
            "steps": [
                "Stand with feet shoulder-width apart, toes slightly out.",
                "Keep your chest up and back straight.",
                "Bend your knees and push your hips back, as if sitting into a chair.",
                "Lower until your thighs are at least parallel to the floor.",
                "Keep knees tracking over your toes, not caving inward.",
                "Push through your heels to stand back up.",
            ],
        },
        "Push-up": {
            "type": "reps", "camera_hint": "Film from the side",
            "targets": ["Arms & Chest"],
            "description": "An upper-body exercise that works the chest, shoulders, and triceps.",
            "steps": [
                "Start in a plank position, hands slightly wider than shoulders.",
                "Keep your body in one straight line from shoulders to ankles.",
                "Lower your chest toward the floor by bending your elbows.",
                "Keep elbows at roughly a 45-degree angle from your body.",
                "Go down until your chest is close to the floor.",
                "Push back up to full arm extension without letting hips sag.",
            ],
        },
        "Plank": {
            "type": "hold", "camera_hint": "Film from the side",
            "targets": ["Core"],
            "description": "A core-strengthening hold that trains stability.",
            "steps": [
                "Get into a forearm or high-plank position.",
                "Keep your body in a straight line from shoulders to ankles.",
                "Engage your core - don't let your hips drop or pike up.",
                "Keep your neck neutral, eyes toward the floor.",
                "Hold the position while breathing steadily.",
            ],
        },
        "Lunge": {
            "type": "reps", "camera_hint": "Film from the side",
            "targets": ["Legs & Glutes"],
            "description": "A single-leg exercise that builds strength and balance.",
            "steps": [
                "Stand tall with feet hip-width apart.",
                "Step forward with one leg.",
                "Lower your hips until both knees are bent around 90 degrees.",
                "Keep your front knee above your ankle, not past your toes.",
                "Keep your torso upright throughout the movement.",
                "Push through your front heel to return to standing.",
            ],
        },
        "Sit-up": {
            "type": "reps", "camera_hint": "Face the camera",
            "targets": ["Core"],
            "description": "A core exercise that targets your abdominal muscles.",
            "steps": [
                "Lie on your back with knees bent, feet flat on the floor.",
                "Cross your arms over your chest or place hands lightly behind your head.",
                "Engage your abs and curl your torso up toward your knees.",
                "Curl up as high as you comfortably can.",
                "Lower back down with control - don't just drop.",
            ],
        },
        "Jumping Jack": {
            "type": "reps", "camera_hint": "Face the camera",
            "targets": ["Full Body / Cardio"],
            "description": "A full-body cardio exercise that raises your heart rate.",
            "steps": [
                "Start standing with feet together, arms at your sides.",
                "Jump your feet out wide while raising your arms overhead.",
                "Jump back to the starting position, feet together, arms down.",
                "Keep a steady, quick rhythm.",
                "Land softly on the balls of your feet.",
            ],
        },
        "Glute Bridge": {
            "type": "reps", "camera_hint": "Film from the side",
            "targets": ["Legs & Glutes"],
            "description": "A lower-body exercise that isolates and strengthens the glutes.",
            "steps": [
                "Lie on your back, knees bent, feet flat on the floor.",
                "Keep feet hip-width apart, arms flat at your sides.",
                "Push through your heels and lift your hips toward the ceiling.",
                "Squeeze your glutes at the top of the movement.",
                "Form a straight line from shoulders to knees at the top.",
                "Lower back down with control.",
            ],
        },
    }


def calculate_angle(a, b, c):
    """Angle at point b, formed by points a-b-c (each an (x, y) pair)."""
    a, b, c = np.array(a), np.array(b), np.array(c)
    radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
    angle = np.abs(radians * 180.0 / np.pi)
    if angle > 180.0:
        angle = 360 - angle
    return angle


def get_points(landmarks, w, h):
    """Pull out all the body points we need, in pixel coordinates."""
    def p(landmark):
        lm = landmarks[landmark.value]
        return [lm.x * w, lm.y * h]

    import mediapipe as mp_pose
    L = mp_pose.PoseLandmark
    return {
        "l_shoulder": p(L.LEFT_SHOULDER), "r_shoulder": p(L.RIGHT_SHOULDER),
        "l_hip": p(L.LEFT_HIP), "r_hip": p(L.RIGHT_HIP),
        "l_knee": p(L.LEFT_KNEE), "r_knee": p(L.RIGHT_KNEE),
        "l_ankle": p(L.LEFT_ANKLE), "r_ankle": p(L.RIGHT_ANKLE),
        "l_elbow": p(L.LEFT_ELBOW), "r_elbow": p(L.RIGHT_ELBOW),
        "l_wrist": p(L.LEFT_WRIST), "r_wrist": p(L.RIGHT_WRIST),
    }


def analyze_squat(pts, state):
    angle = calculate_angle(pts["l_hip"], pts["l_knee"], pts["l_ankle"])
    state["min_angle"] = min(state.get("min_angle", 180), angle)

    knee_dist = abs(pts["l_knee"][0] - pts["r_knee"][0])
    ankle_dist = abs(pts["l_ankle"][0] - pts["r_ankle"][0])
    knees_caving = ankle_dist > 0 and knee_dist < ankle_dist * 0.8

    text, color = "Standing — start your squat", "#a0a0c0"

    if state["stage"] == "up" and angle < 140:
        state["stage"] = "down"
    elif state["stage"] == "down" and angle > 160:
        if state["min_angle"] <= 100:
            state["reps"] += 1
            text, color = "Good depth! Rep counted.", "#8fdc8f"
        else:
            text, color = "Too shallow — go lower next time", "#ff6b6b"
        state["stage"] = "up"
        state["min_angle"] = 180

    if state["stage"] == "down":
        if knees_caving:
            text, color = "Knees caving in — push knees out", "#ff6b6b"
        elif angle > 100:
            text, color = "Keep going lower...", "#ffcc66"
        else:
            text, color = "Good depth — now stand back up", "#8fdc8f"

    return text, color


def analyze_pushup(pts, state):
    elbow_angle = calculate_angle(pts["l_shoulder"], pts["l_elbow"], pts["l_wrist"])
    back_angle = calculate_angle(pts["l_shoulder"], pts["l_hip"], pts["l_ankle"])
    state["min_angle"] = min(state.get("min_angle", 180), elbow_angle)

    text, color = "Arms extended — start your push-up", "#a0a0c0"
    back_sagging = back_angle < 160

    if state["stage"] == "up" and elbow_angle < 140:
        state["stage"] = "down"
    elif state["stage"] == "down" and elbow_angle > 155:
        if state["min_angle"] <= 95:
            state["reps"] += 1
            text, color = "Good rep! Chest went low enough.", "#8fdc8f"
        else:
            text, color = "Go lower — chest closer to the ground", "#ff6b6b"
        state["stage"] = "up"
        state["min_angle"] = 180

    if state["stage"] == "down":
        if back_sagging:
            text, color = "Hips sagging — tighten your core", "#ff6b6b"
        elif elbow_angle > 95:
            text, color = "Lower your chest...", "#ffcc66"
        else:
            text, color = "Good depth — push back up", "#8fdc8f"

    return text, color


def analyze_lunge(pts, state):
    l_angle = calculate_angle(pts["l_hip"], pts["l_knee"], pts["l_ankle"])
    r_angle = calculate_angle(pts["r_hip"], pts["r_knee"], pts["r_ankle"])
    front_angle = min(l_angle, r_angle)
    front_knee = pts["l_knee"] if l_angle < r_angle else pts["r_knee"]
    front_ankle = pts["l_ankle"] if l_angle < r_angle else pts["r_ankle"]
    knee_past_toes = front_knee[0] > front_ankle[0] + 25

    state["min_angle"] = min(state.get("min_angle", 180), front_angle)

    text, color = "Standing — step into your lunge", "#a0a0c0"

    if state["stage"] == "up" and front_angle < 140:
        state["stage"] = "down"
    elif state["stage"] == "down" and front_angle > 160:
        if state["min_angle"] <= 100:
            state["reps"] += 1
            text, color = "Good depth! Rep counted.", "#8fdc8f"
        else:
            text, color = "Go deeper — front thigh closer to parallel", "#ff6b6b"
        state["stage"] = "up"
        state["min_angle"] = 180

    if state["stage"] == "down":
        if knee_past_toes:
            text, color = "Front knee past your toes — shift weight back", "#ff6b6b"
        elif front_angle > 100:
            text, color = "Lower into the lunge...", "#ffcc66"
        else:
            text, color = "Good depth — push back up", "#8fdc8f"

    return text, color


def analyze_situp(pts, state):
    torso_angle = calculate_angle(pts["l_shoulder"], pts["l_hip"], pts["l_knee"])
    state["min_angle"] = min(state.get("min_angle", 180), torso_angle)

    text, color = "Lying down — start your sit-up", "#a0a0c0"

    if state["stage"] == "up" and torso_angle < 120:
        state["stage"] = "down"
    elif state["stage"] == "down" and torso_angle > 150:
        if state["min_angle"] <= 90:
            state["reps"] += 1
            text, color = "Good rep! Curled up all the way.", "#8fdc8f"
        else:
            text, color = "Curl up higher next time", "#ff6b6b"
        state["stage"] = "up"
        state["min_angle"] = 180

    if state["stage"] == "down":
        if torso_angle > 90:
            text, color = "Keep curling up...", "#ffcc66"
        else:
            text, color = "Good height — lower back down slowly", "#8fdc8f"

    return text, color


def analyze_jumping_jack(pts, state):
    wrists_up = pts["l_wrist"][1] < pts["l_shoulder"][1] and pts["r_wrist"][1] < pts["r_shoulder"][1]
    ankle_dist = abs(pts["l_ankle"][0] - pts["r_ankle"][0])
    hip_dist = abs(pts["l_hip"][0] - pts["r_hip"][0])
    legs_spread = hip_dist > 0 and ankle_dist > hip_dist * 1.6
    is_open = wrists_up and legs_spread

    text, color = "Closed position — jump to open", "#a0a0c0"

    if state["stage"] == "closed" and is_open:
        state["stage"] = "open"
    elif state["stage"] == "open" and not is_open:
        state["reps"] += 1
        state["stage"] = "closed"
        text, color = "Rep counted!", "#8fdc8f"

    if state["stage"] == "open":
        if not wrists_up:
            text, color = "Raise your arms higher", "#ff6b6b"
        elif not legs_spread:
            text, color = "Spread your legs wider", "#ff6b6b"
        else:
            text, color = "Good! Jump back to closed", "#8fdc8f"

    return text, color


def analyze_glute_bridge(pts, state):
    hip_angle = calculate_angle(pts["l_shoulder"], pts["l_hip"], pts["l_knee"])
    state["max_angle"] = max(state.get("max_angle", 0), hip_angle)

    text, color = "Lying down — lift your hips", "#a0a0c0"

    if state["stage"] == "down" and hip_angle > 155:
        state["stage"] = "up"
    elif state["stage"] == "up" and hip_angle < 140:
        if state["max_angle"] >= 165:
            state["reps"] += 1
            text, color = "Good lift! Rep counted.", "#8fdc8f"
        else:
            text, color = "Lift your hips higher next time", "#ff6b6b"
        state["stage"] = "down"
        state["max_angle"] = 0

    if state["stage"] == "up":
        if hip_angle < 165:
            text, color = "Lift a bit higher...", "#ffcc66"
        else:
            text, color = "Great hip extension — hold, then lower", "#8fdc8f"

    return text, color


def analyze_plank(pts, state):
    body_angle = calculate_angle(pts["l_shoulder"], pts["l_hip"], pts["l_ankle"])
    now = time.time()
    last = state.get("last_tick", now)
    dt = now - last
    state["last_tick"] = now

    good_form = 165 <= body_angle <= 185

    if good_form:
        state["hold_seconds"] = state.get("hold_seconds", 0) + dt
        if body_angle > 178:
            text, color = f"Great form! Holding: {int(state['hold_seconds'])}s", "#8fdc8f"
        else:
            text, color = f"Good — keep it straight. Holding: {int(state['hold_seconds'])}s", "#8fdc8f"
    else:
        if body_angle < 165:
            text, color = "Hips sagging — lift them up", "#ff6b6b"
        else:
            text, color = "Hips too high — lower them", "#ff6b6b"
        color = "#ff6b6b"

    return text, color


def export_data(state, exercise_name, export_format):
    """Export data as CSV or JSON."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    data_point = {
        "timestamp": timestamp,
        "exercise": exercise_name,
        "reps": state.get("reps", 0),
        "hold_seconds": state.get("hold_seconds", 0),
        "min_angle": state.get("min_angle", 180),
        "max_angle": state.get("max_angle", 0),
        "stage": state.get("stage", "up"),
        "feedback": state.get("feedback", ""),
    }

    if export_format == "CSV":
        output = []
        output.append(",".join(["timestamp", "exercise", "reps", "hold_seconds", "min_angle", "max_angle", "stage", "feedback"]))
        output.append(",".join([str(data_point["timestamp"]), data_point["exercise"], str(data_point["reps"]),
                        str(data_point["hold_seconds"]), str(data_point["min_angle"]), str(data_point["max_angle"]),
                        data_point["stage"], data_point["feedback"]]))
        return "\n".join(output)
    else:  # JSON
        data_point["id"] = len(st.session_state.get("export_history", []))
        history = st.session_state.get("export_history", [])
        history.append(data_point)
        st.session_state.export_history = history
        return json.dumps(data_point, indent=2)


def main():
    # Header
    st.markdown("""
        <div style="text-align: center; padding: 2rem 0;">
            <div class="logo-text">AI Virtual Gym Trainer</div>
            <div style="color: var(--muted); font-size: 0.9rem; margin-top: 0.5rem;">Pose Detection • Form Feedback • Performance Tracking</div>
        </div>
    """, unsafe_allow_html=True)

    # Sidebar
    with st.sidebar:
        st.markdown("### 🎛️ Control Panel")

        # Exercise selection
        exercise_names = list(st.session_state.exercises.keys())
        selected_exercise = st.selectbox(
            "Select Exercise",
            exercise_names,
            index=0 if st.session_state.app_state['exercise'] is None else
                exercise_names.index(st.session_state.app_state['exercise'])
        )

        if selected_exercise != st.session_state.app_state['exercise']:
            st.session_state.app_state['exercise'] = selected_exercise
            st.session_state.app_state = {
                **st.session_state.app_state,
                'stage': "up" if st.session_state.exercises[selected_exercise]["type"] == "reps" else "down",
                'reps': 0,
                'min_angle': 180,
                'max_angle': 0,
                'hold_seconds': 0,
                'last_tick': time.time(),
                'feedback': "Get in position...",
                'feedback_color': '#f6ae2d',
                'data_log': [],
            }

        st.markdown("---")
        st.markdown("### 📊 Exercise Stats")

        config = st.session_state.exercises[selected_exercise]
        exercise_type = config["type"]

        # Metric cards
        col1, col2 = st.columns(2)

        with col1:
            if exercise_type == "reps":
                st.markdown(f"""
                    <div class="metric-card">
                        <div>Reps Completed</div>
                        <div style="font-size: 2rem; font-weight: 700; color: var(--accent);">{st.session_state.app_state['reps']}</div>
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                    <div class="metric-card">
                        <div>Hold Time</div>
                        <div style="font-size: 2rem; font-weight: 700; color: var(--accent);">{int(st.session_state.app_state['hold_seconds'])}s</div>
                    </div>
                """, unsafe_allow_html=True)

        with col2:
            st.markdown(f"""
                <div class="metric-card">
                    <div>Min Angle</div>
                    <div style="font-size: 1rem; color: var(--muted);">{st.session_state.app_state['min_angle']}°</div>
                </div>
            """, unsafe_allow_html=True)

            st.markdown(f"""
                <div class="metric-card">
                    <div>Max Angle</div>
                    <div style="font-size: 1rem; color: var(--muted);">{st.session_state.app_state['max_angle']}°</div>
                </div>
            """, unsafe_allow_html=True)

        st.markdown("---")

        # Data export section
        st.markdown("### 📥 Data Export")
        export_format = st.radio("Format", ["CSV", "JSON"], horizontal=True)
        st.session_state.app_state['export_format'] = export_format

        if st.button("📥 Export Last Session", type="secondary"):
            exported_data = export_data(
                st.session_state.app_state,
                selected_exercise,
                export_format
            )
            st.download_button(
                label=f"Download {export_format}",
                data=exported_data,
                file_name=f"gym_data_{selected_exercise.lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{export_format.lower()}",
                mime="text/csv" if export_format == "CSV" else "application/json",
            )

        st.markdown("---")
        st.markdown("### ℹ️ About")
        st.info(config["description"])

    # Main area - Camera feed and feedback
    col_left, col_right = [st.columns([2, 1])[0], st.columns([2, 1][1] if False else 1)[0]]

    with col_left:
        st.markdown("### 📹 Live Camera Feed")
        video_placeholder = st.empty()

    with col_right:
        st.markdown("### 💡 Form Feedback")
        feedback_placeholder = st.empty()

        # Feedback color indicator
        feedback_color = st.session_state.app_state['feedback_color']
        st.markdown(f"""
            <div style="
                background: {feedback_color};
                color: white;
                padding: 0.75rem;
                border-radius: 8px;
                margin: 0.5rem 0;
                font-weight: 600;
                text-align: center;
            ">
                {st.session_state.app_state['feedback']}
            </div>
        """, unsafe_allow_html=True)

        # Rep/hold counter
        if exercise_type == "reps":
            counter_placeholder = st.empty()
            counter_placeholder.markdown(f"""
                <div style="font-size: 1.5rem; font-weight: 700; color: var(--success); margin: 1rem 0;">
                    Reps: {st.session_state.app_state['reps']}
                </div>
            """, unsafe_allow_html=True)
        else:
            counter_placeholder = st.empty()
            counter_placeholder.markdown(f"""
                <div style="font-size: 1.5rem; font-weight: 700; color: var(--success); margin: 1rem 0;">
                    Time: {int(st.session_state.app_state['hold_seconds'])}s
                </div>
            """, unsafe_allow_html=True)

        # Camera hint
        st.caption(f"📷 Camera hint: {config['camera_hint']}")

    # Control buttons
    col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])

    with col_btn1:
        if not st.session_state.app_state['running']:
            if st.button("▶️ Start Monitoring", type="primary", use_container_width=True):
                st.session_state.app_state['running'] = True
                st.session_state.app_state['cap'] = cv2.VideoCapture(0)
                st.session_state.app_state['pose'] = mp.solutions.pose(
                    min_detection_confidence=0.5, min_tracking_confidence=0.5
                )
                st.session_state.app_state['start_time'] = time.time()
                st.rerun()

    with col_btn2:
        if st.session_state.app_state['running']:
            if st.button("⏸️ Pause", use_container_width=True):
                st.session_state.app_state['running'] = False
                if st.session_state.app_state['cap']:
                    st.session_state.app_state['cap'].release()
                    st.session_state.app_state['cap'] = None
                if st.session_state.app_state['pose']:
                    st.session_state.app_state['pose'].close()
                    st.session_state.app_state['pose'] = None
                st.rerun()

    with col_btn3:
        if st.session_state.app_state['running']:
            if st.button("⏹️ Stop", use_container_width=True, type="secondary"):
                st.session_state.app_state['running'] = False
                if st.session_state.app_state['cap']:
                    st.session_state.app_state['cap'].release()
                    st.session_state.app_state['cap'] = None
                if st.session_state.app_state['pose']:
                    st.session_state.app_state['pose'].close()
                    st.session_state.app_state['pose'] = None
                st.rerun()

    # Video loop
    if st.session_state.app_state['running'] and st.session_state.app_state['cap']:
        ret, frame = st.session_state.app_state['cap'].read()
        if ret:
            frame = cv2.flip(frame, 1)
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = st.session_state.app_state['pose'].process(rgb)

            current_exercise = st.session_state.app_state['exercise']
            config = st.session_state.exercises[current_exercise]
            feedback_text = "No person detected — step into frame"
            feedback_color = "#f6ae2d"

            if results.pose_landmarks:
                import mediapipe as mp_drawing
                mp_drawing.draw_landmarks(
                    frame, results.pose_landmarks, mp.solutions.pose.POSE_CONNECTIONS
                )
                h, w, _ = frame.shape
                pts = get_points(results.pose_landmarks.landmark, w, h)

                feedback_text, feedback_color = config["analyzer"](pts, st.session_state.app_state)

                if config["type"] == "hold":
                    st.session_state.app_state['hold_seconds'] = int(
                        st.session_state.app_state.get('hold_seconds', 0) +
                        (time.time() - st.session_state.app_state.get('last_tick', time.time()))
                    )
                    counter_text = f"Time: {st.session_state.app_state['hold_seconds']}s"
                else:
                    counter_text = f"Reps: {st.session_state.app_state['reps']}"

                # Update rep/hold display
                if config["type"] == "reps":
                    st.session_state.app_state['reps'] = st.session_state.app_state.get('reps', 0)

            # Convert frame for Streamlit
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame_pil = Image.fromarray(frame_rgb)
            frame_resized = frame_pil.resize((560, 420))
            img_buffer = BytesIO()
            frame_resized.save(img_buffer, format="PNG")
            img_base64 = base64.b64encode(img_buffer.getvalue()).decode()

            # Update displays
            video_placeholder.image(
                img_base64,
                channels="BGR",
                use_container_width=False,
                width=560,
                caption=f"🟢 {current_exercise} - Form Analysis Active"
            )

            # Feedback display
            feedback_color_class = {
                "#8fdc8f": "feedback-good",
                "#ffcc66": "feedback-warning",
                "#ff6b6b": "feedback-bad",
                "#f6ae2d": "feedback-warning",
            }.get(feedback_color, "feedback-warning")

            st.markdown(f"""
                <div class="feedback-{feedback_color.replace('#', '')}">
                    {feedback_text}
                </div>
            """, unsafe_allow_html=True)

    # Footer
    st.markdown("""
        <div style="margin-top: 2rem; padding: 1rem; color: var(--muted); text-align: center; font-size: 0.8rem;">
            AI Virtual Gym Trainer • Investor Presentation Demo • November 2026
        </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()