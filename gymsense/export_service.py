"""
Session history and CSV/JSON export service for GYMSENSE.
"""

import csv
import io
import json
import time
from datetime import datetime


def build_session_entry(state):
    """Create a normalized workout summary dictionary from session state."""
    start_time = state.get("start_time") or 0
    return {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "exercise": state.get("exercise") or "",
        "reps": int(state.get("reps", 0)),
        "hold_seconds": round(float(state.get("hold_seconds", 0.0)), 1),
        "min_angle": round(float(state.get("min_angle", 180)), 1),
        "max_angle": round(float(state.get("max_angle", 0)), 1),
        "stage": state.get("stage", "up"),
        "feedback": state.get("feedback", ""),
        "duration": int(time.time() - start_time) if start_time else 0,
    }


def serialize_sessions(entries, fmt):
    """Serialize one or more session entries to CSV or JSON safely."""
    fmt_upper = (fmt or "JSON").upper()
    if fmt_upper == "CSV":
        buf = io.StringIO()
        fieldnames = [
            "timestamp", "exercise", "reps", "hold_seconds",
            "min_angle", "max_angle", "stage", "feedback",
        ]
        writer = csv.DictWriter(buf, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for entry in entries:
            writer.writerow(entry)
        return buf.getvalue(), "text/csv", "csv"

    return json.dumps(entries, indent=2), "application/json", "json"
