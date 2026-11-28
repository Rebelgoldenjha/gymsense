"""
Thread-safe WebRTC Video Processor for GYMSENSE.
Processes browser camera frames in real time via streamlit-webrtc + MediaPipe PoseLandmarker.
"""

import threading
import time
import av
import cv2
from mediapipe import Image as MpImage, ImageFormat
from streamlit_webrtc import RTCConfiguration, VideoProcessorBase

from gymsense.config import CONFIG
from gymsense.constants import EXERCISES
from gymsense.model_loader import create_pose_landmarker, draw_landmarks
from gymsense.pose_analyzer import ANALYZERS, get_points_from_landmarks, initial_stage_for

RTC_CONFIGURATION = RTCConfiguration(
    {"iceServers": [{"urls": [CONFIG.stun_url]}]}
)


def _hex_to_bgr(hex_color):
    h = (hex_color or "").lstrip("#")
    if len(h) != 6:
        return (200, 200, 200)
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return (b, g, r)


class PoseVideoProcessor(VideoProcessorBase):
    """Real-time pose detection and exercise analyzer for WebRTC video frames."""

    def __init__(self):
        self._lock = threading.Lock()
        self._landmarker, self._model_error = create_pose_landmarker()
        self.state = self._make_state("Squat")

    @staticmethod
    def _make_state(exercise_name):
        return {
            "exercise": exercise_name,
            "stage": initial_stage_for(exercise_name),
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
        }

    def set_exercise(self, exercise_name):
        if not exercise_name or exercise_name not in EXERCISES:
            return
        with self._lock:
            if self.state.get("exercise") != exercise_name:
                last_ts = self.state.get("last_ts_ms", 0)
                self.state = self._make_state(exercise_name)
                self.state["last_ts_ms"] = last_ts

    def reset_counters(self):
        with self._lock:
            ex = self.state.get("exercise", "Squat")
            last_ts = self.state.get("last_ts_ms", 0)
            self.state = self._make_state(ex)
            self.state["last_ts_ms"] = last_ts

    def get_snapshot(self):
        with self._lock:
            return {
                "exercise": self.state["exercise"],
                "stage": self.state["stage"],
                "reps": self.state["reps"],
                "min_angle": self.state["min_angle"],
                "max_angle": self.state["max_angle"],
                "current_angle": self.state["current_angle"],
                "hold_seconds": round(self.state["hold_seconds"], 1),
                "feedback": self.state["feedback"],
                "feedback_color": self.state["feedback_color"],
                "model_error": self._model_error,
            }

    def recv(self, frame: av.VideoFrame) -> av.VideoFrame:
        img = cv2.flip(frame.to_ndarray(format="bgr24"), 1)
        h, w, _ = img.shape

        if self._model_error or self._landmarker is None:
            cv2.putText(
                img,
                self._model_error or "Loading pose model...",
                (16, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (0, 180, 255),
                2,
                cv2.LINE_AA,
            )
            return av.VideoFrame.from_ndarray(img, format="bgr24")

        rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        mp_image = MpImage(image_format=ImageFormat.SRGB, data=rgb)

        with self._lock:
            now_ms = int(time.time() * 1000)
            ts_ms = max(self.state["last_ts_ms"] + 1, now_ms)
            self.state["last_ts_ms"] = ts_ms
            ex_name = self.state["exercise"]
            cfg = EXERCISES.get(ex_name, {"type": "reps"})

            result = self._landmarker.detect_for_video(mp_image, ts_ms)
            feedback, fcolor = "No person detected — step into frame", "#f6ae2d"

            if result.pose_landmarks and len(result.pose_landmarks) > 0:
                landmarks = result.pose_landmarks[0]
                draw_landmarks(img, landmarks, w, h)
                pts = get_points_from_landmarks(landmarks, w, h)
                feedback, fcolor = ANALYZERS[ex_name](pts, self.state)
            elif cfg.get("type") == "hold":
                self.state["last_tick"] = time.time()

            self.state["feedback"] = feedback
            self.state["feedback_color"] = fcolor

            self._draw_hud(img, w, ex_name, cfg, feedback, fcolor)

        return av.VideoFrame.from_ndarray(img, format="bgr24")

    def _draw_hud(self, img, w, ex_name, cfg, feedback, fcolor):
        overlay = img.copy()
        cv2.rectangle(overlay, (0, 0), (w, 72), (18, 18, 28), -1)
        cv2.addWeighted(overlay, 0.72, img, 0.28, 0, img)

        counter_txt = (
            f"HOLD: {int(self.state['hold_seconds'])}s"
            if cfg.get("type") == "hold"
            else f"REPS: {self.state['reps']}"
        )
        cv2.putText(img, f"{ex_name} | {counter_txt}", (14, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (255, 255, 255), 2, cv2.LINE_AA)
        if self.state.get("current_angle"):
            cv2.putText(img, f"{self.state['current_angle']:.0f} deg", (w - 115, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200, 200, 220), 2, cv2.LINE_AA)
        cv2.putText(img, feedback[:58], (14, 58), cv2.FONT_HERSHEY_SIMPLEX, 0.62, _hex_to_bgr(fcolor), 2, cv2.LINE_AA)
