# AI Virtual Gym Trainer - Deployment Package

## 📁 Folder Contents

| File | Purpose |
|------|---------|
| `streamlit_app.py` | **Main web app** - Run this for your investor demo |
| `requirements.txt` | Python dependencies (pinned for Streamlit Cloud) |
| `packages.txt` | System dependencies (required for OpenCV on Streamlit Cloud) |
| `README_DEPLOYMENT.md` | Detailed deployment guide |
| `exercise_selector.py` | Original Tkinter desktop app (reference only) |

---

## 🚀 Quick Deploy to Streamlit Cloud (Like claude.ai)

### 1. Create GitHub Repo & Upload
```bash
# In this folder:
git init
git add .
git commit -m "Deploy: AI Virtual Gym Trainer web demo"
# Then create repo on GitHub and push
```

### 2. Deploy on Streamlit Cloud
1. Go to https://share.streamlit.io
2. Click **"New app"**
3. Select your repo → Main file: `streamlit_app.py`
4. Click **"Deploy"**

### 3. Get Your Public URL
- Format: `https://your-repo-name.streamlitapp.com`
- Works from **any device** (phone, laptop, tablet)
- Works **anywhere** with internet
- **No installation** needed for viewers

---

## 💻 Local Testing

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```
Opens at `http://localhost:8501`

---

## 📱 For November 30, 2026 Investor Presentation

1. **Deploy to Streamlit Cloud** (5 minutes)
2. **Test on your phone** (different network)
3. **Share the URL** with investors
4. **They can access from anywhere** - just like opening claude.ai

---

## ⚡ Key Fixes for Cloud Deployment

- ✅ `opencv-python-headless` (not `opencv-python`)
- ✅ Pinned compatible versions
- ✅ `packages.txt` with `libgl1-mesa-glx` & `libglib2.0-0`
- ✅ Removed `ImageTk` (Tkinter - desktop only)
- ✅ Replaced `StringIO` with `BytesIO` for binary images
- ✅ No local-only dependencies

---

**Ready to deploy!** Just upload this folder to GitHub and connect to Streamlit Cloud.