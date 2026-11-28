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

import os
import time
import tkinter as tk
from tkinter import font as tkfont
import cv2
import mediapipe as mp
import numpy as np
from PIL import Image, ImageTk
from gymsense.constants import BODY_PARTS, EXERCISES
from gymsense.model_loader import create_pose_landmarker, draw_landmarks as _draw_tasks_landmarks
from gymsense.pose_analyzer import ANALYZERS, get_points_from_landmarks as get_points

# MediaPipe compatibility layer (works with both 0.x solutions and 1.x Tasks API)
mp_pose = None
mp_drawing = None
USE_TASKS_API = False

try:
    mp_pose = mp.solutions.pose
    mp_drawing = mp.solutions.drawing_utils
except AttributeError:
    USE_TASKS_API = True
    from mediapipe import Image as MpImage, ImageFormat


# Per-exercise analyzers and metadata are imported from pose_analyzer.py


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
        self._last_ts_ms = 0
        if USE_TASKS_API:
            self.pose, err = create_pose_landmarker()
            if err:
                raise RuntimeError(err)
        else:
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
        h, w, _ = frame.shape

        config = EXERCISES[self.current_exercise]
        feedback_text = "No person detected — step into frame"
        feedback_color = "#ffcc66"

        landmarks = None
        if USE_TASKS_API:
            mp_image = MpImage(image_format=ImageFormat.SRGB, data=rgb)
            ts_ms = max(self._last_ts_ms + 1, int(time.time() * 1000))
            self._last_ts_ms = ts_ms
            results = self.pose.detect_for_video(mp_image, ts_ms)
            if results.pose_landmarks and len(results.pose_landmarks) > 0:
                landmarks = results.pose_landmarks[0]
                _draw_tasks_landmarks(frame, landmarks, w, h)
        else:
            results = self.pose.process(rgb)
            if results.pose_landmarks:
                mp_drawing.draw_landmarks(frame, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)
                landmarks = results.pose_landmarks.landmark

        if landmarks is not None:
            pts = get_points(landmarks, w, h)
            feedback_text, feedback_color = ANALYZERS[self.current_exercise](pts, self.state)

            if config["type"] == "hold":
                self.rep_label.config(text=f"Time: {int(self.state.get('hold_seconds', 0))}s")
            else:
                self.rep_label.config(text=f"Reps: {self.state['reps']}")

        self.feedback_label.config(text=feedback_text, fg=feedback_color)

        display_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(display_rgb).resize((560, 420))
        imgtk = ImageTk.PhotoImage(image=img)
        self.video_label.imgtk = imgtk
        self.video_label.config(image=imgtk)

        self.root.after(15, self.update_frame)


if __name__ == "__main__":
    root = tk.Tk()
    app = GymTrainerApp(root)
    root.mainloop()

