import streamlit as st
import os, json, base64, io, subprocess, tempfile, time, random
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
import requests

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="QuietMind Reels",
    page_icon="✨",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# ── Custom CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,300;0,400;0,600;1,300;1,400&family=DM+Sans:wght@300;400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

/* Page background */
.stApp {
    background: #0a0a0f;
    color: #e8e0d0;
}

/* Hide streamlit default elements */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 2rem; padding-bottom: 4rem; max-width: 680px; }

/* Hero heading */
.hero-title {
    font-family: 'Cormorant Garamond', serif;
    font-size: 3.2rem;
    font-weight: 300;
    letter-spacing: 0.06em;
    color: #f0e8d8;
    text-align: center;
    line-height: 1.15;
    margin-bottom: 0.2rem;
}
.hero-sub {
    font-family: 'DM Sans', sans-serif;
    font-size: 0.85rem;
    font-weight: 300;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: #8a7d6a;
    text-align: center;
    margin-bottom: 2.5rem;
}
.divider {
    width: 60px; height: 1px;
    background: linear-gradient(90deg, transparent, #c9a96e, transparent);
    margin: 1.2rem auto 2rem;
}

/* Labels */
label, .stTextArea label, .stTextInput label {
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.72rem !important;
    letter-spacing: 0.15em !important;
    text-transform: uppercase !important;
    color: #7a6e60 !important;
    font-weight: 500 !important;
}

/* Inputs */
.stTextArea textarea, .stTextInput input {
    background: #111118 !important;
    border: 1px solid #2a2820 !important;
    border-radius: 4px !important;
    color: #e8e0d0 !important;
    font-family: 'Cormorant Garamond', serif !important;
    font-size: 1.15rem !important;
    font-weight: 300 !important;
    padding: 14px 16px !important;
    caret-color: #c9a96e;
    transition: border-color 0.3s ease !important;
}
.stTextArea textarea:focus, .stTextInput input:focus {
    border-color: #c9a96e !important;
    box-shadow: 0 0 0 1px rgba(201,169,110,0.15) !important;
}

/* Generate button */
.stButton > button {
    width: 100%;
    background: transparent !important;
    border: 1px solid #c9a96e !important;
    color: #c9a96e !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.75rem !important;
    font-weight: 500 !important;
    letter-spacing: 0.22em !important;
    text-transform: uppercase !important;
    padding: 14px 28px !important;
    border-radius: 2px !important;
    cursor: pointer !important;
    transition: all 0.3s ease !important;
    margin-top: 0.5rem;
}
.stButton > button:hover {
    background: rgba(201,169,110,0.08) !important;
    box-shadow: 0 0 24px rgba(201,169,110,0.12) !important;
}

/* Selectbox */
.stSelectbox > div > div {
    background: #111118 !important;
    border: 1px solid #2a2820 !important;
    border-radius: 4px !important;
    color: #e8e0d0 !important;
}
.stSelectbox svg { color: #8a7d6a !important; }

/* Status / info boxes */
.step-badge {
    display: inline-block;
    background: rgba(201,169,110,0.1);
    border: 1px solid rgba(201,169,110,0.3);
    border-radius: 2px;
    padding: 4px 12px;
    font-size: 0.72rem;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: #c9a96e;
    margin-bottom: 0.6rem;
}
.status-line {
    font-size: 0.82rem;
    color: #8a7d6a;
    letter-spacing: 0.04em;
    margin: 0.25rem 0;
}
.status-line.done { color: #a8c4a0; }
.status-line.active { color: #e8e0d0; }

/* Preview image */
.preview-wrap {
    border: 1px solid #2a2820;
    border-radius: 4px;
    overflow: hidden;
    margin: 1.5rem 0;
}

/* Download button */
.dl-btn {
    display: block;
    width: 100%;
    background: linear-gradient(135deg, #1a1508, #2a2010) !important;
    border: 1px solid #c9a96e !important;
    color: #c9a96e !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 0.78rem !important;
    font-weight: 500 !important;
    letter-spacing: 0.18em !important;
    text-transform: uppercase !important;
    padding: 14px !important;
    border-radius: 2px !important;
    text-align: center;
    box-shadow: 0 4px 24px rgba(201,169,110,0.08);
}

/* Sidebar / API key section */
.api-box {
    background: #0e0e14;
    border: 1px solid #1e1e28;
    border-radius: 4px;
    padding: 1.2rem;
    margin-bottom: 1.5rem;
}
.api-box p {
    font-size: 0.8rem;
    color: #6a5e52;
    margin: 0 0 0.8rem;
    letter-spacing: 0.03em;
}
.api-box a { color: #c9a96e; text-decoration: none; }

/* Progress bar override */
.stProgress > div > div > div {
    background: linear-gradient(90deg, #c9a96e, #e8c878) !important;
    border-radius: 2px !important;
}
.stProgress > div > div {
    background: #1a1a24 !important;
    border-radius: 2px !important;
}

/* Video player */
.stVideo { border-radius: 4px; overflow: hidden; }

/* Expander */
.streamlit-expanderHeader {
    font-size: 0.75rem !important;
    letter-spacing: 0.12em !important;
    text-transform: uppercase !important;
    color: #6a5e52 !important;
}

/* Columns gap */
[data-testid="column"] { padding: 0 8px; }
</style>
""", unsafe_allow_html=True)

# ── Constants ──────────────────────────────────────────────────────────────────
REEL_W, REEL_H = 1080, 1920
FPS            = 30
DURATION       = 5
TOTAL_FRAMES   = FPS * DURATION

GEMINI_IMG_URL  = "https://generativelanguage.googleapis.com/v1beta/models/imagen-3.0-generate-001:predict"
GEMINI_TEXT_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"

FONT_BOLD   = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
FONT_LIGHT  = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_ITALIC = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Italic.ttf"

WATERMARK_OPTIONS = ["@quietmind", "@yourbrand", ""]

# ── Gemini API ─────────────────────────────────────────────────────────────────

def ask_gemini_prompt(quote: str, api_key: str) -> str:
    system = (
        "You are a cinematic art director. Given a quote, craft a detailed image-generation "
        "prompt (max 75 words) for an atmospheric background image that matches the quote's "
        "mood, theme, and emotion. The scene should be cinematic, moody, beautiful. "
        "No text, no words, no letters in the image. No human faces. "
        "Focus on landscapes, abstract light, textures, nature, architecture. "
        "Reply with ONLY the prompt, nothing else."
    )
    payload = {
        "system_instruction": {"parts": [{"text": system}]},
        "contents": [{"parts": [{"text": f'Quote: "{quote}"'}]}],
        "generationConfig": {"maxOutputTokens": 120, "temperature": 0.95}
    }
    r = requests.post(GEMINI_TEXT_URL, headers={"Content-Type": "application/json"},
                      params={"key": api_key}, json=payload, timeout=30)
    r.raise_for_status()
    return r.json()["candidates"][0]["content"]["parts"][0]["text"].strip()


def generate_background(prompt: str, api_key: str) -> Image.Image:
    payload = {
        "instances": [{"prompt": prompt}],
        "parameters": {
            "sampleCount": 1,
            "aspectRatio": "9:16",
            "safetyFilterLevel": "block_few",
            "personGeneration": "dont_allow"
        }
    }
    r = requests.post(GEMINI_IMG_URL, headers={"Content-Type": "application/json"},
                      params={"key": api_key}, json=payload, timeout=60)
    if r.status_code != 200:
        raise RuntimeError(f"Imagen API error {r.status_code}: {r.text[:300]}")
    b64 = r.json()["predictions"][0]["bytesBase64Encoded"]
    return Image.open(io.BytesIO(base64.b64decode(b64))).convert("RGB")


# ── Rendering ──────────────────────────────────────────────────────────────────

def ease_inout(t):
    return t * t * (3 - 2 * t)

def frame_alpha(p):
    if p < 0.15:   return ease_inout(p / 0.15)
    if p > 0.82:   return ease_inout((1 - p) / 0.18)
    return 1.0

def detect_colors(img: Image.Image):
    small = img.resize((30, 30))
    pixels = list(small.getdata())
    avg = tuple(int(sum(c[i] for c in pixels) / len(pixels)) for i in range(3))
    bright = (avg[0]*299 + avg[1]*587 + avg[2]*114) / 1000
    if bright > 140:
        return (20, 15, 10), (180, 120, 40)
    return (245, 238, 220), (210, 175, 105)

def apply_vignette(img: Image.Image) -> Image.Image:
    v = Image.new("L", (REEL_W, REEL_H), 0)
    d = ImageDraw.Draw(v)
    cx, cy = REEL_W // 2, REEL_H // 2
    for i in range(80, 0, -1):
        r = int(50 + 205 * i / 80)
        w, h = int(REEL_W * i / 80 * 0.9), int(REEL_H * i / 80 * 0.9)
        d.ellipse([cx-w, cy-h, cx+w, cy+h], fill=r)
    v = v.filter(ImageFilter.GaussianBlur(80))
    rgba = img.convert("RGBA")
    vig_rgba = Image.merge("RGBA", [
        Image.new("L", (REEL_W, REEL_H), 0), Image.new("L", (REEL_W, REEL_H), 0),
        Image.new("L", (REEL_W, REEL_H), 0),
        ImageEnhance.Brightness(v).enhance(0.55)
    ])
    return Image.alpha_composite(rgba, vig_rgba).convert("RGB")

def prep_bg(img: Image.Image, progress: float) -> Image.Image:
    zoom = 1.10 - 0.10 * progress
    tw, th = int(REEL_W * zoom), int(REEL_H * zoom)
    bg = img.resize((tw, th), Image.LANCZOS)
    l, t = (tw - REEL_W) // 2, (th - REEL_H) // 2
    bg = bg.crop((l, t, l + REEL_W, t + REEL_H))
    bg = bg.filter(ImageFilter.GaussianBlur(1.0))
    bg = apply_vignette(bg)
    bg = ImageEnhance.Brightness(bg).enhance(0.52)
    bg = ImageEnhance.Color(bg).enhance(0.78)
    return bg

def load_font(path, size):
    try:    return ImageFont.truetype(path, size)
    except: return ImageFont.load_default()

def wrap_text(draw, text, font, max_w):
    words, lines, cur = text.split(), [], ""
    for w in words:
        test = (cur + " " + w).strip()
        bbox = draw.textbbox((0, 0), test, font=font)
        if bbox[2] - bbox[0] <= max_w: cur = test
        else:
            if cur: lines.append(cur)
            cur = w
    if cur: lines.append(cur)
    return lines

def render_frame(bg: Image.Image, quote: str, author: str, watermark: str,
                 progress: float, tc, ac) -> Image.Image:
    frame = prep_bg(bg, progress).convert("RGBA")
    alpha_val = int(255 * frame_alpha(progress))
    drift = int((1 - frame_alpha(progress)) * 32)

    ov = Image.new("RGBA", (REEL_W, REEL_H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(ov)

    fq  = load_font(FONT_BOLD,   66)
    fau = load_font(FONT_ITALIC, 44)
    fwm = load_font(FONT_LIGHT,  30)
    foq = load_font(FONT_BOLD,  190)

    # Big quote mark
    draw.text((68, REEL_H // 2 - 490 + drift), "\u201c",
              font=foq, fill=(*ac, min(alpha_val, 65)))

    # Quote text
    lines = wrap_text(draw, quote, fq, REEL_W - 160)
    lh = 86
    total_h = len(lines) * lh
    sy = REEL_H // 2 - total_h // 2 + drift
    for i, line in enumerate(lines):
        bbox = draw.textbbox((0, 0), line, font=fq)
        x = (REEL_W - (bbox[2] - bbox[0])) // 2
        y = sy + i * lh
        draw.text((x+3, y+3), line, font=fq, fill=(0, 0, 0, min(alpha_val, 110)))
        draw.text((x, y), line, font=fq, fill=(*tc, alpha_val))

    # Divider
    dy = sy + total_h + 38 + drift
    draw.line([(REEL_W//2 - 200, dy), (REEL_W//2 + 200, dy)],
              fill=(*ac, min(alpha_val, 170)), width=2)

    # Author
    if author:
        txt = f"— {author}"
        bbox = draw.textbbox((0, 0), txt, font=fau)
        draw.text(((REEL_W - (bbox[2]-bbox[0]))//2, dy + 22 + drift),
                  txt, font=fau, fill=(*ac, alpha_val))

    # Watermark
    if watermark:
        bbox = draw.textbbox((0, 0), watermark, font=fwm)
        draw.text(((REEL_W - (bbox[2]-bbox[0]))//2, REEL_H - 105),
                  watermark, font=fwm, fill=(*tc, min(alpha_val, 75)))

    return Image.alpha_composite(frame, ov).convert("RGB")


def encode_video(frames_dir: Path, out_path: Path):
    cmd = [
        "ffmpeg", "-y",
        "-framerate", str(FPS),
        "-i", str(frames_dir / "frame_%04d.png"),
        "-c:v", "libx264", "-preset", "fast", "-crf", "18",
        "-pix_fmt", "yuv420p",
        "-vf", f"scale={REEL_W}:{REEL_H}",
        str(out_path)
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f"FFmpeg error:\n{result.stderr[-500:]}")


# ── UI ─────────────────────────────────────────────────────────────────────────

st.markdown('<h1 class="hero-title">QuietMind Reels</h1>', unsafe_allow_html=True)
st.markdown('<p class="hero-sub">AI · Quote · Reel Generator</p>', unsafe_allow_html=True)
st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

# API Key
with st.expander("🔑  Gemini API Key", expanded="api_key" not in st.session_state):
    st.markdown("""
    <div class="api-box">
    <p>Get a free key at <a href="https://aistudio.google.com/apikey" target="_blank">aistudio.google.com/apikey</a> — no credit card needed.</p>
    </div>
    """, unsafe_allow_html=True)
    api_key_input = st.text_input("API Key", type="password",
                                   placeholder="AIza...",
                                   label_visibility="collapsed")
    if api_key_input:
        st.session_state["api_key"] = api_key_input

api_key = st.session_state.get("api_key", os.environ.get("GEMINI_API_KEY", ""))

st.markdown("<br>", unsafe_allow_html=True)

# Quote input
quote = st.text_area(
    "Your Quote",
    placeholder="Enter a quote that moves you…",
    height=120,
    max_chars=280
)

col1, col2 = st.columns(2)
with col1:
    author = st.text_input("Author", placeholder="e.g. Rumi")
with col2:
    watermark = st.text_input("Watermark", placeholder="e.g. @yourbrand", value="@quietmind")

st.markdown("<br>", unsafe_allow_html=True)
generate_btn = st.button("✦  Generate Reel")

# ── Generation pipeline ────────────────────────────────────────────────────────

if generate_btn:
    if not quote.strip():
        st.error("Please enter a quote.")
        st.stop()
    if not api_key:
        st.error("Please enter your Gemini API key above.")
        st.stop()

    status_area = st.empty()

    def show_status(steps):
        html = '<div style="background:#0e0e14;border:1px solid #1e1e28;border-radius:4px;padding:1.2rem 1.4rem;margin:0.8rem 0">'
        for label, state in steps:
            cls = {"done": "done", "active": "active", "wait": ""}.get(state, "")
            icon = {"done": "✓", "active": "◌", "wait": "·"}[state]
            html += f'<p class="status-line {cls}">{icon}  {label}</p>'
        html += "</div>"
        status_area.markdown(html, unsafe_allow_html=True)

    prog_bar  = st.progress(0)
    prog_text = st.empty()

    # ── Step 1: image prompt ──
    show_status([
        ("Asking Gemini to read the quote…", "active"),
        ("Generating background image", "wait"),
        ("Rendering 150 frames", "wait"),
        ("Encoding MP4", "wait"),
    ])
    prog_bar.progress(5)

    try:
        img_prompt = ask_gemini_prompt(quote.strip(), api_key)
    except Exception as e:
        st.error(f"Gemini text API error: {e}")
        st.stop()

    with st.expander("💬  Generated image prompt", expanded=False):
        st.caption(img_prompt)

    # ── Step 2: generate image ──
    show_status([
        ("Quote analysed", "done"),
        ("Generating background with Imagen 3…", "active"),
        ("Rendering 150 frames", "wait"),
        ("Encoding MP4", "wait"),
    ])
    prog_bar.progress(15)

    try:
        bg_img = generate_background(img_prompt, api_key)
        bg_img = bg_img.resize((REEL_W, REEL_H), Image.LANCZOS)
    except Exception as e:
        st.error(f"Imagen 3 API error: {e}")
        st.stop()

    # Show background preview
    preview_w = 320
    preview_h = int(preview_w * REEL_H / REEL_W)
    preview = bg_img.resize((preview_w, preview_h), Image.LANCZOS)
    st.image(preview, caption="AI-generated background", use_container_width=False)

    tc, ac = detect_colors(bg_img)

    # ── Step 3: render frames ──
    show_status([
        ("Quote analysed", "done"),
        ("Background image generated", "done"),
        ("Rendering 150 frames…", "active"),
        ("Encoding MP4", "wait"),
    ])

    with tempfile.TemporaryDirectory() as tmp:
        frames_dir = Path(tmp) / "frames"
        frames_dir.mkdir()
        out_path = Path(tmp) / "reel.mp4"

        for i in range(TOTAL_FRAMES):
            p = i / (TOTAL_FRAMES - 1)
            frame = render_frame(bg_img, quote.strip(), author.strip(),
                                 watermark.strip(), p, tc, ac)
            frame.save(frames_dir / f"frame_{i:04d}.png", "PNG")
            pct = 15 + int((i / TOTAL_FRAMES) * 65)
            prog_bar.progress(pct)
            if i % 25 == 0:
                prog_text.caption(f"Rendering frame {i+1} / {TOTAL_FRAMES}")

        prog_text.empty()

        # ── Step 4: encode ──
        show_status([
            ("Quote analysed", "done"),
            ("Background image generated", "done"),
            ("150 frames rendered", "done"),
            ("Encoding MP4…", "active"),
        ])
        prog_bar.progress(82)

        try:
            encode_video(frames_dir, out_path)
        except Exception as e:
            st.error(f"FFmpeg encoding failed: {e}")
            st.stop()

        prog_bar.progress(100)
        show_status([
            ("Quote analysed", "done"),
            ("Background image generated", "done"),
            ("150 frames rendered", "done"),
            ("MP4 encoded ✓", "done"),
        ])

        # ── Result ──
        video_bytes = out_path.read_bytes()

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### ✦  Your Reel")
    st.video(video_bytes)

    safe = "".join(c if c.isalnum() else "_" for c in quote.strip()[:30])
    st.download_button(
        label="⬇  Download Reel (MP4)",
        data=video_bytes,
        file_name=f"reel_{safe}.mp4",
        mime="video/mp4",
        use_container_width=True
    )

    st.markdown("<br>", unsafe_allow_html=True)
    st.caption("1080 × 1920 · H.264 · 5 sec · 30 fps · Ready for Instagram Reels")

