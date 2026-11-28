"""
MediaPipe PoseLandmarker model management and OpenCV landmark drawing helpers.
"""

import os
import threading
import cv2
from mediapipe.tasks.python.core import base_options as base_options_module
from mediapipe.tasks.python.vision import PoseLandmarker, PoseLandmarkerOptions, RunningMode

from gymsense.config import CONFIG, get_logger
from gymsense.constants import POSE_CONNECTIONS

logger = get_logger(__name__)
_download_lock = threading.Lock()


def ensure_model():
    """Download the PoseLandmarker task model if not already present."""
    with _download_lock:
        if os.path.exists(CONFIG.model_path):
            return True, None
        try:
            import requests

            logger.info("Downloading MediaPipe PoseLandmarker model from %s", CONFIG.model_url)
            response = requests.get(CONFIG.model_url, stream=True, timeout=60)
            response.raise_for_status()
            os.makedirs(os.path.dirname(CONFIG.model_path) or ".", exist_ok=True)
            tmp_path = f"{CONFIG.model_path}.tmp"
            with open(tmp_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            os.replace(tmp_path, CONFIG.model_path)
            return True, None
        except Exception as exc:
            logger.exception("Failed to download pose model")
            return False, f"Failed to load pose model: {exc}"


def create_pose_landmarker():
    """Create a configured MediaPipe PoseLandmarker in VIDEO running mode."""
    ok, err = ensure_model()
    if not ok:
        return None, err
    try:
        base_opts = base_options_module.BaseOptions(model_asset_path=CONFIG.model_path)
        opts = PoseLandmarkerOptions(
            base_options=base_opts,
            running_mode=RunningMode.VIDEO,
            num_poses=1,
            min_pose_detection_confidence=CONFIG.min_detection_confidence,
            min_pose_presence_confidence=CONFIG.min_presence_confidence,
            min_tracking_confidence=CONFIG.min_tracking_confidence,
        )
        return PoseLandmarker.create_from_options(opts), None
    except Exception as exc:
        logger.exception("Failed to initialize PoseLandmarker")
        return None, f"Pose detector initialization failed: {exc}"


def draw_landmarks(frame, landmarks, w, h):
    """Draw visible body joints (indices 11-28) and skeleton connections on a BGR frame."""
    for a, b in POSE_CONNECTIONS:
        if a < len(landmarks) and b < len(landmarks):
            va = getattr(landmarks[a], "visibility", 1.0) or 0.0
            vb = getattr(landmarks[b], "visibility", 1.0) or 0.0
            if va >= 0.35 and vb >= 0.35:
                pa = (int(landmarks[a].x * w), int(landmarks[a].y * h))
                pb = (int(landmarks[b].x * w), int(landmarks[b].y * h))
                cv2.line(frame, pa, pb, (140, 179, 7), 3)
    for idx in range(11, min(29, len(landmarks))):
        lm = landmarks[idx]
        if (getattr(lm, "visibility", 1.0) or 0.0) >= 0.35:
            pt = (int(lm.x * w), int(lm.y * h))
            cv2.circle(frame, pt, 5, (96, 69, 233), -1)
            cv2.circle(frame, pt, 7, (255, 255, 255), 1)
