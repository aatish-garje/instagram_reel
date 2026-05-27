# 📱✨ QuietMind Reels — Streamlit App

AI-powered Instagram Quote Reel generator using Google Gemini (Imagen 3).

---

## Local Setup

```bash
# 1. Install dependencies (ffmpeg is required)
pip install streamlit pillow requests

# macOS
brew install ffmpeg

# Ubuntu / Debian
sudo apt install ffmpeg

# 2. Get a free Gemini API key
#    → https://aistudio.google.com/apikey

# 3. (Optional) Set key as environment variable
export GEMINI_API_KEY="your_key_here"

# 4. Run
streamlit run app.py
```

Open http://localhost:8501 in your browser.

---

## Deploy to Streamlit Cloud (Free)

1. Push your files to a **GitHub repo**:
   ```
   app.py
   requirements.txt
   packages.txt        ← create this (see below)
   ```

2. Create `packages.txt` in the repo root:
   ```
   ffmpeg
   ```
   This tells Streamlit Cloud to install ffmpeg via apt.

3. Go to → https://share.streamlit.io
   - Connect your GitHub repo
   - Set main file: `app.py`
   - Under **Secrets**, add:
     ```toml
     GEMINI_API_KEY = "your_key_here"
     ```
   - Deploy!

---

## Project Files

| File | Purpose |
|---|---|
| `app.py` | Streamlit web app (UI + pipeline) |
| `requirements.txt` | Python dependencies |
| `packages.txt` | System packages (ffmpeg) for Streamlit Cloud |
| `.streamlit/secrets.toml` | Local secrets (do NOT commit to git) |

---

## How It Works

```
Quote entered by user
      │
      ▼
[Gemini Flash]   Reads quote → writes cinematic image prompt
      │
      ▼
[Imagen 3]       Generates AI background image (9:16)
      │
      ▼
[Pillow]         Renders 150 frames with:
                   • Ken Burns slow zoom (110%→100%)
                   • Cinematic vignette darkening
                   • Fade-in / fade-out animation
                   • Quote + author text overlay
                   • Auto accent color detection
      │
      ▼
[FFmpeg]         Encodes frames → 1080×1920 H.264 MP4
      │
      ▼
Download button in browser ✅
```

---

## Output Specs

| | |
|---|---|
| Resolution | 1080 × 1920 (9:16 Instagram) |
| Duration | 5 seconds |
| Frame rate | 30 fps |
| Codec | H.264 (MP4) |
| File size | ~1–3 MB |
