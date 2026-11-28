# AI Virtual Gym Trainer - Complete Deployment Guide

## 📋 Table of Contents
1. [Quick Start](#quick-start)
2. [Local Development](#local-development)
3. [Docker Deployment](#docker-deployment)
4. [Streamlit Cloud Deployment](#streamlit-cloud-deployment)
5. [Production Deployment](#production-deployment)
6. [Troubleshooting](#troubleshooting)
7. [Architecture Overview](#architecture-overview)

---

## 🚀 Quick Start

### Prerequisites
- **Python 3.11+** (recommended)
- **Git** for version control
- **Docker** (optional, for containerized deployment)
- **Webcam** for pose detection

### One-Command Local Run
```bash
# Clone and run
git clone <your-repo>
cd GYMSENSE
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
streamlit run streamlit_app_enhanced.py
```
**Access at:** `http://localhost:8501`

---

## 💻 Local Development

### 1. Environment Setup
```bash
# Create virtual environment
python -m venv venv

# Activate (Linux/Mac)
source venv/bin/activate

# Activate (Windows PowerShell)
venv\Scripts\Activate.ps1

# Activate (Windows CMD)
venv\Scripts\activate.bat
```

### 2. Install Dependencies
```bash
# Upgrade pip
pip install --upgrade pip

# Install Python dependencies
pip install -r requirements.txt

# Verify installations
python -c "import cv2, mediapipe, streamlit, numpy; print('All packages OK')"
```

### 3. Run Application
```bash
# Main app (enhanced version)
streamlit run streamlit_app_enhanced.py

# Alternative ports
streamlit run streamlit_app_enhanced.py --server.port 8502

# With custom config
streamlit run streamlit_app_enhanced.py --server.headless true --server.address 0.0.0.0
```

### 4. Development with Hot Reload (Docker)
```bash
# Start dev container with live reload
docker-compose --profile dev up -d

# View logs
docker-compose logs -f gym-trainer-dev

# Access at: http://localhost:8502
```

### 5. Testing Camera
```bash
# Test camera access
python -c "
import cv2
cap = cv2.VideoCapture(0)
print('Camera opened:', cap.isOpened())
ret, frame = cap.read()
print('Frame captured:', ret, frame.shape if ret else '')
cap.release()
"
```

---

## 🐳 Docker Deployment

### Docker Files Overview
| File | Purpose |
|------|---------|
| `Dockerfile` | Production multi-stage build |
| `Dockerfile.dev` | Development with hot reload |
| `docker-compose.yml` | Multi-service orchestration |
| `nginx.conf` | Reverse proxy for production |

### 1. Build Production Image
```bash
# Build image
docker build -t gym-trainer:latest .

# Or use docker-compose
docker-compose build gym-trainer
```

### 2. Run Production Container
```bash
# Simple run
docker run -d \
  --name gym-trainer \
  -p 8501:8501 \
  -e STREAMLIT_SERVER_HEADLESS=true \
  -e STREAMLIT_SERVER_ADDRESS=0.0.0.0 \
  gym-trainer:latest

# With docker-compose (recommended)
docker-compose up -d gym-trainer
```

### 3. Run Development Container
```bash
# Start with hot reload
docker-compose --profile dev up -d

# Access at: http://localhost:8502
```

### 4. Production with Nginx Reverse Proxy
```bash
# Start full production stack
docker-compose --profile production up -d

# Access at: http://localhost (port 80)
# HTTPS: Configure SSL certificates in ./ssl/ directory
```

### 5. Docker Commands Reference
```bash
# View logs
docker-compose logs -f gym-trainer

# Rebuild after code changes
docker-compose build gym-trainer
docker-compose up -d

# Access container shell
docker-compose exec gym-trainer bash

# Check health
curl http://localhost:8501/_stcore/health

# Stop all services
docker-compose down

# Stop and remove volumes
docker-compose down -v

# View running containers
docker-compose ps
```

### 6. Docker Image Details
**Production Image Features:**
- Multi-stage build (~500MB final size)
- Non-root user for security
- Health checks included
- Only runtime dependencies
- Optimized layer caching

**Environment Variables:**
```bash
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_HEADLESS=true
STREAMLIT_SERVER_ADDRESS=0.0.0.0
STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
STREAMLIT_THEME_BASE=dark
```

---

## ☁️ Streamlit Cloud Deployment

### 1. Prepare Repository
```bash
# Initialize git (if not already)
git init
git add .
git commit -m "Deploy: AI Virtual Gym Trainer v2.0"

# Push to GitHub
git remote add origin https://github.com/yourusername/gym-sense.git
git push -u origin main
```

### 2. Deploy on Streamlit Cloud
1. Go to: https://share.streamlit.io
2. Sign in with GitHub
3. Click **"New app"**
4. Configure:
   - **Repository:** `yourusername/gym-sense`
   - **Branch:** `main`
   - **Main file path:** `streamlit_app_enhanced.py`
5. Click **"Deploy!"**

### 3. Streamlit Cloud Configuration
The app includes required files for Streamlit Cloud:

**`requirements.txt`** (Python dependencies):
```txt
streamlit==1.28.0
opencv-python-headless==4.8.1.78
mediapipe==0.10.30
pillow==10.0.1
numpy==1.24.4
pandas==2.1.4
```

**`packages.txt`** (System dependencies):
```txt
libgl1-mesa-glx
libglib2.0-0
libsm6
libxext6
libxrender-dev
libgomp1
```

### 4. Camera Access on Streamlit Cloud
- ✅ Works in browser (HTTPS required - automatic on Streamlit Cloud)
- ✅ Mobile and desktop browsers supported
- ✅ User must grant camera permission
- ✅ Best results: Chrome/Edge, good lighting, contrasting clothing

### 5. Streamlit Cloud Limitations
| Limitation | Workaround |
|------------|------------|
| Free tier resource limits | Upgrade for production |
| First deploy downloads models (~100MB) | Wait 2-3 minutes |
| No persistent storage | Use database for history |
| Session timeout | Keep session active |

---

## 🏭 Production Deployment

### 1. Architecture Overview
```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Client    │────▶│   Nginx     │────▶│  Streamlit  │
│  (Browser)  │     │ (Reverse    │     │   App       │
└─────────────┘     │  Proxy)     │     │  (Port 8501)│
                    └─────────────┘     └─────────────┘
                           │                    │
                    ┌──────▼──────┐     ┌───────▼───────┐
                    │ Rate Limit  │     │  MediaPipe    │
                    │   SSL/TLS   │     │  Pose Model   │
                    └─────────────┘     └───────────────┘
```

### 2. Nginx Configuration (`nginx.conf`)
Key features:
- **WebSocket support** for Streamlit
- **Rate limiting** (10 req/s burst 20)
- **Security headers** (X-Frame-Options, CSP, etc.)
- **Gzip compression** for static assets
- **SSL/TLS termination** (configure certificates in `./ssl/`)

### 3. SSL Certificate Setup
```bash
# Create SSL directory
mkdir -p ssl

# Option 1: Let's Encrypt (production)
# certbot certonly --standalone -d yourdomain.com
# cp /etc/letsencrypt/live/yourdomain.com/fullchain.pem ssl/cert.pem
# cp /etc/letsencrypt/live/yourdomain.com/privkey.pem ssl/key.pem

# Option 2: Self-signed (development)
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout ssl/key.pem -out ssl/cert.pem \
  -subj "/CN=localhost"
```

### 4. Production Checklist
- [ ] HTTPS configured with valid certificates
- [ ] Nginx reverse proxy running
- [ ] Rate limiting enabled
- [ ] Health checks passing
- [ ] Logs configured and monitored
- [ ] Backup strategy for session data
- [ ] Monitoring alerts set up
- [ ] Resource limits configured (CPU/Memory)

### 5. Scaling for High Load
```bash
# Multiple replicas with docker-compose
docker-compose up -d --scale gym-trainer=3

# Kubernetes deployment (example)
kubectl create deployment gym-trainer --image=gym-trainer:latest
kubectl scale deployment gym-trainer --replicas=3
kubectl expose deployment gym-trainer --port=8501 --target-port=8501
```

---

## 🔧 Troubleshooting

### Camera Issues
| Problem | Solution |
|---------|----------|
| Camera not accessible | Grant browser permission; use HTTPS; try external webcam |
| "Camera read failed" | Close other camera apps; check `cv2.VideoCapture(0)` index |
| Low frame rate | Reduce resolution in code; close background apps |
| Black screen | Check camera permissions in browser settings |

### Pose Detection Issues
| Problem | Solution |
|---------|----------|
| No pose detected | Ensure good lighting; wear contrasting colors; face camera properly |
| Jittery landmarks | Lower `min_detection_confidence` to 0.3; increase `model_complexity` |
| Wrong angle calculation | Verify camera angle matches exercise requirements |
| Feedback delayed | Reduce processing resolution; optimize analyzer functions |

### Deployment Issues
| Problem | Solution |
|---------|----------|
| App won't start | Run `pip install -r requirements.txt`; check Python version |
| Docker build fails | Check Docker daemon; try `docker system prune`; verify base image |
| Streamlit Cloud deploy fails | Check `packages.txt` and `requirements.txt`; view build logs |
| Nginx 502 Bad Gateway | Verify Streamlit container is healthy; check port mapping |

### Debug Commands
```bash
# Check Streamlit health
curl http://localhost:8501/_stcore/health

# View Streamlit metrics
curl http://localhost:8501/_stcore/metrics

# Test camera in container
docker-compose exec gym-trainer python -c "
import cv2
cap = cv2.VideoCapture(0)
print('Camera:', cap.isOpened())
"

# Check MediaPipe installation
docker-compose exec gym-trainer python -c "
import mediapipe as mp
print('MediaPipe:', mp.__version__)
"

# View container logs
docker-compose logs --tail=100 gym-trainer

# Check resource usage
docker stats gym-trainer
```

---

## 📐 Architecture Overview

### Application Structure
```
GYMSENSE/
├── streamlit_app_enhanced.py    # Main web application
├── exercise_selector.py         # Original Tkinter desktop app
├── test_core_logic.py           # Unit tests
├── requirements.txt             # Python dependencies
├── packages.txt                 # System deps for Streamlit Cloud
├── Dockerfile                   # Production Docker image
├── Dockerfile.dev               # Development Docker image
├── docker-compose.yml           # Multi-service orchestration
├── nginx.conf                   # Reverse proxy config
├── README.md                    # Project overview
└── DEPLOYMENT_GUIDE.md          # This file
```

### Core Components

#### 1. MediaPipe Pose Detection
- **33 keypoints** for full-body tracking
- **Real-time** processing at ~30 FPS
- **Configurable** confidence thresholds

#### 2. Exercise Analyzers
Each exercise has a dedicated analyzer function:
```python
def analyze_squat(pts, state):
    # Calculate knee angle
    # Track rep state (up/down)
    # Detect form issues (knee cave, depth)
    # Return feedback text and color
```

#### 3. State Management
- **Session state** for exercise data
- **Camera state** (running, initialized, error)
- **History** for session persistence

#### 4. UI Components
- **Exercise grid** for selection
- **Live camera feed** with landmark overlay
- **Real-time feedback** banner
- **Statistics panel** (reps, angles, time)
- **History/export** functionality

### Data Flow
```
Camera Frame → MediaPipe Process → Landmarks → Analyzer → State Update → UI Render
     │              │                    │           │            │           │
  OpenCV         Pose Model          33 pts      Angle Calc   Reps/Hold   Streamlit
  Capture        (MediaPipe)         (x,y)       Logic        Counter     Image
```

---

## 📦 Requirements Summary

### Python Packages
```txt
streamlit==1.28.0
opencv-python-headless==4.8.1.78
mediapipe==0.10.30
pillow==10.0.1
numpy==1.24.4
pandas==2.1.4
```

### System Dependencies (Linux)
```bash
# Ubuntu/Debian
apt-get update && apt-get install -y \
  libgl1-mesa-glx libglib2.0-0 libsm6 \
  libxext6 libxrender-dev libgomp1

# Alpine (Docker)
apk add --no-cache \
  libglvnd libglib2.0 libsm libxext \
  libxrender libgomp
```

---

## 🔒 Security Considerations

1. **Camera Access**: Only with explicit user permission (browser prompt)
2. **No Server-side Storage**: All processing client-side
3. **Non-root Container**: Docker runs as `app` user
4. **HTTPS Required**: For camera access on production
5. **Rate Limiting**: Configured in Nginx
6. **Security Headers**: CSP, X-Frame-Options, etc.

---

## 📈 Monitoring & Maintenance

### Health Endpoints
- **Streamlit**: `http://localhost:8501/_stcore/health`
- **Metrics**: `http://localhost:8501/_stcore/metrics`

### Log Locations
```bash
# Docker logs
docker-compose logs -f gym-trainer

# Nginx logs
docker-compose logs -f nginx

# Application logs (inside container)
docker-compose exec gym-trainer tail -f /var/log/streamlit.log
```

### Backup Strategy
- Session history stored in browser sessionStorage
- For persistence: Add Redis/PostgreSQL
- Export data via CSV/JSON download buttons

---

## 🎯 Next Steps for Production

1. **Authentication** (Streamlit Auth, Auth0, or custom)
2. **Database Integration** for persistent history
3. **User Profiles** with preferences
4. **Progress Charts** (weekly/monthly trends)
5. **Exercise Library** with video demonstrations
6. **Coach Dashboard** for remote training
7. **Mobile App** (React Native + WebView)
8. **API** for third-party integrations

---

## 📞 Support Resources

- **Streamlit Docs**: https://docs.streamlit.io
- **MediaPipe Docs**: https://mediapipe.dev
- **Docker Docs**: https://docs.docker.com
- **Nginx Docs**: https://nginx.org/en/docs/
- **GitHub Issues**: Create issue in repository

---

## ✅ Deployment Verification Checklist

### Local Development
- [ ] Virtual environment created
- [ ] Dependencies installed
- [ ] Camera accessible
- [ ] App runs on `localhost:8501`
- [ ] Exercise selection works
- [ ] Camera feed displays
- [ ] Pose landmarks visible
- [ ] Rep counting functional
- [ ] Data export works

### Docker Deployment
- [ ] Image builds successfully
- [ ] Container starts healthy
- [ ] Port 8501 accessible
- [ ] Camera works in container
- [ ] Health check passes
- [ ] Logs show no errors

### Streamlit Cloud
- [ ] Repository connected
- [ ] Deploy succeeds
- [ ] Public URL accessible
- [ ] Camera permission works
- [ ] Mobile responsive

### Production (Nginx + SSL)
- [ ] SSL certificates valid
- [ ] Nginx proxies correctly
- [ ] WebSocket connections work
- [ ] Rate limiting active
- [ ] Security headers present
- [ ] Monitoring configured

---

**Last Updated:** 2026-11-26  
**Version:** 2.0  
**Status:** Production Ready