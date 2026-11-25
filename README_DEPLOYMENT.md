# AI Virtual Gym Trainer - Deployment Guide

## 🚀 Quick Start Options

### Option 1: Streamlit Cloud (Recommended for Demos)
**Easiest - No infrastructure needed, free tier available**

1. **Push to GitHub:**
   ```bash
   git init
   git add .
   git commit -m "Deploy: AI Virtual Gym Trainer v2.0"
   # Create repo on GitHub and push
   ```

2. **Deploy on Streamlit Cloud:**
   - Go to https://share.streamlit.io
   - Click "New app"
   - Select your repo
   - Main file: `streamlit_app_enhanced.py`
   - Click "Deploy"

3. **Your public URL:** `https://your-repo-name.streamlit.app`

**✅ Perfect for investor demos - shareable link, works on any device**

---

### Option 2: Docker (Recommended for Production)
**Full control, scalable, production-ready**

```bash
# Build and run with Docker Compose (recommended)
docker-compose up -d

# Or build and run manually
docker build -t gym-trainer .
docker run -p 8501:8501 gym-trainer
```

**Access at:** `http://localhost:8501`

**Production with Nginx:**
```bash
docker-compose --profile production up -d
```
Access at `http://localhost` (port 80) with reverse proxy, rate limiting, and WebSocket support.

---

### Option 3: Local Development
**For testing and development**

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run enhanced app
streamlit run streamlit_app_enhanced.py

# Or run original app
streamlit run streamlit_app.py
```

**Access at:** `http://localhost:8501`

**Development with hot reload:**
```bash
docker-compose --profile dev up -d
```
Access at `http://localhost:8502` with auto-reload on file changes.

---

## 📦 File Structure

```
GYMSENSE/
├── streamlit_app_enhanced.py    # Enhanced web app (recommended)
├── streamlit_app.py             # Original web app
├── exercise_selector.py         # Original Tkinter desktop app
├── requirements.txt             # Python dependencies
├── packages.txt                 # System deps for Streamlit Cloud
├── Dockerfile                   # Production Docker image
├── Dockerfile.dev               # Development Docker image
├── docker-compose.yml           # Multi-service orchestration
├── nginx.conf                   # Reverse proxy config
├── README.md                    # Project overview
└── README_DEPLOYMENT.md         # This file
```

---

## ☁️ Streamlit Cloud Specific Notes

### Required Files for Streamlit Cloud:
- `requirements.txt` - Python packages (already configured)
- `packages.txt` - System packages (already configured):
  ```
  libgl1-mesa-glx
  libglib2.0-0
  ```

### Configuration:
The app is configured for Streamlit Cloud with:
- Headless mode enabled
- Proper port binding (8501)
- No local-only dependencies
- OpenCV headless version
- Compatible pinned versions

### Camera Access on Streamlit Cloud:
- Camera access works in browser (HTTPS required)
- Users must grant camera permission
- Works on mobile and desktop browsers
- For best results: use Chrome/Edge, good lighting, contrasting clothing

---

## 🐳 Docker Deployment Details

### Production Image Features:
- Multi-stage build for smaller size (~500MB)
- Non-root user for security
- Health checks included
- Optimized layer caching
- Only runtime dependencies in final image

### Environment Variables:
```bash
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_HEADLESS=true
STREAMLIT_SERVER_ADDRESS=0.0.0.0
STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
STREAMLIT_THEME_BASE=dark
```

### Volumes (Optional):
```yaml
volumes:
  - ./streamlit_app_enhanced.py:/app/streamlit_app_enhanced.py:ro
```
Mount for live code updates without rebuild.

---

## 🔧 Customization

### Branding & Colors:
Edit CSS variables in `streamlit_app_enhanced.py`:
```css
:root {
    --primary: #0f0f1a;       /* Main background */
    --accent: #e94560;        /* Primary brand color */
    --accent-light: #f47c6f;  /* Accent highlight */
    --success: #07b38c;       /* Success green */
    --warning: #f6ae2d;       /* Warning amber */
    --info: #4dabf7;          /* Info blue */
}
```

### Adding Exercises:
1. Add to `st.session_state.exercises` dictionary
2. Create analyzer function following existing pattern
3. Add to `ANALYZERS` mapping
4. Include icon, type (reps/hold), camera hint, targets, description, steps

### Data Export:
- CSV: Opens in Excel/Google Sheets for charts
- JSON: Structured data for programmatic analysis
- Session history persists in browser session

---

## 📱 Investor Demo Checklist

### Pre-Demo Setup:
- [ ] Deploy to Streamlit Cloud (5 min)
- [ ] Test on phone (different network)
- [ ] Test on laptop with external webcam
- [ ] Verify camera permissions work
- [ ] Export sample CSV/JSON data
- [ ] Prepare talking points

### Demo Flow:
1. **Open URL** → Show landing page with exercise cards
2. **Select Squat** → Explain real-time pose detection
3. **Start Monitoring** → Show camera feed with landmarks
4. **Perform reps** → Demonstrate form feedback (green/yellow/red)
5. **Stop & Export** → Show data download
6. **History Tab** → Show session tracking

### Talking Points:
- "Real-time 33-keypoint pose detection via MediaPipe"
- "Automated form analysis with actionable feedback"
- "Rep counting & hold timing with angle measurement"
- "Zero-install web app - works on any device"
- "Exportable data for progress tracking & coaching"
- "Scalable architecture - Docker + Kubernetes ready"

### Backup Plan:
- Screenshots of each exercise flow
- Pre-recorded video demo
- Sample exported data files

---

## 🐛 Troubleshooting

### Common Issues:

| Problem | Solution |
|---------|----------|
| Camera not accessible | Grant browser permission; use HTTPS; try external webcam |
| Low frame rate | Close other camera apps; reduce resolution in code |
| Pose not detecting | Ensure good lighting; wear contrasting colors; face camera properly |
| Feedback delayed | Lower `min_detection_confidence` to 0.3 |
| Export button not working | Complete a session first (start → exercise → stop) |
| App won't start | `pip install -r requirements.txt` |
| Docker build fails | Check Docker daemon running; try `docker system prune` |

### Streamlit Cloud Specific:
- First deploy downloads models (~100MB) - wait 2-3 minutes
- Camera requires HTTPS (automatic on Streamlit Cloud)
- Mobile browsers need explicit camera permission
- Free tier has resource limits - upgrade for heavy usage

### Docker Specific:
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
```

---

## 🔒 Security Considerations

- Camera access only with explicit user permission
- No data stored server-side (client-side only)
- No authentication by default - add if needed
- Run behind reverse proxy (Nginx) in production
- Use HTTPS in production
- Rate limiting configured in Nginx
- Non-root container user

---

## 📈 Scaling & Production

### For Higher Loads:
1. **Multiple replicas:** `docker-compose up -d --scale gym-trainer=3`
2. **Load balancer:** Nginx upstream with multiple servers
3. **Kubernetes:** Deploy with HPA based on CPU/memory
4. **CDN:** CloudFlare for static assets

### Monitoring:
- Health endpoint: `/_stcore/health`
- Streamlit metrics: `/_stcore/metrics`
- Container logs: `docker-compose logs`

### Database (Future):
Add Redis/PostgreSQL for:
- Persistent session history
- Multi-user support
- Analytics dashboard

---

## 📞 Support

- **Issues:** GitHub Issues
- **Docs:** This file + inline code comments
- **Streamlit Docs:** https://docs.streamlit.io
- **MediaPipe Docs:** https://mediapipe.dev
- **Docker Docs:** https://docs.docker.com

---

## 🎯 Next Steps for Production

1. **Add authentication** (Streamlit Auth, Auth0, or custom)
2. **Database integration** for persistent history
3. **User profiles** with preferences
4. **Progress charts** (weekly/monthly trends)
5. **Exercise library** with video demonstrations
6. **Coach dashboard** for remote training
7. **Mobile app** (React Native + WebView)
8. **API** for third-party integrations

---

**Ready to deploy!** Choose your platform and follow the quick start above.