# GYMSENSE — AI Virtual Gym Trainer

Real-time bodyweight exercise form analysis, rep counting, and hold-time tracking powered by **MediaPipe PoseLandmarker**, **WebRTC**, **OpenCV**, and **Streamlit**.

---

## Features
- **7 Supported Exercises:** Squat, Push-up, Plank, Lunge, Sit-up, Jumping Jack, Glute Bridge
- **Browser-Side Live Camera (WebRTC):** Works on **Streamlit Cloud**, mobile browsers, and desktop browsers via `streamlit-webrtc` (with optional local OpenCV webcam fallback)
- **Biomechanical Accuracy:** Bilateral landmark visibility selection, exponential moving average (EMA) angle smoothing, sag-vs-pike Plank detection, and direction/scale-normalized Lunge tracking
- **Session History & Export:** Track reps, hold duration, min/max joint angles, and export workouts as **CSV** or **JSON**
- **Desktop Mode:** Tkinter desktop app ([exercise_selector.py](exercise_selector.py)) sharing the exact same pose analysis engine

---

## Tech Stack
- **Frontend / Web:** Streamlit (`>=1.51.0`), `streamlit-webrtc` (`>=0.47.0`), PyAV (`av`)
- **Computer Vision:** MediaPipe Tasks API (`PoseLandmarker`), OpenCV (`opencv-python-headless`), NumPy, Pillow
- **Desktop UI:** Tkinter (optional local entrypoint)
- **Containerization & CI:** Docker (multi-stage), Docker Compose, Nginx, GitHub Actions (`ruff`, `pytest`)

---

## Project Structure

```
GYMSENSE/
├── streamlit_app_enhanced.py     # Main Streamlit Cloud / Docker web entrypoint
├── exercise_selector.py          # Optional Tkinter desktop entrypoint
├── gymsense/                     # Modular core package
│   ├── config.py                 # Env-based configuration & logging
│   ├── constants.py              # Exercise definitions, landmarks, color tokens
│   ├── pose_analyzer.py          # Pure biomechanical angle math & 7 analyzers
│   ├── model_loader.py           # MediaPipe PoseLandmarker download/init & drawing
│   ├── webrtc_processor.py       # Thread-safe WebRTC VideoProcessorBase
│   ├── export_service.py         # Session summary & CSV/JSON serialization
│   └── ui/
│       ├── styles.py             # Dark-theme CSS
│       └── components.py         # Reusable Streamlit UI components
├── tests/
│   └── test_pose_analyzer.py     # Unit tests for analyzers, config, and exports
├── test_core_logic.py            # Convenience test runner
├── .streamlit/config.toml        # Streamlit server & theme configuration
├── .env.example                  # Documented environment variables
├── requirements.txt              # Python dependencies
├── packages.txt                  # System packages for Streamlit Cloud
├── Dockerfile                    # Multi-stage production container
├── docker-compose.yml            # Local / production orchestration
└── nginx.conf                    # Reverse proxy with WebSocket support
```

---

## Local Setup

```bash
# 1. Create and activate virtual environment
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. (Optional) Configure environment variables
cp .env.example .env

# 4. Run the web app
streamlit run streamlit_app_enhanced.py
```

Open `http://localhost:8501`, select an exercise, and click **START** on the WebRTC player to allow browser camera access.

---

## Environment Variables
See [.env.example](.env.example) for all supported variables:
- `GYMSENSE_APP_TITLE`, `GYMSENSE_APP_ICON`, `GYMSENSE_LOG_LEVEL`
- `GYMSENSE_MODEL_PATH`, `GYMSENSE_MODEL_URL`
- `GYMSENSE_STUN_URL` (default: `stun:stun.l.google.com:19302`)
- `GYMSENSE_MIN_DETECTION_CONFIDENCE`, `GYMSENSE_MIN_PRESENCE_CONFIDENCE`, `GYMSENSE_MIN_TRACKING_CONFIDENCE`
- `GYMSENSE_HISTORY_LIMIT`

---

## Deployment

### Streamlit Cloud
1. Push this repository to GitHub (`main` branch).
2. Go to [share.streamlit.io](https://share.streamlit.io) → **New app**.
3. Select your repository, branch `main`, and main file **`streamlit_app_enhanced.py`**.
4. Click **Deploy**.

### Docker
```bash
docker compose up -d --build
```
Access at `http://localhost:8501`.

---

## Testing & Code Quality

```bash
# Syntax & bytecode check
python -m compileall -q gymsense streamlit_app_enhanced.py exercise_selector.py tests

# Run unit tests
python test_core_logic.py
# Or with pytest:
pytest -v tests/
```
