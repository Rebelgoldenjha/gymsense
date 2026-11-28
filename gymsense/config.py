"""
Centralized environment-based configuration for GYMSENSE.
All external URLs, thresholds, and runtime settings are configurable via environment variables.
"""

import logging
import os
from dataclasses import dataclass


@dataclass(frozen=True)
class AppConfig:
    app_title: str
    app_icon: str
    log_level: str
    model_path: str
    model_url: str
    stun_url: str
    min_detection_confidence: float
    min_presence_confidence: float
    min_tracking_confidence: float
    history_limit: int
    help_url: str
    issues_url: str


def _float_env(name: str, default: float) -> float:
    raw = os.getenv(name)
    if raw is None:
        return default
    try:
        val = float(raw)
        return val if 0.0 <= val <= 1.0 else default
    except ValueError:
        return default


def _int_env(name: str, default: int) -> int:
    raw = os.getenv(name)
    if raw is None:
        return default
    try:
        val = int(raw)
        return val if val > 0 else default
    except ValueError:
        return default


def load_config() -> AppConfig:
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    default_model_path = os.path.join(root_dir, "pose_landmarker_lite.task")
    return AppConfig(
        app_title=os.getenv("GYMSENSE_APP_TITLE", "AI Virtual Gym Trainer"),
        app_icon=os.getenv("GYMSENSE_APP_ICON", "💪"),
        log_level=os.getenv("GYMSENSE_LOG_LEVEL", "INFO").upper(),
        model_path=os.getenv("GYMSENSE_MODEL_PATH", default_model_path),
        model_url=os.getenv(
            "GYMSENSE_MODEL_URL",
            "https://storage.googleapis.com/mediapipe-models/pose_landmarker/"
            "pose_landmarker_lite/float16/1/pose_landmarker_lite.task",
        ),
        stun_url=os.getenv("GYMSENSE_STUN_URL", "stun:stun.l.google.com:19302"),
        min_detection_confidence=_float_env("GYMSENSE_MIN_DETECTION_CONFIDENCE", 0.5),
        min_presence_confidence=_float_env("GYMSENSE_MIN_PRESENCE_CONFIDENCE", 0.5),
        min_tracking_confidence=_float_env("GYMSENSE_MIN_TRACKING_CONFIDENCE", 0.5),
        history_limit=_int_env("GYMSENSE_HISTORY_LIMIT", 50),
        help_url=os.getenv("GYMSENSE_HELP_URL", "https://github.com/Rebelgoldenjha/GymSensee"),
        issues_url=os.getenv("GYMSENSE_ISSUES_URL", "https://github.com/Rebelgoldenjha/GymSensee/issues"),
    )


CONFIG = load_config()


def get_logger(name: str) -> logging.Logger:
    """Return a consistently formatted logger."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s"))
        logger.addHandler(handler)
    logger.setLevel(getattr(logging, CONFIG.log_level, logging.INFO))
    return logger
