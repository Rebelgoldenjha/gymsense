"""
Constants, landmark indices, exercise metadata, and color tokens for GYMSENSE.
"""


class PL:
    """MediaPipe PoseLandmark indices (compatible with both Solutions and Tasks API)."""

    NOSE = 0
    LEFT_SHOULDER = 11
    RIGHT_SHOULDER = 12
    LEFT_ELBOW = 13
    RIGHT_ELBOW = 14
    LEFT_WRIST = 15
    RIGHT_WRIST = 16
    LEFT_HIP = 23
    RIGHT_HIP = 24
    LEFT_KNEE = 25
    RIGHT_KNEE = 26
    LEFT_ANKLE = 27
    RIGHT_ANKLE = 28


POSE_CONNECTIONS = [
    (11, 12), (11, 13), (13, 15), (12, 14), (14, 16),
    (11, 23), (12, 24), (23, 24), (23, 25), (25, 27), (24, 26), (26, 28),
]

COLOR_GOOD = "#07b38c"
COLOR_WARN = "#f6ae2d"
COLOR_BAD = "#e94560"
COLOR_NEUTRAL = "#888899"

BODY_PARTS = ["Legs & Glutes", "Arms & Chest", "Core", "Full Body / Cardio"]

EXERCISES = {
    "Squat": {
        "type": "reps",
        "camera_hint": "Face camera straight-on",
        "icon": "🏋️",
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
        "type": "reps",
        "camera_hint": "Film from side profile",
        "icon": "💪",
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
        "type": "hold",
        "camera_hint": "Film from side profile",
        "icon": "🧘",
        "targets": ["Core"],
        "description": "A core-strengthening hold that trains stability in your abs, back, and shoulders.",
        "steps": [
            "Get into a forearm or high-plank position.",
            "Keep your body in a straight line from shoulders to ankles.",
            "Engage your core — don't let your hips drop or pike up.",
            "Keep your neck neutral, eyes toward the floor.",
            "Hold the position while breathing steadily.",
        ],
    },
    "Lunge": {
        "type": "reps",
        "camera_hint": "Film from side profile",
        "icon": "🦵",
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
        "type": "reps",
        "camera_hint": "Face camera straight-on",
        "icon": "🏋️‍♀️",
        "targets": ["Core"],
        "description": "A core exercise that targets your abdominal muscles by curling your torso upward.",
        "steps": [
            "Lie on your back with knees bent, feet flat on the floor.",
            "Cross your arms over your chest or place hands lightly behind your head.",
            "Engage your abs and curl your torso up toward your knees.",
            "Curl up as high as you comfortably can.",
            "Lower back down with control — don't just drop.",
        ],
    },
    "Jumping Jack": {
        "type": "reps",
        "camera_hint": "Face camera straight-on",
        "icon": "🤸",
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
        "type": "reps",
        "camera_hint": "Film from side profile",
        "icon": "🍑",
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
