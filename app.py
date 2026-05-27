import streamlit as st
from google import genai
from google.oauth2 import service_account
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
from io import BytesIO
import tempfile
import subprocess
import os
import json
from pathlib import Path

# ---------------- PAGE CONFIG ----------------

st.set_page_config(
page_title="AI Quote Reel Generator",
page_icon="🎬",
layout="centered"
)

# ---------------- GOOGLE AUTH ----------------

service_account_info = dict(st.secrets["gcp_service_account"])

credentials = service_account.Credentials.from_service_account_info(
service_account_info
)

with open("temp_credentials.json", "w") as f:
json.dump(service_account_info, f)

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "temp_credentials.json"

# ---------------- GEMINI CLIENT ----------------

client = genai.Client(
vertexai=True,
project=st.secrets["PROJECT_ID"],
location=st.secrets["LOCATION"],
)

# ---------------- CONSTANTS ----------------

REEL_W = 1080
REEL_H = 1920
FPS = 30
DURATION = 5
TOTAL_FRAMES = FPS * DURATION

FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"

# ---------------- UI ----------------

st.title("🎬 AI Quote Reel Generator")

quote = st.text_area(
"Enter Your Quote",
height=150,
placeholder="Type your quote..."
)

author = st.text_input(
"Author Name",
placeholder="Author"
)

watermark = st.text_input(
"Watermark",
value="@yourpage"
)

generate = st.button("Generate Reel")

# ---------------- PROMPT GENERATION ----------------

def generate_prompt(quote):

```
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=f"""
    Create a cinematic vertical image prompt for Instagram reel background.

    Quote:
    "{quote}"

    Requirements:
    - emotional
    - aesthetic
    - cinematic
    - moody lighting
    - no text
    - no watermark
    - ultra realistic
    - vertical composition
    - highly detailed
    - dramatic atmosphere

    Return ONLY prompt.
    """
)

return response.text.strip()
```

# ---------------- IMAGE GENERATION ----------------

def generate_background(prompt):

```
response = client.models.generate_images(
    model="imagen-3.0-generate-002",
    prompt=prompt,
    config={
        "number_of_images": 1,
        "aspect_ratio": "9:16"
    }
)

image_bytes = response.generated_images[0].image.image_bytes

img = Image.open(BytesIO(image_bytes)).convert("RGB")

return img
```

# ---------------- VIGNETTE ----------------

def apply_vignette(img):

```
vignette = Image.new("L", img.size, 0)

draw = ImageDraw.Draw(vignette)

width, height = img.size

for i in range(350):

    alpha = int(255 * (i / 350))

    draw.ellipse(
        (
            i,
            i,
            width - i,
            height - i
        ),
        fill=alpha
    )

vignette = vignette.filter(ImageFilter.GaussianBlur(120))

black = Image.new("RGB", img.size, "black")

img = Image.composite(img, black, vignette)

return img
```

# ---------------- TEXT WRAP ----------------

def wrap_text(draw, text, font, max_width):

```
words = text.split()

lines = []

current = ""

for word in words:

    test = current + " " + word

    bbox = draw.textbbox((0,0), test, font=font)

    width = bbox[2] - bbox[0]

    if width <= max_width:
        current = test
    else:
        lines.append(current.strip())
        current = word

lines.append(current.strip())

return lines
```

# ---------------- FRAME RENDER ----------------

def render_frame(bg, quote, author, watermark, progress):

```
zoom = 1.12 - (0.12 * progress)

new_w = int(REEL_W * zoom)
new_h = int(REEL_H * zoom)

bg_zoom = bg.resize((new_w, new_h))

left = (new_w - REEL_W) // 2
top = (new_h - REEL_H) // 2

bg_crop = bg_zoom.crop(
    (
        left,
        top,
        left + REEL_W,
        top + REEL_H
    )
)

bg_crop = apply_vignette(bg_crop)

overlay = Image.new(
    "RGBA",
    (REEL_W, REEL_H),
    (0,0,0,0)
)

draw = ImageDraw.Draw(overlay)

quote_font = ImageFont.truetype(FONT_PATH, 70)

lines = wrap_text(
    draw,
    quote,
    quote_font,
    REEL_W - 180
)

line_height = 90

total_height = len(lines) * line_height

start_y = (REEL_H // 2) - (total_height // 2)

alpha = int(255 * min(progress * 2, 1))

for i, line in enumerate(lines):

    bbox = draw.textbbox((0,0), line, font=quote_font)

    text_width = bbox[2] - bbox[0]

    x = (REEL_W - text_width) // 2

    y = start_y + (i * line_height)

    draw.text(
        (x+4, y+4),
        line,
        font=quote_font,
        fill=(0,0,0,130)
    )

    draw.text(
        (x, y),
        line,
        font=quote_font,
        fill=(255,255,255,alpha)
    )

# Author

if author:

    author_font = ImageFont.truetype(FONT_PATH, 40)

    author_text = f"— {author}"

    bbox = draw.textbbox((0,0), author_text, font=author_font)

    width = bbox[2] - bbox[0]

    draw.text(
        (
            (REEL_W - width) // 2,
            start_y + total_height + 60
        ),
        author_text,
        font=author_font,
        fill=(255,220,180,alpha)
    )

# Watermark

watermark_font = ImageFont.truetype(FONT_PATH, 30)

bbox = draw.textbbox((0,0), watermark, font=watermark_font)

width = bbox[2] - bbox[0]

draw.text(
    (
        (REEL_W - width) // 2,
        REEL_H - 120
    ),
    watermark,
    font=watermark_font,
    fill=(255,255,255,80)
)

final = Image.alpha_composite(
    bg_crop.convert("RGBA"),
    overlay
)

return final.convert("RGB")
```

# ---------------- VIDEO ENCODING ----------------

def encode_video(frames_dir, output_path):

```
cmd = [
    "ffmpeg",
    "-y",
    "-framerate",
    str(FPS),
    "-i",
    str(frames_dir / "frame_%04d.png"),
    "-c:v",
    "libx264",
    "-preset",
    "medium",
    "-crf",
    "18",
    "-pix_fmt",
    "yuv420p",
    str(output_path)
]

subprocess.run(
    cmd,
    check=True
)
```

# ---------------- GENERATION ----------------

if generate:

```
if not quote:
    st.error("Please enter quote")
    st.stop()

with st.spinner("Generating cinematic prompt..."):

    prompt = generate_prompt(quote)

st.success("Prompt generated")

with st.expander("Generated Prompt"):
    st.write(prompt)

with st.spinner("Generating AI image..."):

    bg = generate_background(prompt)

st.image(
    bg,
    caption="AI Generated Background"
)

with tempfile.TemporaryDirectory() as tmpdir:

    tmpdir = Path(tmpdir)

    frames_dir = tmpdir / "frames"

    frames_dir.mkdir()

    video_path = tmpdir / "quote_reel.mp4"

    progress_bar = st.progress(0)

    status = st.empty()

    for i in range(TOTAL_FRAMES):

        progress = i / TOTAL_FRAMES

        frame = render_frame(
            bg,
            quote,
            author,
            watermark,
            progress
        )

        frame.save(
            frames_dir / f"frame_{i:04d}.png"
        )

        progress_bar.progress(
            int((i / TOTAL_FRAMES) * 100)
        )

        status.text(
            f"Rendering frame {i+1}/{TOTAL_FRAMES}"
        )

    status.text("Encoding reel...")

    encode_video(
        frames_dir,
        video_path
    )

    video_bytes = open(
        video_path,
        "rb"
    ).read()

    st.success("Reel generated successfully!")

    st.video(video_bytes)

    st.download_button(
        "Download Reel",
        video_bytes,
        file_name="instagram_quote_reel.mp4",
        mime="video/mp4"
    )
```
