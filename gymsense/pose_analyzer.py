"""
Pure Biomechanical Pose Analysis Engine for GYMSENSE.
No UI or camera framework dependencies — independently testable.
"""

import time
import numpy as np

from gymsense.constants import (
    COLOR_BAD,
    COLOR_GOOD,
    COLOR_NEUTRAL,
    COLOR_WARN,
    EXERCISES,
    PL,
)


def calculate_angle(a, b, c):
    """Calculate angle in degrees [0, 180] at vertex b formed by points a-b-c."""
    a = np.array(a[:2], dtype=float)
    b = np.array(b[:2], dtype=float)
    c = np.array(c[:2], dtype=float)
    radians = np.arctan2(c[1] - b[1], c[0] - b[0]) - np.arctan2(a[1] - b[1], a[0] - b[0])
    angle = np.abs(radians * 180.0 / np.pi)
    if angle > 180.0:
        angle = 360.0 - angle
    return float(angle)


def smooth_angle(state, key, raw_angle, alpha=0.45):
    """Apply exponential moving average to reduce single-frame landmark jitter."""
    prev = state.get(key)
    smoothed = float(raw_angle) if prev is None else alpha * float(raw_angle) + (1.0 - alpha) * float(prev)
    state[key] = smoothed
    return smoothed


def get_points_from_landmarks(landmarks, w, h):
    """Extract key body landmarks in pixel coordinates as [x_px, y_px, visibility]."""
    def p(idx):
        lm = landmarks[idx]
        vis = getattr(lm, "visibility", 1.0)
        if vis is None:
            vis = 1.0
        return [float(lm.x) * w, float(lm.y) * h, float(vis)]

    return {
        "l_shoulder": p(PL.LEFT_SHOULDER), "r_shoulder": p(PL.RIGHT_SHOULDER),
        "l_elbow": p(PL.LEFT_ELBOW), "r_elbow": p(PL.RIGHT_ELBOW),
        "l_wrist": p(PL.LEFT_WRIST), "r_wrist": p(PL.RIGHT_WRIST),
        "l_hip": p(PL.LEFT_HIP), "r_hip": p(PL.RIGHT_HIP),
        "l_knee": p(PL.LEFT_KNEE), "r_knee": p(PL.RIGHT_KNEE),
        "l_ankle": p(PL.LEFT_ANKLE), "r_ankle": p(PL.RIGHT_ANKLE),
    }


def _vis(pt):
    return pt[2] if len(pt) > 2 else 1.0


def _pick_best_side(pts, joint_names, min_vis=0.45):
    """Select 'l' or 'r' side with higher average visibility."""
    l_vis = sum(_vis(pts[f"l_{j}"]) for j in joint_names) / len(joint_names)
    r_vis = sum(_vis(pts[f"r_{j}"]) for j in joint_names) / len(joint_names)
    side = "l" if l_vis >= r_vis else "r"
    best_min = min(_vis(pts[f"{side}_{j}"]) for j in joint_names)
    return side, best_min >= min_vis


def _check_all_visible(pts, keys, min_vis=0.45):
    return all(_vis(pts[k]) >= min_vis for k in keys)


def initial_stage_for(exercise_name):
    """Return the initial state machine stage for a given exercise."""
    cfg = EXERCISES.get(exercise_name, {})
    if exercise_name == "Jumping Jack":
        return "closed"
    if exercise_name == "Glute Bridge" or cfg.get("type") == "hold":
        return "down"
    return "up"


def analyze_squat(pts, state):
    side, visible = _pick_best_side(pts, ["hip", "knee", "ankle"])
    if not visible:
        return "Step back — hips, knees & ankles must be visible", COLOR_WARN

    angle = smooth_angle(state, "_smooth_angle", calculate_angle(pts[f"{side}_hip"], pts[f"{side}_knee"], pts[f"{side}_ankle"]))
    state["current_angle"] = round(angle, 1)

    if state["stage"] == "down":
        state["min_angle"] = min(state.get("min_angle", 180), angle)

    knees_caving = False
    if _check_all_visible(pts, ["l_knee", "r_knee", "l_ankle", "r_ankle"], min_vis=0.45):
        knee_dist = abs(pts["l_knee"][0] - pts["r_knee"][0])
        ankle_dist = abs(pts["l_ankle"][0] - pts["r_ankle"][0])
        knees_caving = ankle_dist > 20 and knee_dist < ankle_dist * 0.78

    if state["stage"] == "up" and angle < 140:
        state["stage"] = "down"
        state["min_angle"] = angle
    elif state["stage"] == "down" and angle > 160:
        if state["min_angle"] <= 105:
            state["reps"] += 1
            text, color = "Excellent depth! Rep counted.", COLOR_GOOD
        else:
            text, color = "Too shallow — go lower next time", COLOR_BAD
        state["stage"] = "up"
        state["min_angle"] = 180
        return text, color

    if state["stage"] == "down":
        if knees_caving:
            return "Knees caving in — push knees out", COLOR_BAD
        if angle > 105:
            return "Keep lowering...", COLOR_WARN
        return "Good depth — now stand up", COLOR_GOOD

    return "Standing — start your squat", COLOR_NEUTRAL


def analyze_pushup(pts, state):
    side, visible = _pick_best_side(pts, ["shoulder", "elbow", "wrist", "hip", "ankle"])
    if not visible:
        return "Position full body in side view", COLOR_WARN

    elbow_angle = smooth_angle(state, "_smooth_angle", calculate_angle(pts[f"{side}_shoulder"], pts[f"{side}_elbow"], pts[f"{side}_wrist"]))
    back_angle = calculate_angle(pts[f"{side}_shoulder"], pts[f"{side}_hip"], pts[f"{side}_ankle"])
    state["current_angle"] = round(elbow_angle, 1)

    if state["stage"] == "down":
        state["min_angle"] = min(state.get("min_angle", 180), elbow_angle)

    if state["stage"] == "up" and elbow_angle < 140:
        state["stage"] = "down"
        state["min_angle"] = elbow_angle
    elif state["stage"] == "down" and elbow_angle > 155:
        if state["min_angle"] <= 100:
            state["reps"] += 1
            text, color = "Perfect rep! Chest went low enough.", COLOR_GOOD
        else:
            text, color = "Go lower — chest closer to floor", COLOR_BAD
        state["stage"] = "up"
        state["min_angle"] = 180
        return text, color

    if state["stage"] == "down":
        if back_angle < 155:
            return "Hips sagging — tighten your core", COLOR_BAD
        if elbow_angle > 100:
            return "Lower your chest...", COLOR_WARN
        return "Good depth — push back up", COLOR_GOOD

    return "Arms extended — start your push-up", COLOR_NEUTRAL


def analyze_plank(pts, state):
    side, visible = _pick_best_side(pts, ["shoulder", "hip", "ankle"])
    now = time.time()
    dt = max(0.0, min(now - state.get("last_tick", now), 1.0))
    state["last_tick"] = now

    if not visible:
        return "Position full body in side view", COLOR_WARN

    shoulder, hip, ankle = pts[f"{side}_shoulder"], pts[f"{side}_hip"], pts[f"{side}_ankle"]
    body_angle = smooth_angle(state, "_smooth_angle", calculate_angle(shoulder, hip, ankle))
    state["current_angle"] = round(body_angle, 1)
    state["max_angle"] = max(state.get("max_angle", 0), round(body_angle, 1))

    # Signed vertical offset from shoulder-ankle line distinguishes sag (>0) from pike (<0)
    dx = ankle[0] - shoulder[0]
    if abs(dx) > 1e-3:
        t = (hip[0] - shoulder[0]) / dx
        hip_offset_y = hip[1] - (shoulder[1] + t * (ankle[1] - shoulder[1]))
    else:
        hip_offset_y = 0.0

    if body_angle >= 165:
        state["hold_seconds"] = state.get("hold_seconds", 0.0) + dt
        if body_angle > 175:
            return f"Perfect form! Holding: {int(state['hold_seconds'])}s", COLOR_GOOD
        return f"Good — keep body straight. Holding: {int(state['hold_seconds'])}s", COLOR_GOOD

    return ("Hips too high — lower them", COLOR_BAD) if hip_offset_y < 0 else ("Hips sagging — lift them up", COLOR_BAD)


def analyze_lunge(pts, state):
    if not _check_all_visible(pts, ["l_hip", "l_knee", "l_ankle", "r_hip", "r_knee", "r_ankle"], min_vis=0.4):
        return "Step back — both legs must be visible", COLOR_WARN

    l_angle = calculate_angle(pts["l_hip"], pts["l_knee"], pts["l_ankle"])
    r_angle = calculate_angle(pts["r_hip"], pts["r_knee"], pts["r_ankle"])
    front_angle = smooth_angle(state, "_smooth_angle", min(l_angle, r_angle))
    state["current_angle"] = round(front_angle, 1)

    if l_angle < r_angle:
        front_hip, front_knee, front_ankle = pts["l_hip"], pts["l_knee"], pts["l_ankle"]
    else:
        front_hip, front_knee, front_ankle = pts["r_hip"], pts["r_knee"], pts["r_ankle"]

    shin_len = max(1.0, float(np.hypot(front_knee[0] - front_ankle[0], front_knee[1] - front_ankle[1])))
    facing_sign = 1.0 if front_knee[0] >= front_hip[0] else -1.0
    knee_past_toes = (front_knee[0] - front_ankle[0]) * facing_sign > shin_len * 0.25

    if state["stage"] == "down":
        state["min_angle"] = min(state.get("min_angle", 180), front_angle)

    if state["stage"] == "up" and front_angle < 140:
        state["stage"] = "down"
        state["min_angle"] = front_angle
    elif state["stage"] == "down" and front_angle > 160:
        if state["min_angle"] <= 105:
            state["reps"] += 1
            text, color = "Great depth! Rep counted.", COLOR_GOOD
        else:
            text, color = "Go deeper — thigh closer to parallel", COLOR_BAD
        state["stage"] = "up"
        state["min_angle"] = 180
        return text, color

    if state["stage"] == "down":
        if knee_past_toes:
            return "Front knee past toes — shift weight back", COLOR_BAD
        if front_angle > 105:
            return "Lower into the lunge...", COLOR_WARN
        return "Good depth — push back up", COLOR_GOOD

    return "Standing — step into your lunge", COLOR_NEUTRAL


def analyze_situp(pts, state):
    side, visible = _pick_best_side(pts, ["shoulder", "hip", "knee"])
    if not visible:
        return "Position upper body & knees in frame", COLOR_WARN

    torso_angle = smooth_angle(state, "_smooth_angle", calculate_angle(pts[f"{side}_shoulder"], pts[f"{side}_hip"], pts[f"{side}_knee"]))
    state["current_angle"] = round(torso_angle, 1)

    if state["stage"] == "down":
        state["min_angle"] = min(state.get("min_angle", 180), torso_angle)

    if state["stage"] == "up" and torso_angle < 120:
        state["stage"] = "down"
        state["min_angle"] = torso_angle
    elif state["stage"] == "down" and torso_angle > 145:
        if state["min_angle"] <= 90:
            state["reps"] += 1
            text, color = "Strong rep! Curled up all the way.", COLOR_GOOD
        else:
            text, color = "Curl up higher next time", COLOR_BAD
        state["stage"] = "up"
        state["min_angle"] = 180
        return text, color

    if state["stage"] == "down":
        if torso_angle > 90:
            return "Keep curling up...", COLOR_WARN
        return "Good height — lower back down slowly", COLOR_GOOD

    return "Lying down — start your sit-up", COLOR_NEUTRAL


def analyze_jumping_jack(pts, state):
    required = ["l_wrist", "r_wrist", "l_shoulder", "r_shoulder", "l_hip", "r_hip", "l_ankle", "r_ankle"]
    if not _check_all_visible(pts, required, min_vis=0.4):
        return "Step back — full body must be visible", COLOR_WARN

    wrists_up = pts["l_wrist"][1] < pts["l_shoulder"][1] and pts["r_wrist"][1] < pts["r_shoulder"][1]
    ankle_dist = abs(pts["l_ankle"][0] - pts["r_ankle"][0])
    hip_dist = abs(pts["l_hip"][0] - pts["r_hip"][0])
    legs_spread = hip_dist > 10 and ankle_dist > hip_dist * 1.5

    if state["stage"] == "closed" and wrists_up and legs_spread:
        state["stage"] = "open"
    elif state["stage"] == "open" and (not wrists_up) and (not legs_spread):
        state["reps"] += 1
        state["stage"] = "closed"
        return "Rep counted!", COLOR_GOOD

    if state["stage"] == "open":
        if not wrists_up:
            return "Raise your arms higher", COLOR_BAD
        if not legs_spread:
            return "Spread your legs wider", COLOR_BAD
        return "Good! Jump back to closed", COLOR_GOOD

    return "Closed position — jump to open", COLOR_NEUTRAL


def analyze_glute_bridge(pts, state):
    side, visible = _pick_best_side(pts, ["shoulder", "hip", "knee"])
    if not visible:
        return "Position full body in side view", COLOR_WARN

    hip_angle = smooth_angle(state, "_smooth_angle", calculate_angle(pts[f"{side}_shoulder"], pts[f"{side}_hip"], pts[f"{side}_knee"]))
    state["current_angle"] = round(hip_angle, 1)

    if state["stage"] == "up":
        state["max_angle"] = max(state.get("max_angle", 0), hip_angle)

    if state["stage"] == "down" and hip_angle > 150:
        state["stage"] = "up"
        state["max_angle"] = hip_angle
    elif state["stage"] == "up" and hip_angle < 140:
        if state["max_angle"] >= 165:
            state["reps"] += 1
            text, color = "Powerful lift! Rep counted.", COLOR_GOOD
        else:
            text, color = "Lift your hips higher next time", COLOR_BAD
        state["stage"] = "down"
        state["max_angle"] = 0
        return text, color

    if state["stage"] == "up":
        if hip_angle < 165:
            return "Lift a bit higher...", COLOR_WARN
        return "Great hip extension — hold, then lower", COLOR_GOOD

    return "Lying down — lift your hips", COLOR_NEUTRAL


ANALYZERS = {
    "Squat": analyze_squat,
    "Push-up": analyze_pushup,
    "Plank": analyze_plank,
    "Lunge": analyze_lunge,
    "Sit-up": analyze_situp,
    "Jumping Jack": analyze_jumping_jack,
    "Glute Bridge": analyze_glute_bridge,
}
