"""
AI Virtual Gym Trainer - Enhanced Web Demo
Streamlit-based web application with polished UI/UX for investor presentations.

Features:
- Real-time pose detection with MediaPipe
- Form analysis for 7 exercises with detailed feedback
- Rep/hold tracking with visual progress indicators
- CSV/JSON data export with session history
- Polished investor-grade UI with animations
- Browser-based (no local install needed for viewers)
- Camera permission handling and error recovery
- Exercise instructions with visual guides
- Session history and progress tracking
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
import pandas as pd

# Page configuration
st.set_page_config(
    page_title="AI Virtual Gym Trainer",
    page_icon="💪",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/your-repo/gym-sense',
        'Report a bug': 'https://github.com/your-repo/gym-sense/issues',
        'About': "AI Virtual Gym Trainer - Real-time form analysis with MediaPipe"
    }
)

# Custom CSS for polished investor-grade UI
st.markdown("""
    <style>
    :root {
        --primary: #0f0f1a;
        --secondary: #1a1a2e;
        --tertiary: #16213e;
        --accent: #e94560;
        --accent-light: #f47c6f;
        --accent-glow: rgba(233, 69, 96, 0.4);
        --success: #07b38c;
        --success-glow: rgba(7, 179, 140, 0.4);
        --warning: #f6ae2d;
        --warning-glow: rgba(246, 174, 45, 0.4);
        --info: #4dabf7;
        --text: #f1f1f1;
        --text-muted: #7d7d84;
        --card: #1e1e2e;
        --card-hover: #25253a;
        --border: #2d2d44;
        --shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        --shadow-hover: 0 12px 40px rgba(0, 0, 0, 0.4);
        --radius: 12px;
        --transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }

    /* Global styles */
    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 2rem;
        max-width: 1400px;
    }

    .main {
        background: linear-gradient(180deg, var(--primary) 0%, var(--secondary) 100%);
    }

    /* Typography */
    h1, h2, h3, h4, h5, h6 {
        color: var(--text) !important;
        font-weight: 600;
    }

    .logo-text {
        font-size: 2rem;
        font-weight: 800;
        background: linear-gradient(135deg, var(--accent) 0%, var(--accent-light) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        letter-spacing: -0.02em;
    }

    .logo-subtext {
        color: var(--text-muted);
        font-size: 0.95rem;
        font-weight: 400;
        margin-top: 0.25rem;
    }

    /* Cards */
    .metric-card {
        background: var(--card);
        border: 1px solid var(--border);
        border-radius: var(--radius);
        padding: 1.25rem;
        text-align: center;
        transition: var(--transition);
        box-shadow: var(--shadow);
    }

    .metric-card:hover {
        border-color: var(--accent);
        box-shadow: var(--shadow-hover);
        transform: translateY(-2px);
    }

    .metric-value {
        font-size: 2.5rem;
        font-weight: 800;
        line-height: 1;
        margin: 0.5rem 0;
    }

    .metric-label {
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        color: var(--text-muted);
        font-weight: 600;
    }

    .metric-unit {
        font-size: 1rem;
        font-weight: 400;
        opacity: 0.7;
    }

    /* Exercise cards */
    .exercise-card {
        background: var(--card);
        border: 1px solid var(--border);
        border-radius: var(--radius);
        padding: 1.5rem;
        transition: var(--transition);
        cursor: pointer;
        height: 100%;
    }

    .exercise-card:hover {
        border-color: var(--accent);
        box-shadow: var(--shadow-hover);
        transform: translateY(-4px);
    }

    .exercise-card.selected {
        border-color: var(--accent);
        box-shadow: 0 0 0 2px var(--accent-glow), var(--shadow);
    }

    .exercise-icon {
        font-size: 2.5rem;
        margin-bottom: 0.75rem;
    }

    .exercise-name {
        font-size: 1.25rem;
        font-weight: 700;
        margin-bottom: 0.25rem;
    }

    .exercise-type {
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        padding: 0.25rem 0.75rem;
        border-radius: 100px;
        display: inline-block;
        font-weight: 600;
    }

    .exercise-type-reps {
        background: rgba(233, 69, 96, 0.15);
        color: var(--accent-light);
    }

    .exercise-type-hold {
        background: rgba(7, 179, 140, 0.15);
        color: var(--success);
    }

    .exercise-hint {
        font-size: 0.8rem;
        color: var(--text-muted);
        margin-top: 0.5rem;
        display: flex;
        align-items: center;
        gap: 0.35rem;
    }

    /* Feedback banner */
    .feedback-banner {
        padding: 1rem 1.5rem;
        border-radius: var(--radius);
        font-weight: 600;
        font-size: 1.1rem;
        text-align: center;
        transition: var(--transition);
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 0.75rem;
        min-height: 80px;
    }

    .feedback-good {
        background: linear-gradient(135deg, rgba(7, 179, 140, 0.15), rgba(7, 179, 140, 0.08));
        border: 1px solid var(--success);
        color: var(--success);
    }

    .feedback-warning {
        background: linear-gradient(135deg, rgba(246, 174, 45, 0.15), rgba(246, 174, 45, 0.08));
        border: 1px solid var(--warning);
        color: var(--warning);
    }

    .feedback-bad {
        background: linear-gradient(135deg, rgba(233, 69, 96, 0.15), rgba(233, 69, 96, 0.08));
        border: 1px solid var(--accent);
        color: var(--accent);
    }

    .feedback-neutral {
        background: var(--card);
        border: 1px solid var(--border);
        color: var(--text-muted);
    }

    /* Progress ring */
    .progress-ring-container {
        position: relative;
        width: 120px;
        height: 120px;
        margin: 0 auto 1rem;
    }

    .progress-ring-bg {
        fill: none;
        stroke: var(--border);
        stroke-width: 8;
    }

    .progress-ring-fill {
        fill: none;
        stroke: var(--accent);
        stroke-width: 8;
        stroke-linecap: round;
        stroke-dasharray: 283;
        stroke-dashoffset: 283;
        transform: rotate(-90deg);
        transform-origin: center;
        transition: stroke-dashoffset 0.5s ease-out;
    }

    .progress-ring-text {
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        font-size: 1.5rem;
        font-weight: 700;
        color: var(--text);
    }

    /* Camera feed */
    .camera-container {
        background: var(--card);
        border: 1px solid var(--border);
        border-radius: var(--radius);
        overflow: hidden;
        box-shadow: var(--shadow);
        position: relative;
    }

    .camera-container::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, var(--accent), var(--accent-light), var(--success));
        opacity: 0;
        transition: opacity 0.3s;
    }

    .camera-container.active::before {
        opacity: 1;
    }

    .camera-feed {
        width: 100%;
        display: block;
        border-radius: var(--radius) var(--radius) 0 0;
    }

    .camera-overlay {
        position: absolute;
        bottom: 0;
        left: 0;
        right: 0;
        padding: 1rem;
        background: linear-gradient(transparent, rgba(0,0,0,0.8));
        pointer-events: none;
    }

    .camera-status {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        font-size: 0.85rem;
        font-weight: 500;
        color: var(--text);
    }

    .status-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: var(--success);
        animation: pulse 2s infinite;
    }

    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }

    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, var(--accent) 0%, var(--accent-light) 100%);
        color: white;
        border: none;
        border-radius: var(--radius);
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        font-size: 0.95rem;
        transition: var(--transition);
        box-shadow: 0 4px 16px var(--accent-glow);
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 24px var(--accent-glow);
    }

    .stButton > button:active {
        transform: translateY(0);
    }

    .stButton > button[kind="secondary"] {
        background: var(--card);
        border: 1px solid var(--border);
        box-shadow: none;
        color: var(--text);
    }

    .stButton > button[kind="secondary"]:hover {
        background: var(--card-hover);
        border-color: var(--accent);
        box-shadow: 0 4px 16px var(--accent-glow);
    }

    /* Selectbox */
    .stSelectbox > div > div > div {
        background: var(--card);
        border: 1px solid var(--border);
        border-radius: var(--radius);
        color: var(--text);
    }

    .stSelectbox > div > div > div:focus-within {
        border-color: var(--accent);
        box-shadow: 0 0 0 3px var(--accent-glow);
    }

    /* Slider */
    .stSlider > div > div > div > div {
        background: linear-gradient(90deg, var(--accent), var(--accent-light));
    }

    .stSlider > div > div > div > div > div {
        background: var(--accent);
        border: 2px solid white;
    }

    /* Radio */
    .stRadio > div {
        gap: 1rem;
    }

    .stRadio > div > label {
        background: var(--card);
        border: 1px solid var(--border);
        border-radius: var(--radius);
        padding: 0.75rem 1.5rem;
        transition: var(--transition);
        cursor: pointer;
    }

    .stRadio > div > label:hover {
        border-color: var(--accent);
        background: var(--card-hover);
    }

    .stRadio > div > label[data-selected="true"] {
        background: linear-gradient(135deg, rgba(233, 69, 96, 0.15), rgba(233, 69, 96, 0.08));
        border-color: var(--accent);
        color: var(--accent-light);
    }

    /* Expander */
    .stExpander {
        background: var(--card);
        border: 1px solid var(--border);
        border-radius: var(--radius);
        overflow: hidden;
    }

    .stExpander > summary {
        color: var(--text);
        font-weight: 600;
        padding: 1rem 1.25rem;
    }

    .stExpander > div {
        padding: 0 1.25rem 1.25rem;
        color: var(--text-muted);
    }

    /* Progress bar */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, var(--accent), var(--accent-light));
        border-radius: 4px;
    }

    .stProgress > div > div > div {
        background: var(--border);
        border-radius: 4px;
    }

    /* Dataframe */
    .stDataFrame {
        background: var(--card);
        border: 1px solid var(--border);
        border-radius: var(--radius);
        overflow: hidden;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0.5rem;
        background: transparent;
    }

    .stTabs [data-baseweb="tab"] {
        background: var(--card);
        border: 1px solid var(--border);
        border-radius: var(--radius);
        color: var(--text-muted);
        font-weight: 500;
        padding: 0.75rem 1.5rem;
        transition: var(--transition);
    }

    .stTabs [data-baseweb="tab"]:hover {
        border-color: var(--accent);
        color: var(--text);
    }

    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        background: linear-gradient(135deg, var(--accent), var(--accent-light));
        border-color: transparent;
        color: white;
    }

    /* Sidebar */
    .css-1d391kg {
        background: var(--secondary);
    }

    .sidebar .stMarkdown {
        color: var(--text);
    }

    /* Download button */
    .stDownloadButton > button {
        background: var(--card);
        border: 1px solid var(--border);
        color: var(--text);
    }

    .stDownloadButton > button:hover {
        background: var(--card-hover);
        border-color: var(--success);
        color: var(--success);
    }

    /* Animations */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }

    @keyframes slideIn {
        from { opacity: 0; transform: translateX(-20px); }
        to { opacity: 1; transform: translateX(0); }
    }

    .animate-fade-in {
        animation: fadeIn 0.5s ease-out forwards;
    }

    .animate-slide-in {
        animation: slideIn 0.5s ease-out forwards;
    }

    /* Responsive */
    @media (max-width: 768px) {
        .logo-text { font-size: 1.5rem; }
        .metric-value { font-size: 2rem; }
        .exercise-icon { font-size: 2rem; }
    }

    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }

    ::-webkit-scrollbar-track {
        background: var(--primary);
    }

    ::-webkit-scrollbar-thumb {
        background: var(--border);
        border-radius: 4px;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: var(--accent);
    }

    /* Toast notifications */
    .toast {
        position: fixed;
        bottom: 2rem;
        right: 2rem;
        background: var(--card);
        border: 1px solid var(--border);
        border-radius: var(--radius);
        padding: 1rem 1.5rem;
        box-shadow: var(--shadow-hover);
        z-index: 1000;
        animation: slideIn 0.3s ease-out;
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }

    .toast.success { border-color: var(--success); }
    .toast.error { border-color: var(--accent); }
    .toast.info { border-color: var(--info); }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
def init_session_state():
    """Initialize all session state variables."""
    defaults = {
        'app_state': {
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
            'feedback': 'Select an exercise to begin',
            'feedback_color': '#7d7d84',
            'data_log': [],
            'export_format': 'CSV',
            'running': False,
            'camera_error': None,
        },
        'exercises': {
            "Squat": {
                "type": "reps", "camera_hint": "Face the camera straight-on",
                "icon": "🏋️",
                "targets": ["Legs & Glutes"],
                "description": "A fundamental lower-body exercise that builds leg and glute strength.",
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
                "type": "reps", "camera_hint": "Film from the side profile",
                "icon": "💪",
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
                "type": "hold", "camera_hint": "Film from the side profile",
                "icon": "🧘",
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
                "type": "reps", "camera_hint": "Film from the side profile",
                "icon": "🦵",
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
                "type": "reps", "camera_hint": "Face the camera straight-on",
                "icon": "🏋️‍♀️",
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
                "type": "reps", "camera_hint": "Face the camera straight-on",
                "icon": "🤸",
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
                "type": "reps", "camera_hint": "Film from the side profile",
                "icon": "🍑",
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
        },
        'session_history': [],
        'show_instructions': False,
        'selected_exercise_card': None,
        'last_export_time': None,
    }

    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

init_session_state()

# Analyzer functions
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

    text, color = "Standing — start your squat", "#7d7d84"

    if state["stage"] == "up" and angle < 140:
        state["stage"] = "down"
    elif state["stage"] == "down" and angle > 160:
        if state["min_angle"] <= 100:
            state["reps"] += 1
            text, color = "Excellent depth! Rep counted.", "#07b38c"
        else:
            text, color = "Too shallow — go lower next time", "#e94560"
        state["stage"] = "up"
        state["min_angle"] = 180

    if state["stage"] == "down":
        if knees_caving:
            text, color = "Knees caving in — push knees out", "#e94560"
        elif angle > 100:
            text, color = "Keep going lower...", "#f6ae2d"
        else:
            text, color = "Good depth — now stand back up", "#07b38c"

    return text, color


def analyze_pushup(pts, state):
    elbow_angle = calculate_angle(pts["l_shoulder"], pts["l_elbow"], pts["l_wrist"])
    back_angle = calculate_angle(pts["l_shoulder"], pts["l_hip"], pts["l_ankle"])
    state["min_angle"] = min(state.get("min_angle", 180), elbow_angle)

    text, color = "Arms extended — start your push-up", "#7d7d84"
    back_sagging = back_angle < 160

    if state["stage"] == "up" and elbow_angle < 140:
        state["stage"] = "down"
    elif state["stage"] == "down" and elbow_angle > 155:
        if state["min_angle"] <= 95:
            state["reps"] += 1
            text, color = "Perfect rep! Chest went low enough.", "#07b38c"
        else:
            text, color = "Go lower — chest closer to the ground", "#e94560"
        state["stage"] = "up"
        state["min_angle"] = 180

    if state["stage"] == "down":
        if back_sagging:
            text, color = "Hips sagging — tighten your core", "#e94560"
        elif elbow_angle > 95:
            text, color = "Lower your chest...", "#f6ae2d"
        else:
            text, color = "Good depth — push back up", "#07b38c"

    return text, color


def analyze_lunge(pts, state):
    l_angle = calculate_angle(pts["l_hip"], pts["l_knee"], pts["l_ankle"])
    r_angle = calculate_angle(pts["r_hip"], pts["r_knee"], pts["r_ankle"])
    front_angle = min(l_angle, r_angle)
    front_knee = pts["l_knee"] if l_angle < r_angle else pts["r_knee"]
    front_ankle = pts["l_ankle"] if l_angle < r_angle else pts["r_ankle"]
    knee_past_toes = front_knee[0] > front_ankle[0] + 25

    state["min_angle"] = min(state.get("min_angle", 180), front_angle)

    text, color = "Standing — step into your lunge", "#7d7d84"

    if state["stage"] == "up" and front_angle < 140:
        state["stage"] = "down"
    elif state["stage"] == "down" and front_angle > 160:
        if state["min_angle"] <= 100:
            state["reps"] += 1
            text, color = "Great depth! Rep counted.", "#07b38c"
        else:
            text, color = "Go deeper — front thigh closer to parallel", "#e94560"
        state["stage"] = "up"
        state["min_angle"] = 180

    if state["stage"] == "down":
        if knee_past_toes:
            text, color = "Front knee past your toes — shift weight back", "#e94560"
        elif front_angle > 100:
            text, color = "Lower into the lunge...", "#f6ae2d"
        else:
            text, color = "Good depth — push back up", "#07b38c"

    return text, color


def analyze_situp(pts, state):
    torso_angle = calculate_angle(pts["l_shoulder"], pts["l_hip"], pts["l_knee"])
    state["min_angle"] = min(state.get("min_angle", 180), torso_angle)

    text, color = "Lying down — start your sit-up", "#7d7d84"

    if state["stage"] == "up" and torso_angle < 120:
        state["stage"] = "down"
    elif state["stage"] == "down" and torso_angle > 150:
        if state["min_angle"] <= 90:
            state["reps"] += 1
            text, color = "Strong rep! Curled up all the way.", "#07b38c"
        else:
            text, color = "Curl up higher next time", "#e94560"
        state["stage"] = "up"
        state["min_angle"] = 180

    if state["stage"] == "down":
        if torso_angle > 90:
            text, color = "Keep curling up...", "#f6ae2d"
        else:
            text, color = "Good height — lower back down slowly", "#07b38c"

    return text, color


def analyze_jumping_jack(pts, state):
    wrists_up = pts["l_wrist"][1] < pts["l_shoulder"][1] and pts["r_wrist"][1] < pts["r_shoulder"][1]
    ankle_dist = abs(pts["l_ankle"][0] - pts["r_ankle"][0])
    hip_dist = abs(pts["l_hip"][0] - pts["r_hip"][0])
    legs_spread = hip_dist > 0 and ankle_dist > hip_dist * 1.6
    is_open = wrists_up and legs_spread

    text, color = "Closed position — jump to open", "#7d7d84"

    if state["stage"] == "closed" and is_open:
        state["stage"] = "open"
    elif state["stage"] == "open" and not is_open:
        state["reps"] += 1
        state["stage"] = "closed"
        text, color = "Rep counted!", "#07b38c"

    if state["stage"] == "open":
        if not wrists_up:
            text, color = "Raise your arms higher", "#e94560"
        elif not legs_spread:
            text, color = "Spread your legs wider", "#e94560"
        else:
            text, color = "Good! Jump back to closed", "#07b38c"

    return text, color


def analyze_glute_bridge(pts, state):
    hip_angle = calculate_angle(pts["l_shoulder"], pts["l_hip"], pts["l_knee"])
    state["max_angle"] = max(state.get("max_angle", 0), hip_angle)

    text, color = "Lying down — lift your hips", "#7d7d84"

    if state["stage"] == "down" and hip_angle > 155:
        state["stage"] = "up"
    elif state["stage"] == "up" and hip_angle < 140:
        if state["max_angle"] >= 165:
            state["reps"] += 1
            text, color = "Powerful lift! Rep counted.", "#07b38c"
        else:
            text, color = "Lift your hips higher next time", "#e94560"
        state["stage"] = "down"
        state["max_angle"] = 0

    if state["stage"] == "up":
        if hip_angle < 165:
            text, color = "Lift a bit higher...", "#f6ae2d"
        else:
            text, color = "Great hip extension — hold, then lower", "#07b38c"

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
            text, color = f"Perfect form! Holding: {int(state['hold_seconds'])}s", "#07b38c"
        else:
            text, color = f"Good — keep it straight. Holding: {int(state['hold_seconds'])}s", "#07b38c"
    else:
        if body_angle < 165:
            text, color = "Hips sagging — lift them up", "#e94560"
        else:
            text, color = "Hips too high — lower them", "#e94560"

    return text, color


ANALYZERS = {
    "Squat": analyze_squat,
    "Push-up": analyze_pushup,
    "Lunge": analyze_lunge,
    "Sit-up": analyze_situp,
    "Jumping Jack": analyze_jumping_jack,
    "Glute Bridge": analyze_glute_bridge,
    "Plank": analyze_plank,
}


def export_data(state, exercise_name, export_format, session_history=None):
    """Export data as CSV or JSON."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    data_point = {
        "timestamp": timestamp,
        "exercise": exercise_name,
        "reps": state.get("reps", 0),
        "hold_seconds": round(state.get("hold_seconds", 0), 1),
        "min_angle": state.get("min_angle", 180),
        "max_angle": state.get("max_angle", 0),
        "stage": state.get("stage", "up"),
        "feedback": state.get("feedback", ""),
    }

    if export_format == "CSV":
        output = []
        headers = ["timestamp", "exercise", "reps", "hold_seconds", "min_angle", "max_angle", "stage", "feedback"]
        output.append(",".join(headers))
        output.append(",".join([
            str(data_point["timestamp"]), data_point["exercise"], str(data_point["reps"]),
            str(data_point["hold_seconds"]), str(data_point["min_angle"]), str(data_point["max_angle"]),
            data_point["stage"], f'"{data_point["feedback"]}"'
        ]))
        return "\n".join(output)
    else:  # JSON
        data_point["id"] = len(st.session_state.get("export_history", []))
        history = st.session_state.get("export_history", [])
        history.append(data_point)
        st.session_state.export_history = history
        return json.dumps(data_point, indent=2)


def export_session_history(session_history, export_format):
    """Export full session history."""
    if export_format == "CSV":
        if not session_history:
            return "No data to export"
        output = []
        headers = ["timestamp", "exercise", "reps", "hold_seconds", "min_angle", "max_angle", "stage", "feedback"]
        output.append(",".join(headers))
        for entry in session_history:
            output.append(",".join([
                str(entry.get("timestamp", "")), entry.get("exercise", ""), str(entry.get("reps", 0)),
                str(entry.get("hold_seconds", 0)), str(entry.get("min_angle", 180)), str(entry.get("max_angle", 0)),
                entry.get("stage", "up"), f'"{entry.get("feedback", "")}"'
            ]))
        return "\n".join(output)
    else:
        return json.dumps(session_history, indent=2)


def reset_exercise_state(exercise_name):
    """Reset state for a new exercise."""
    exercise_type = st.session_state.exercises[exercise_name]["type"]
    return {
        'exercise': exercise_name,
        'cap': None,
        'pose': None,
        'start_time': time.time(),
        'stage': "up" if exercise_type == "reps" else ("closed" if exercise_name == "Jumping Jack" else "down"),
        'reps': 0,
        'min_angle': 180,
        'max_angle': 0,
        'hold_seconds': 0,
        'last_tick': time.time(),
        'feedback': "Get in position...",
        'feedback_color': '#f6ae2d',
        'data_log': [],
        'export_format': st.session_state.app_state['export_format'],
        'running': False,
        'camera_error': None,
    }


def start_camera():
    """Initialize camera and pose detection."""
    try:
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            st.session_state.app_state['camera_error'] = "Could not access camera. Please check permissions."
            st.session_state.app_state['running'] = False
            return False

        # Set camera properties for better performance
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        cap.set(cv2.CAP_PROP_FPS, 30)

        pose = mp.solutions.pose.Pose(
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5,
            model_complexity=1,
            smooth_landmarks=True
        )

        st.session_state.app_state['cap'] = cap
        st.session_state.app_state['pose'] = pose
        st.session_state.app_state['running'] = True
        st.session_state.app_state['start_time'] = time.time()
        st.session_state.app_state['last_tick'] = time.time()
        st.session_state.app_state['camera_error'] = None
        return True
    except Exception as e:
        st.session_state.app_state['camera_error'] = f"Camera error: {str(e)}"
        st.session_state.app_state['running'] = False
        return False


def stop_camera():
    """Release camera resources."""
    if st.session_state.app_state['cap']:
        st.session_state.app_state['cap'].release()
        st.session_state.app_state['cap'] = None
    if st.session_state.app_state['pose']:
        st.session_state.app_state['pose'].close()
        st.session_state.app_state['pose'] = None
    st.session_state.app_state['running'] = False


def pause_camera():
    """Pause camera without releasing resources."""
    st.session_state.app_state['running'] = False


def render_header():
    """Render the application header."""
    st.markdown("""
        <div style="text-align: center; padding: 1.5rem 0 2rem;">
            <div class="logo-text">AI Virtual Gym Trainer</div>
            <div class="logo-subtext">Real-time Pose Detection • Form Analysis • Performance Tracking</div>
        </div>
    """, unsafe_allow_html=True)


def render_exercise_selector():
    """Render the exercise selection grid."""
    st.markdown("### Choose Your Exercise")

    cols = st.columns(4)
    exercise_items = list(st.session_state.exercises.items())

    for idx, (name, config) in enumerate(exercise_items):
        col = cols[idx % 4]
        with col:
            is_selected = st.session_state.app_state['exercise'] == name
            card_class = "exercise-card selected" if is_selected else "exercise-card"

            type_class = "exercise-type-reps" if config["type"] == "reps" else "exercise-type-hold"
            type_label = "REPS" if config["type"] == "reps" else "HOLD"

            st.markdown(f"""
                <div class="{card_class}" onclick="this.closest('[data-testid=column]').querySelector('button').click()">
                    <div class="exercise-icon">{config['icon']}</div>
                    <div class="exercise-name">{name}</div>
                    <span class="exercise-type {type_class}">{type_label}</span>
                    <div class="exercise-hint">
                        <span>📷</span> {config['camera_hint']}
                    </div>
                </div>
            """, unsafe_allow_html=True)

            if st.button(f"Select {name}", key=f"select_{name}", use_container_width=True):
                st.session_state.app_state = reset_exercise_state(name)
                st.rerun()


def render_sidebar():
    """Render the sidebar with controls and stats."""
    with st.sidebar:
        st.markdown("### 🎛️ Control Panel")

        # Exercise selection dropdown (alternative to cards)
        exercise_names = list(st.session_state.exercises.keys())
        current_idx = 0
        if st.session_state.app_state['exercise']:
            try:
                current_idx = exercise_names.index(st.session_state.app_state['exercise'])
            except ValueError:
                pass

        selected_exercise = st.selectbox(
            "Quick Switch Exercise",
            exercise_names,
            index=current_idx,
            key="exercise_dropdown"
        )

        if selected_exercise != st.session_state.app_state['exercise']:
            st.session_state.app_state = reset_exercise_state(selected_exercise)
            st.rerun()

        st.markdown("---")

        # Exercise stats
        config = st.session_state.exercises[st.session_state.app_state['exercise']]
        exercise_type = config["type"]
        state = st.session_state.app_state

        st.markdown("### 📊 Live Stats")

        # Metric cards
        col1, col2 = st.columns(2)

        with col1:
            if exercise_type == "reps":
                st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-label">Reps Completed</div>
                        <div class="metric-value" style="color: var(--accent);">{state['reps']}</div>
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-label">Hold Time</div>
                        <div class="metric-value" style="color: var(--success);">{int(state['hold_seconds'])}<span class="metric-unit">s</span></div>
                    </div>
                """, unsafe_allow_html=True)

        with col2:
            if exercise_type == "reps":
                # Progress towards next rep (based on min_angle)
                progress = max(0, min(1, (180 - state.get('min_angle', 180)) / 80))
                st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-label">Rep Progress</div>
                        <div class="metric-value" style="color: var(--info);">{int(progress * 100)}<span class="metric-unit">%</span></div>
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                    <div class="metric-card">
                        <div class="metric-label">Best Angle</div>
                        <div class="metric-value" style="color: var(--info);">{state.get('max_angle', 0)}<span class="metric-unit">°</span></div>
                    </div>
                """, unsafe_allow_html=True)

        # Min/Max angles
        col3, col4 = st.columns(2)
        with col3:
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Min Angle</div>
                    <div class="metric-value" style="color: var(--warning);">{state.get('min_angle', 180)}<span class="metric-unit">°</span></div>
                </div>
            """, unsafe_allow_html=True)

        with col4:
            st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-label">Max Angle</div>
                    <div class="metric-value" style="color: var(--warning);">{state.get('max_angle', 0)}<span class="metric-unit">°</span></div>
                </div>
            """, unsafe_allow_html=True)

        # Session duration
        if state['running'] and state['start_time']:
            duration = int(time.time() - state['start_time'])
            st.markdown(f"""
                <div class="metric-card" style="margin-top: 0.5rem;">
                    <div class="metric-label">Session Time</div>
                    <div class="metric-value" style="color: var(--info);">{duration // 60}:{duration % 60:02d}</div>
                </div>
            """, unsafe_allow_html=True)

        st.markdown("---")

        # Data export section
        st.markdown("### 📥 Data Export")
        export_format = st.radio("Format", ["CSV", "JSON"], horizontal=True, key="export_format_radio")
        st.session_state.app_state['export_format'] = export_format

        col_exp1, col_exp2 = st.columns(2)

        with col_exp1:
            if st.button("📥 Export Current", use_container_width=True, key="export_current"):
                exported_data = export_data(
                    st.session_state.app_state,
                    st.session_state.app_state['exercise'],
                    export_format
                )
                st.download_button(
                    label=f"Download {export_format}",
                    data=exported_data,
                    file_name=f"gym_{st.session_state.app_state['exercise'].lower().replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{export_format.lower()}",
                    mime="text/csv" if export_format == "CSV" else "application/json",
                    use_container_width=True,
                    key="download_current"
                )

        with col_exp2:
            if st.button("📊 Export History", use_container_width=True, key="export_history"):
                history_data = export_session_history(st.session_state.session_history, export_format)
                st.download_button(
                    label=f"Download History {export_format}",
                    data=history_data,
                    file_name=f"gym_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.{export_format.lower()}",
                    mime="text/csv" if export_format == "CSV" else "application/json",
                    use_container_width=True,
                    key="download_history"
                )

        st.markdown("---")

        # About section
        st.markdown("### ℹ️ About This Exercise")
        st.info(config["description"])

        with st.expander("📋 How to Perform"):
            for i, step in enumerate(config["steps"], 1):
                st.markdown(f"**{i}.** {step}")

        st.markdown("---")
        st.markdown("""
            <div style="text-align: center; color: var(--text-muted); font-size: 0.75rem; padding: 1rem;">
                AI Virtual Gym Trainer v2.0<br>
                Powered by MediaPipe & Streamlit
            </div>
        """, unsafe_allow_html=True)


def render_camera_feed(state, config):
    """Render the camera feed area."""
    st.markdown("### 📹 Live Camera Feed")

    # Camera status and error handling
    if state['camera_error']:
        st.error(f"📷 {state['camera_error']}")
        if st.button("🔄 Retry Camera", key="retry_camera"):
            state['camera_error'] = None
            st.rerun()
        return None

    video_placeholder = st.empty()

    if state['running'] and state['cap']:
        ret, frame = state['cap'].read()
        if ret:
            frame = cv2.flip(frame, 1)
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = state['pose'].process(rgb)

            feedback_text = "No person detected — step into frame"
            feedback_color = "#f6ae2d"

            if results.pose_landmarks:
                import mediapipe as mp_drawing
                mp_drawing.draw_landmarks(
                    frame, results.pose_landmarks, mp.solutions.pose.POSE_CONNECTIONS,
                    mp_drawing.DrawingSpec(color=(233, 69, 96), thickness=2, circle_radius=2),
                    mp_drawing.DrawingSpec(color=(7, 179, 140), thickness=2)
                )
                h, w, _ = frame.shape
                pts = get_points(results.pose_landmarks.landmark, w, h)

                analyzer = ANALYZERS[config["exercise"]]
                feedback_text, feedback_color = analyzer(pts, state)

                if config["type"] == "hold":
                    state['hold_seconds'] = state.get('hold_seconds', 0) + (time.time() - state.get('last_tick', time.time()))
                    state['last_tick'] = time.time()

            # Convert frame for Streamlit
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            frame_pil = Image.fromarray(frame_rgb)
            frame_resized = frame_pil.resize((640, 480))
            img_buffer = BytesIO()
            frame_resized.save(img_buffer, format="PNG")
            img_base64 = base64.b64encode(img_buffer.getvalue()).decode()

            # Update video feed
            video_placeholder.markdown(f"""
                <div class="camera-container active">
                    <img class="camera-feed" src="data:image/png;base64,{img_base64}" alt="Camera feed">
                    <div class="camera-overlay">
                        <div class="camera-status">
                            <span class="status-dot"></span>
                            LIVE - {config['exercise']} Analysis Active
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            return feedback_text, feedback_color
        else:
            state['running'] = False
            st.warning("Camera feed lost. Click Start to retry.")
            return "Camera feed lost", "#e94560"
    else:
        # Show placeholder when not running
        video_placeholder.markdown("""
            <div class="camera-container" style="height: 480px; display: flex; flex-direction: column; align-items: center; justify-content: center;">
                <div style="font-size: 4rem; margin-bottom: 1rem;">📷</div>
                <div style="color: var(--text-muted); font-size: 1.1rem;">Click "Start Monitoring" to begin</div>
                <div style="color: var(--text-muted); font-size: 0.85rem; margin-top: 0.5rem;">Camera access will be requested</div>
            </div>
        """, unsafe_allow_html=True)
        return "Select an exercise and click Start", "#7d7d84"


def render_feedback_panel(state, config, feedback_text, feedback_color):
    """Render the feedback panel with form analysis."""
    st.markdown("### 💡 Form Feedback")

    # Determine feedback class
    if feedback_color == "#07b38c":
        feedback_class = "feedback-good"
        icon = "✅"
    elif feedback_color == "#f6ae2d":
        feedback_class = "feedback-warning"
        icon = "⚠️"
    elif feedback_color == "#e94560":
        feedback_class = "feedback-bad"
        icon = "❌"
    else:
        feedback_class = "feedback-neutral"
        icon = "ℹ️"

    st.markdown(f"""
        <div class="feedback-banner {feedback_class} animate-fade-in">
            <span>{icon}</span>
            <span>{feedback_text}</span>
        </div>
    """, unsafe_allow_html=True)

    # Counter display
    if config["type"] == "reps":
        st.markdown(f"""
            <div style="text-align: center; margin: 1.5rem 0;">
                <div style="font-size: 4rem; font-weight: 800; color: var(--accent); font-variant-numeric: tabular-nums;">{state['reps']}</div>
                <div style="color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.1em; font-size: 0.8rem;">REPS COMPLETED</div>
            </div>
        """, unsafe_allow_html=True)
    else:
        mins = int(state['hold_seconds']) // 60
        secs = int(state['hold_seconds']) % 60
        st.markdown(f"""
            <div style="text-align: center; margin: 1.5rem 0;">
                <div style="font-size: 4rem; font-weight: 800; color: var(--success); font-variant-numeric: tabular-nums;">{mins:02d}:{secs:02d}</div>
                <div style="color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.1em; font-size: 0.8rem;">HOLD TIME</div>
            </div>
        """, unsafe_allow_html=True)

    # Camera hint
    st.caption(f"📷 Camera hint: {config['camera_hint']}")

    # Angle visualization for rep exercises
    if config["type"] == "reps" and state.get('min_angle', 180) < 180:
        progress = max(0, min(1, (180 - state['min_angle']) / 80))
        st.markdown(f"""
            <div style="margin-top: 1rem;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                    <span style="color: var(--text-muted); font-size: 0.85rem;">Current Depth</span>
                    <span style="color: var(--accent); font-weight: 600;">{state['min_angle']}°</span>
                </div>
                <div style="height: 8px; background: var(--border); border-radius: 4px; overflow: hidden;">
                    <div style="width: {progress * 100}%; height: 100%; background: linear-gradient(90deg, var(--accent), var(--accent-light)); border-radius: 4px; transition: width 0.3s ease;"></div>
                </div>
                <div style="display: flex; justify-content: space-between; margin-top: 0.5rem; font-size: 0.75rem; color: var(--text-muted);">
                    <span>Standing (180°)</span>
                    <span>Parallel (90°)</span>
                    <span>Deep (<90°)</span>
                </div>
            </div>
        """, unsafe_allow_html=True)


def render_control_buttons(state):
    """Render the control buttons."""
    st.markdown("---")
    col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])

    with col_btn1:
        if not state['running']:
            if st.button("▶️ Start Monitoring", type="primary", use_container_width=True, key="btn_start"):
                if start_camera():
                    st.rerun()
        else:
            st.button("▶️ Running...", disabled=True, use_container_width=True)

    with col_btn2:
        if state['running']:
            if st.button("⏸️ Pause", use_container_width=True, key="btn_pause"):
                pause_camera()
                st.rerun()
        else:
            st.button("⏸️ Pause", disabled=True, use_container_width=True)

    with col_btn3:
        if state['running']:
            if st.button("⏹️ Stop & Save", use_container_width=True, type="secondary", key="btn_stop"):
                # Save session to history
                session_entry = {
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "exercise": state['exercise'],
                    "reps": state['reps'],
                    "hold_seconds": round(state['hold_seconds'], 1),
                    "min_angle": state['min_angle'],
                    "max_angle": state['max_angle'],
                    "stage": state['stage'],
                    "feedback": state['feedback'],
                    "duration": int(time.time() - state['start_time']) if state['start_time'] else 0,
                }
                st.session_state.session_history.insert(0, session_entry)
                # Keep only last 50 sessions
                st.session_state.session_history = st.session_state.session_history[:50]

                stop_camera()
                st.success("Session saved! Check the History tab to view or export.")
                st.rerun()
        else:
            st.button("⏹️ Stop", disabled=True, use_container_width=True, type="secondary")


def render_session_history():
    """Render the session history tab."""
    st.markdown("### 📜 Session History")

    if not st.session_state.session_history:
        st.info("No sessions recorded yet. Complete a workout to see history here.")
        return

    # Summary stats
    total_sessions = len(st.session_state.session_history)
    total_reps = sum(s.get('reps', 0) for s in st.session_state.session_history)
    total_hold = sum(s.get('hold_seconds', 0) for s in st.session_state.session_history)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Sessions", total_sessions)
    with col2:
        st.metric("Total Reps", total_reps)
    with col3:
        st.metric("Total Hold Time", f"{int(total_hold)}s")

    # Session list
    for idx, session in enumerate(st.session_state.session_history):
        with st.expander(f"{session['exercise']} • {session['timestamp']} • {session.get('reps', 0)} reps / {session.get('hold_seconds', 0)}s"):
            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Exercise:** {session['exercise']}")
                st.write(f"**Date:** {session['timestamp']}")
                st.write(f"**Duration:** {session.get('duration', 0)//60}:{session.get('duration', 0)%60:02d}")
            with col2:
                st.write(f"**Reps:** {session.get('reps', 0)}")
                st.write(f"**Hold Time:** {session.get('hold_seconds', 0)}s")
                st.write(f"**Min Angle:** {session.get('min_angle', 180)}°")
                st.write(f"**Max Angle:** {session.get('max_angle', 0)}°")
            st.write(f"**Final Feedback:** {session.get('feedback', 'N/A')}")


def main():
    render_header()

    # Main layout
    if not st.session_state.app_state['exercise']:
        # Show exercise selector when no exercise chosen
        render_exercise_selector()

        # Features highlight
        st.markdown("---")
        st.markdown("### ✨ Features")
        feat_cols = st.columns(4)
        features = [
            ("🎯", "Real-time Analysis", "MediaPipe pose detection with 33 keypoints"),
            ("📊", "Form Feedback", "Instant visual & text feedback on every rep"),
            ("📈", "Progress Tracking", "Rep counting, hold timing, angle measurement"),
            ("📥", "Data Export", "CSV & JSON export for analysis"),
        ]
        for col, (icon, title, desc) in zip(feat_cols, features):
            with col:
                st.markdown(f"""
                    <div class="metric-card" style="text-align: center;">
                        <div style="font-size: 2.5rem; margin-bottom: 0.5rem;">{icon}</div>
                        <div style="font-weight: 600; margin-bottom: 0.25rem;">{title}</div>
                        <div style="color: var(--text-muted); font-size: 0.85rem;">{desc}</div>
                    </div>
                """, unsafe_allow_html=True)
    else:
        # Show main workout interface
        config = st.session_state.exercises[st.session_state.app_state['exercise']]
        config = {**config, "exercise": st.session_state.app_state['exercise']}
        state = st.session_state.app_state

        # Tabs for different views
        tab1, tab2 = st.tabs(["🏋️ Workout", "📜 History"])

        with tab1:
            # Two-column layout
            col_left, col_right = st.columns([2.2, 1], gap="large")

            with col_left:
                feedback_text, feedback_color = render_camera_feed(state, config)

            with col_right:
                render_feedback_panel(state, config, feedback_text, feedback_color)
                render_control_buttons(state)

        with tab2:
            render_session_history()

    # Sidebar
    render_sidebar()

    # Auto-refresh for live feed
    if state.get('running', False):
        time.sleep(0.033)  # ~30 FPS
        st.rerun()


if __name__ == "__main__":
    main()