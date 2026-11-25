"""
AI Virtual Gym Trainer
------------------------
Menu to pick a no-equipment exercise. Every exercise below has an
embedded camera feed (inside the Tkinter window), MediaPipe pose
detection, and live form feedback + rep/hold tracking.

CAMERA ANGLE NOTES (important for accuracy):
    - Squat, Sit-up, Jumping Jack -> face the camera straight-on
    - Push-up, Lunge, Glute Bridge, Plank -> film from the SIDE
      (these need a side profile to judge back/hip alignment)

Run with: python exercise_selector.py
Requires:
    pip install opencv-python==4.11.0.86 mediapipe==0.10.21 pillow numpy==1.26.4
"""

import time
import tkinter as tk
from tkinter import font as tkfont
import cv2
import mediapipe as mp
import numpy as np
from PIL import Image, ImageTk

mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils


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

    L = mp_pose.PoseLandmark
    return {
        "l_shoulder": p(L.LEFT_SHOULDER), "r_shoulder": p(L.RIGHT_SHOULDER),
        "l_hip": p(L.LEFT_HIP), "r_hip": p(L.RIGHT_HIP),
        "l_knee": p(L.LEFT_KNEE), "r_knee": p(L.RIGHT_KNEE),
        "l_ankle": p(L.LEFT_ANKLE), "r_ankle": p(L.RIGHT_ANKLE),
        "l_elbow": p(L.LEFT_ELBOW), "r_elbow": p(L.RIGHT_ELBOW),
        "l_wrist": p(L.LEFT_WRIST), "r_wrist": p(L.RIGHT_WRIST),
    }


# ============================================================
# Per-exercise analyzers.
# Each returns (feedback_text, feedback_color) and updates
# state (a dict with at least "stage" and "reps" or "hold_seconds").
# ============================================================

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
    # Uses whichever leg is more bent as the "front" leg.
    l_angle = calculate_angle(pts["l_hip"], pts["l_knee"], pts["l_ankle"])
    r_angle = calculate_angle(pts["r_hip"], pts["r_knee"], pts["r_ankle"])
    front_angle = min(l_angle, r_angle)
    front_knee = pts["l_knee"] if l_angle < r_angle else pts["r_knee"]
    front_ankle = pts["l_ankle"] if l_angle < r_angle else pts["r_ankle"]
    knee_past_toes = front_knee[0] > front_ankle[0] + 25  # side view assumed

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


EXERCISES = {
    "Squat": {
        "type": "reps", "analyzer": analyze_squat, "camera_hint": "Face the camera",
        "targets": ["Legs & Glutes"],
        "description": "A lower-body exercise that builds leg and glute strength by bending at the hips and knees.",
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
        "type": "reps", "analyzer": analyze_pushup, "camera_hint": "Film from the side",
        "targets": ["Arms & Chest"],
        "description": "An upper-body exercise that works the chest, shoulders, and triceps using your bodyweight.",
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
        "type": "hold", "analyzer": analyze_plank, "camera_hint": "Film from the side",
        "targets": ["Core"],
        "description": "A core-strengthening hold that trains stability in your abs, back, and shoulders.",
        "steps": [
            "Get into a forearm or high-plank position.",
            "Keep your body in a straight line from shoulders to ankles.",
            "Engage your core - don't let your hips drop or pike up.",
            "Keep your neck neutral, eyes toward the floor.",
            "Hold the position while breathing steadily.",
        ],
    },
    "Lunge": {
        "type": "reps", "analyzer": analyze_lunge, "camera_hint": "Film from the side",
        "targets": ["Legs & Glutes"],
        "description": "A single-leg exercise that builds strength and balance in the legs and glutes.",
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
        "type": "reps", "analyzer": analyze_situp, "camera_hint": "Face the camera",
        "targets": ["Core"],
        "description": "A core exercise that targets your abdominal muscles by curling your torso upward.",
        "steps": [
            "Lie on your back with knees bent, feet flat on the floor.",
            "Cross your arms over your chest or place hands lightly behind your head.",
            "Engage your abs and curl your torso up toward your knees.",
            "Curl up as high as you comfortably can.",
            "Lower back down with control - don't just drop.",
        ],
    },
    "Jumping Jack": {
        "type": "reps", "analyzer": analyze_jumping_jack, "camera_hint": "Face the camera",
        "targets": ["Full Body / Cardio"],
        "description": "A full-body cardio exercise that raises your heart rate using coordinated arm and leg movement.",
        "steps": [
            "Start standing with feet together, arms at your sides.",
            "Jump your feet out wide while raising your arms overhead.",
            "Jump back to the starting position, feet together, arms down.",
            "Keep a steady, quick rhythm.",
            "Land softly on the balls of your feet.",
        ],
    },
    "Glute Bridge": {
        "type": "reps", "analyzer": analyze_glute_bridge, "camera_hint": "Film from the side",
        "targets": ["Legs & Glutes"],
        "description": "A lower-body exercise that isolates and strengthens the glutes and hamstrings.",
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


BODY_PARTS = ["Legs & Glutes", "Arms & Chest", "Core", "Full Body / Cardio"]


class GymTrainerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("AI Virtual Gym Trainer")
        self.root.geometry("640x760")
        self.root.configure(bg="#1e1e2f")

        self.title_font = tkfont.Font(family="Helvetica", size=20, weight="bold")
        self.subtitle_font = tkfont.Font(family="Helvetica", size=11)
        self.button_font = tkfont.Font(family="Helvetica", size=13)
        self.feedback_font = tkfont.Font(family="Helvetica", size=14, weight="bold")

        self.cap = None
        self.pose = None
        self.current_exercise = None
        self.state = {}

        self.active_frame = None
        self.camera_frame = None

        self.build_home()

    # ---------------- Home screen ----------------
    def build_home(self):
        if self.active_frame:
            self.active_frame.destroy()
        if self.camera_frame:
            self.camera_frame.destroy()
            self.camera_frame = None

        frame = tk.Frame(self.root, bg="#1e1e2f")
        frame.pack(fill="both", expand=True)
        self.active_frame = frame

        tk.Label(
            frame, text="AI Virtual Gym Trainer", font=self.title_font,
            fg="white", bg="#1e1e2f", pady=30
        ).pack()

        tk.Label(
            frame, text="How do you want to start?", font=self.subtitle_font,
            fg="#a0a0c0", bg="#1e1e2f", pady=5
        ).pack()

        tk.Button(
            frame, text="I know my exercise", font=self.button_font, width=26, height=2,
            bg="#3b3b5c", fg="white", activebackground="#5757a3", activeforeground="white",
            relief="flat", bd=0, command=self.build_exercise_menu
        ).pack(pady=15)

        tk.Button(
            frame, text="Suggest an exercise for me", font=self.button_font, width=26, height=2,
            bg="#3b3b5c", fg="white", activebackground="#5757a3", activeforeground="white",
            relief="flat", bd=0, command=self.build_bodypart_menu
        ).pack(pady=15)

    # ---------------- Exercise picker (all 7) ----------------
    def build_exercise_menu(self):
        if self.active_frame:
            self.active_frame.destroy()
        frame = tk.Frame(self.root, bg="#1e1e2f")
        frame.pack(fill="both", expand=True)
        self.active_frame = frame

        tk.Label(
            frame, text="Which exercise are you doing?",
            font=self.title_font, fg="white", bg="#1e1e2f", pady=20
        ).pack()

        tk.Label(
            frame, text="Pick one — the camera will check your form",
            font=self.subtitle_font, fg="#a0a0c0", bg="#1e1e2f", pady=5
        ).pack()

        button_container = tk.Frame(frame, bg="#1e1e2f")
        button_container.pack(pady=15)

        for name, config in EXERCISES.items():
            row = tk.Frame(button_container, bg="#1e1e2f")
            row.pack(pady=6)
            tk.Button(
                row, text=name, font=self.button_font, width=18, height=1,
                bg="#3b3b5c", fg="white", activebackground="#5757a3",
                activeforeground="white", relief="flat", bd=0, pady=8,
                command=lambda n=name: self.launch_camera(n)
            ).pack(side="left")
            tk.Label(
                row, text=f"  ({config['camera_hint']})", font=self.subtitle_font,
                fg="#7a7a9a", bg="#1e1e2f"
            ).pack(side="left")

        tk.Button(
            frame, text="← Back", font=self.subtitle_font,
            bg="#1e1e2f", fg="#a0a0c0", relief="flat", bd=0,
            command=self.build_home
        ).pack(pady=20)

    # ---------------- Body-part picker ----------------
    def build_bodypart_menu(self):
        if self.active_frame:
            self.active_frame.destroy()
        frame = tk.Frame(self.root, bg="#1e1e2f")
        frame.pack(fill="both", expand=True)
        self.active_frame = frame

        tk.Label(
            frame, text="What do you want to work on?",
            font=self.title_font, fg="white", bg="#1e1e2f", pady=20
        ).pack()

        tk.Label(
            frame, text="Pick a body part — I'll suggest exercises for it",
            font=self.subtitle_font, fg="#a0a0c0", bg="#1e1e2f", pady=5
        ).pack()

        button_container = tk.Frame(frame, bg="#1e1e2f")
        button_container.pack(pady=15)

        for part in BODY_PARTS:
            tk.Button(
                button_container, text=part, font=self.button_font, width=22, height=2,
                bg="#3b3b5c", fg="white", activebackground="#5757a3", activeforeground="white",
                relief="flat", bd=0, command=lambda p=part: self.build_bodypart_results(p)
            ).pack(pady=8)

        tk.Button(
            frame, text="← Back", font=self.subtitle_font,
            bg="#1e1e2f", fg="#a0a0c0", relief="flat", bd=0,
            command=self.build_home
        ).pack(pady=20)

    def build_bodypart_results(self, body_part):
        if self.active_frame:
            self.active_frame.destroy()
        frame = tk.Frame(self.root, bg="#1e1e2f")
        frame.pack(fill="both", expand=True)
        self.active_frame = frame

        tk.Label(
            frame, text=body_part, font=self.title_font,
            fg="white", bg="#1e1e2f", pady=20
        ).pack()

        matches = [name for name, cfg in EXERCISES.items() if body_part in cfg["targets"]]

        tk.Label(
            frame, text=f"Recommended exercises ({len(matches)}):", font=self.subtitle_font,
            fg="#a0a0c0", bg="#1e1e2f", pady=5
        ).pack()

        button_container = tk.Frame(frame, bg="#1e1e2f")
        button_container.pack(pady=15)

        for name in matches:
            config = EXERCISES[name]
            row = tk.Frame(button_container, bg="#1e1e2f")
            row.pack(pady=6)
            tk.Button(
                row, text=name, font=self.button_font, width=18, height=1,
                bg="#3b3b5c", fg="white", activebackground="#5757a3",
                activeforeground="white", relief="flat", bd=0, pady=8,
                command=lambda n=name: self.launch_camera(n)
            ).pack(side="left")
            tk.Label(
                row, text=f"  ({config['camera_hint']})", font=self.subtitle_font,
                fg="#7a7a9a", bg="#1e1e2f"
            ).pack(side="left")

        tk.Button(
            frame, text="← Back", font=self.subtitle_font,
            bg="#1e1e2f", fg="#a0a0c0", relief="flat", bd=0,
            command=self.build_bodypart_menu
        ).pack(pady=20)

    # ---------------- Camera screen (shared by all exercises) ----------------
    def launch_camera(self, exercise_name):
        if self.active_frame:
            self.active_frame.destroy()
            self.active_frame = None
        self.current_exercise = exercise_name
        config = EXERCISES[exercise_name]

        # Outer frame holds a Canvas + Scrollbar so the whole screen can scroll
        self.camera_frame = tk.Frame(self.root, bg="#1e1e2f")
        self.camera_frame.pack(fill="both", expand=True)

        canvas = tk.Canvas(self.camera_frame, bg="#1e1e2f", highlightthickness=0)
        scrollbar = tk.Scrollbar(self.camera_frame, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        content = tk.Frame(canvas, bg="#1e1e2f")
        content_window = canvas.create_window((0, 0), window=content, anchor="n")

        def on_content_configure(event):
            canvas.configure(scrollregion=canvas.bbox("all"))

        def on_canvas_configure(event):
            # keep content centered/full-width as the canvas resizes
            canvas.itemconfig(content_window, width=event.width)

        content.bind("<Configure>", on_content_configure)
        canvas.bind("<Configure>", on_canvas_configure)

        def on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        canvas.bind_all("<MouseWheel>", on_mousewheel)

        # ---- Everything below goes inside "content" instead of camera_frame ----
        tk.Label(
            content, text=exercise_name, font=self.title_font,
            fg="white", bg="#1e1e2f", pady=10
        ).pack()

        tk.Label(
            content, text=config["camera_hint"], font=self.subtitle_font,
            fg="#7a7a9a", bg="#1e1e2f"
        ).pack()

        self.video_label = tk.Label(content, bg="#000000")
        self.video_label.pack(pady=5)

        counter_text = "Time: 0s" if config["type"] == "hold" else "Reps: 0"
        self.rep_label = tk.Label(
            content, text=counter_text, font=self.title_font,
            fg="#8fdc8f", bg="#1e1e2f", pady=5
        )
        self.rep_label.pack()

        self.feedback_label = tk.Label(
            content, text="Get in position...", font=self.feedback_font,
            fg="#ffcc66", bg="#1e1e2f", pady=10, wraplength=560, justify="center"
        )
        self.feedback_label.pack()

        tk.Button(
            content, text="Stop / Back to menu", font=self.button_font,
            bg="#3b3b5c", fg="white", relief="flat", bd=0, pady=8,
            command=self.stop_camera
        ).pack(pady=10)

        # ---- How-to info panel ----
        info_frame = tk.Frame(content, bg="#2a2a45")
        info_frame.pack(fill="x", padx=15, pady=(5, 15))

        tk.Label(
            info_frame, text=f"About {exercise_name}", font=self.button_font,
            fg="white", bg="#2a2a45", anchor="w", pady=6
        ).pack(fill="x", padx=10)

        tk.Label(
            info_frame, text=config["description"], font=self.subtitle_font,
            fg="#c0c0d8", bg="#2a2a45", wraplength=580, justify="left", anchor="w"
        ).pack(fill="x", padx=10, pady=(0, 8))

        tk.Label(
            info_frame, text="How to do it:", font=self.subtitle_font,
            fg="white", bg="#2a2a45", anchor="w"
        ).pack(fill="x", padx=10)

        steps_text = "\n".join(f"{i+1}. {step}" for i, step in enumerate(config["steps"]))
        tk.Label(
            info_frame, text=steps_text, font=self.subtitle_font,
            fg="#c0c0d8", bg="#2a2a45", wraplength=580, justify="left", anchor="w", pady=6
        ).pack(fill="x", padx=10, pady=(0, 10))

        # reset per-session state
        self.state = {"stage": "up", "reps": 0, "min_angle": 180, "max_angle": 0,
                      "hold_seconds": 0, "last_tick": time.time()}
        if exercise_name == "Jumping Jack":
            self.state["stage"] = "closed"
        if exercise_name == "Glute Bridge":
            self.state["stage"] = "down"

        self.cap = cv2.VideoCapture(0)
        self.pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5)
        self.update_frame()

    def stop_camera(self):
        if self.cap:
            self.cap.release()
            self.cap = None
        if self.pose:
            self.pose.close()
            self.pose = None
        self.camera_frame.unbind_all("<MouseWheel>")
        self.camera_frame.destroy()
        self.camera_frame = None
        self.build_home()

    def update_frame(self):
        if self.cap is None:
            return

        ret, frame = self.cap.read()
        if not ret:
            self.root.after(10, self.update_frame)
            return

        frame = cv2.flip(frame, 1)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.pose.process(rgb)

        config = EXERCISES[self.current_exercise]
        feedback_text = "No person detected — step into frame"
        feedback_color = "#ffcc66"

        if results.pose_landmarks:
            mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
            h, w, _ = frame.shape
            pts = get_points(results.pose_landmarks.landmark, w, h)

            feedback_text, feedback_color = config["analyzer"](pts, self.state)

            if config["type"] == "hold":
                self.rep_label.config(text=f"Time: {int(self.state.get('hold_seconds', 0))}s")
            else:
                self.rep_label.config(text=f"Reps: {self.state['reps']}")

        self.feedback_label.config(text=feedback_text, fg=feedback_color)

        img = Image.fromarray(rgb).resize((560, 420))
        imgtk = ImageTk.PhotoImage(image=img)
        self.video_label.imgtk = imgtk
        self.video_label.config(image=imgtk)

        self.root.after(15, self.update_frame)


if __name__ == "__main__":
    root = tk.Tk()
    app = GymTrainerApp(root)
    root.mainloop()

