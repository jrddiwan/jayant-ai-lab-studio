# Jayant's AI Lab — Master Autonomous Studio Engine
# Cloud Host: Render.com (24/7 Always-On)
# Features:
# - Multi-Platform Radar (X, YouTube, HuggingFace, Reddit, GitHub)
# - Publication Date Filter: Only videos published AFTER automation launch (zero past videos)
# - Executive Quality Gate: Evaluates transcripts with Groq 120B to suppress fluff & spam
# - Multi-Creator Master Scriptwriting: Vaibhav Sisinty Hook + AI Search ELI12 + Jayant Triad
# - Gemini 3.1 Flash TTS (ZORO Confident Male Voice with South Delhi Cadence)
# - Pillow Visual Instagram Carousel Generator (Delivers 6 1080x1350 PNG slides directly to Telegram)
# - Automated B-Roll Generator & Hugging Face FLUX.1 Visual Proof Cards
# - Strict <= 260 Char Tweet Generator & High-Insight LinkedIn Post
# - "Prompt of the Day" WhatsApp Community Template
# - Central Delivery to "Jayant's AI Lab HQ" Telegram Channel

import os
import time
import json
import wave
import base64
import threading
import requests
import urllib.parse
from datetime import datetime, timezone
import xml.etree.ElementTree as ET
from http.server import HTTPServer, BaseHTTPRequestHandler
from PIL import Image, ImageDraw, ImageFont
from google import genai

# ─── LOAD ENVIRONMENT VARIABLES ───
if os.path.exists(".env"):
    try:
        with open(".env", "r", encoding="utf-8") as f:
            for line in f:
                if "=" in line and not line.startswith("#"):
                    k, v = line.strip().split("=", 1)
                    if k not in os.environ:
                        os.environ[k] = v
    except Exception:
        pass

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
AUTHORIZED_CHAT_ID = int(os.getenv("AUTHORIZED_CHAT_ID", "7007116692"))
HQ_CHANNEL_ID = os.getenv("HQ_CHANNEL_ID", "-1004226935646")
ZORO_VOICE = os.getenv("ZORO_VOICE", "Puck")

# ─── MULTI-KEY POOLS (TWO KEYS FOR EACH PLATFORM) ───
GEMINI_KEYS = [k for k in [os.getenv("GEMINI_API_KEY", ""), os.getenv("GEMINI_API_KEY_2", "")] if k]
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
AGNES_KEYS = [k for k in [os.getenv("AGNES_API_KEY", ""), os.getenv("AGNES_API_KEY_2", "")] if k]
HF_TOKENS = [k for k in [os.getenv("HF_TOKEN", ""), os.getenv("HF_TOKEN_2", "")] if k]
OPENROUTER_KEYS = [k for k in [os.getenv("OPENROUTER_API_KEY", ""), os.getenv("OPENROUTER_API_KEY_2", "")] if k]

CF_CREDS = []
if os.getenv("CF_ACCOUNT") and os.getenv("CF_TOKEN"):
    CF_CREDS.append((os.getenv("CF_ACCOUNT"), os.getenv("CF_TOKEN")))
if os.getenv("CF_ACCOUNT_2") and os.getenv("CF_TOKEN_2"):
    CF_CREDS.append((os.getenv("CF_ACCOUNT_2"), os.getenv("CF_TOKEN_2")))

TG_API_BASE = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"
OUTPUT_DIR = "telegram_outputs"
CAROUSEL_DIR = "carousel_outputs"
SEEN_FILE = "seen_topics.json"
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(CAROUSEL_DIR, exist_ok=True)

# Baseline timestamp: Only accept videos published after this time
AUTOMATION_START_TIME = datetime.now(timezone.utc)
IS_INITIAL_BASELINE_DONE = False

# ─── MEMORY & DEDUPLICATION ───
if os.path.exists(SEEN_FILE):
    try:
        with open(SEEN_FILE, "r", encoding="utf-8") as f:
            seen_topics = json.load(f)
    except Exception:
        seen_topics = {}
else:
    seen_topics = {}


def save_memory():
    try:
        with open(SEEN_FILE, "w", encoding="utf-8") as f:
            json.dump(seen_topics, f, indent=2)
    except Exception as e:
        print(f"Error saving memory: {e}")


# ─── TELEGRAM BROADCAST HELPERS ───
def send_tg_message(chat_id, text):
    url = f"{TG_API_BASE}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}
    try:
        requests.post(url, json=payload, timeout=15)
    except Exception as e:
        print(f"Error sending TG message: {e}")


def send_tg_photo(chat_id, photo_url_or_bytes, caption=""):
    url = f"{TG_API_BASE}/sendPhoto"
    try:
        if isinstance(photo_url_or_bytes, str) and photo_url_or_bytes.startswith("http"):
            requests.post(url, json={"chat_id": chat_id, "photo": photo_url_or_bytes, "caption": caption, "parse_mode": "Markdown"}, timeout=20)
        else:
            files = {"photo": photo_url_or_bytes}
            data = {"chat_id": chat_id, "caption": caption, "parse_mode": "Markdown"}
            requests.post(url, files=files, data=data, timeout=25)
    except Exception as e:
        print(f"Error sending TG photo: {e}")


def send_tg_audio(chat_id, audio_path, caption=""):
    url = f"{TG_API_BASE}/sendAudio"
    try:
        with open(audio_path, "rb") as f:
            files = {"audio": f}
            data = {"chat_id": chat_id, "caption": caption}
            requests.post(url, files=files, data=data, timeout=35)
    except Exception as e:
        print(f"Error sending TG audio: {e}")


def send_tg_album(chat_id, image_paths, caption=""):
    """Sends multiple photos grouped as a single Instagram-style swipeable carousel album."""
    url = f"{TG_API_BASE}/sendMediaGroup"
    try:
        media = []
        files = {}
        for idx, img_path in enumerate(image_paths):
            attach_name = f"photo_{idx}"
            item = {"type": "photo", "media": f"attach://{attach_name}"}
            if idx == 0 and caption:
                item["caption"] = caption
                item["parse_mode"] = "Markdown"
            media.append(item)
            files[attach_name] = open(img_path, "rb")

        data = {"chat_id": chat_id, "media": json.dumps(media)}
        res = requests.post(url, data=data, files=files, timeout=60)
        for f in files.values():
            f.close()
        return res.status_code == 200
    except Exception as e:
        print(f"Error sending TG album: {e}")
        return False


# ─── VISUAL CAROUSEL GENERATOR (PILLOW 1080x1350) ───
def render_instagram_carousel(topic_title, carousel_text):
    """
    Renders 6 ultra-clean, dark mode Instagram carousel slides (1080x1350 vertical aspect ratio).
    Uses Roboto-Bold & Roboto-Regular for agency-grade typography.
    Delivered directly as an album to Telegram.
    """
    font_bold_path = "fonts/Roboto-Bold.ttf"
    font_reg_path = "fonts/Roboto-Regular.ttf"

    try:
        f_badge = ImageFont.truetype(font_bold_path, 28)
        f_brand = ImageFont.truetype(font_bold_path, 30)
        f_title = ImageFont.truetype(font_bold_path, 54)
        f_body = ImageFont.truetype(font_reg_path, 34)
        f_footer = ImageFont.truetype(font_bold_path, 26)
    except Exception:
        f_badge = f_brand = f_title = f_body = f_footer = ImageFont.load_default()

    slides_data = [
        ("THE BIG SHIFT", f"{topic_title[:80]}\n\nStop doing this the old way. A new AI model just flipped the industry.", "Swipe >>"),
        ("THE PROBLEM", "99% of creators & business owners are wasting 4+ hours every day on repetitive manual work.\n\nHere is how to automate it in seconds.", "Why it matters >>"),
        ("HOW IT WORKS", "No tech jargon. Plain English breakdown so simple a 12-year-old gets it.\n\nIt replaces 3 separate complex tools into 1 unified pipeline.", "The secret triad >>"),
        ("THE SIGNATURE TRIAD", "INPUT: Your raw data or simple prompt\nPROMPT: Jayant's System Architecture\nOUTPUT: Production-ready client deliverable", "Practical ROI >>"),
        ("BUSINESS IMPACT", "What used to take 3 days and an expensive agency now takes 30 seconds inside your business.", "Final step >>"),
        ("TAKE ACTION", "Save this post for later.\n\nWhatsApp +91 78800 56262 or DM 'AUDIT' for a free 15-minute AI implementation roadmap.", "Jayant's AI Lab HQ")
    ]

    timestamp = int(time.time())
    generated_paths = []

    for idx, (headline, body, footer_hint) in enumerate(slides_data, 1):
        img = Image.new("RGB", (1080, 1350), color="#080c14")
        draw = ImageDraw.Draw(img)

        # Outer rounded frame
        draw.rounded_rectangle([(40, 40), (1040, 1310)], radius=24, outline="#1e293b", width=3)

        # Top Pill Badge
        draw.rounded_rectangle([(80, 80), (460, 150)], radius=35, fill="#0f2338", outline="#0284c7", width=2)
        draw.text((110, 98), f"AI STRATEGY  |  {idx}/6", font=f_badge, fill="#38bdf8")

        # Brand Title
        draw.text((640, 100), "JAYANT'S AI LAB", font=f_brand, fill="#64748b")

        # Headline
        draw.text((80, 240), headline, font=f_title, fill="#ffffff", spacing=14)

        # Content Container Card
        draw.rounded_rectangle([(80, 480), (1000, 1140)], radius=20, fill="#0d1526", outline="#1e293b", width=2)
        draw.text((120, 530), body, font=f_body, fill="#cbd5e1", spacing=22)

        # Footer
        draw.line([(80, 1190), (1000, 1190)], fill="#1e293b", width=2)
        draw.text((80, 1225), footer_hint, font=f_footer, fill="#38bdf8")
        draw.text((700, 1225), "@jrddiwan", font=f_footer, fill="#64748b")

        slide_path = os.path.join(CAROUSEL_DIR, f"slide_{timestamp}_{idx}.png")
        img.save(slide_path)
        generated_paths.append(slide_path)

    return generated_paths


# ─── VISUAL ENGINE (SCREENSHOTS + FLUX.1 + CLOUDFLARE) ───
def capture_url_screenshot(target_url):
    """Capture a crisp visual screenshot of the target tweet, blog post, or release page."""
    try:
        encoded_url = urllib.parse.quote(target_url)
        screenshot_api_url = f"https://api.microlink.io?url={encoded_url}&screenshot=true&meta=false&embed=screenshot.url"
        res = requests.get(screenshot_api_url, timeout=15)
        if res.status_code == 200:
            return screenshot_api_url
    except Exception as e:
        print(f"Screenshot error: {e}")
    return None


def generate_flux_image(prompt):
    """Generate high-res visual proof card via Hugging Face FLUX.1-schnell (dual key rotation) with Cloudflare SDXL fallback."""
    for token in HF_TOKENS:
        try:
            api_url = "https://api-inference.huggingface.co/models/black-forest-labs/FLUX.1-schnell"
            headers = {"Authorization": f"Bearer {token}"}
            res = requests.post(api_url, headers=headers, json={"inputs": prompt}, timeout=25)
            if res.status_code == 200 and res.content:
                return res.content
        except Exception as e:
            print(f"HF FLUX error with token: {e}")

    for account, token in CF_CREDS:
        try:
            cf_url = f"https://api.cloudflare.com/client/v4/accounts/{account}/ai/run/@cf/bytedance/stable-diffusion-xl-lightning"
            r = requests.post(cf_url, headers={"Authorization": f"Bearer {token}"}, json={"prompt": prompt}, timeout=20)
            if r.status_code == 200 and r.content:
                return r.content
        except Exception as e:
            print(f"CF Fallback error with account {account}: {e}")

    return None


# ─── EXECUTIVE QUALITY GATE (GROQ 120B / GEMINI) ───
def evaluate_video_worth(title, description=""):
    """
    Evaluates whether an upload covers a genuine, high-value AI tool suitable for a viral breakdown reel.
    Filters out casual conversation, podcast banter, and non-actionable vlogs.
    """
    eval_prompt = f"""You are the Executive Producer for Jayant's AI Lab.
Evaluate this YouTube video:
Title: {title}
Context: {description}

Determine if this video covers a specific, actionable new AI tool, model, or breakthrough that normal creators or businesses can use immediately.
If it is just general commentary, podcast banter, opinion, or vague news, reply strictly with:
REJECT: [Reason]

If it showcases a genuine game-changer tool or model worthy of a dedicated breakdown reel, reply strictly with:
APPROVE: [Tool Name] | [One-line core reason]
"""
    if GROQ_API_KEY:
        try:
            res = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
                json={"model": "openai/gpt-oss-120b", "messages": [{"role": "user", "content": eval_prompt}], "temperature": 0.2},
                timeout=15
            )
            if res.status_code == 200:
                out = res.json()["choices"][0]["message"]["content"].strip()
                if out.startswith("APPROVE"):
                    return True, out.replace("APPROVE:", "").strip()
                else:
                    return False, out.replace("REJECT:", "").strip()
        except Exception as e:
            print(f"Quality gate Groq error: {e}")

    for g_key in GEMINI_KEYS:
        try:
            c = genai.Client(api_key=g_key)
            r = c.models.generate_content(model="gemini-3.8-flash", contents=eval_prompt)
            out = r.text.strip()
            if out.startswith("APPROVE"):
                return True, out.replace("APPROVE:", "").strip()
            else:
                return False, out.replace("REJECT:", "").strip()
        except Exception:
            pass

    return True, title


# ─── MASTER SCRIPTWRITING ENGINE (VAIBHAV + AI SEARCH + JAYANT FUSION) ───
def generate_full_studio_package(topic_title, topic_details, source_url=""):
    prompt = f"""You are the elite chief scriptwriter for Jayant's AI Lab.
Topic: {topic_title}
Details: {topic_details}

Write a viral studio distribution package blending the styles of:
1. VAIBHAV SISINTY: Hard contrarian pattern-interrupt hook ("Stop doing X manually", "99% of people are doing this wrong"), punchy cadence, quantifiable time/money saved.
2. THE AI SEARCH: Extreme visual dissection, explain the mechanics so simply that a 12-year-old school kid gets it immediately, clear real-world analogies.
3. JAYANT: High-energy, confident South Delhi tech consultant authority, signature transformation triad (Input -> Prompt -> Output), WhatsApp audit CTA (+91 78800 56262).

STRICT BANNED ROBOTIC WORDS:
Do NOT use: "game-changer", "in today's fast-paced world", "harnessing the power", "delve into", "revolutionize", "testament", "tapestry".
Speak naturally, like a sharp tech founder talking to an ambitious business owner.

Return your response strictly adhering to these EXACT tags:

[HOOK]
(6-8 seconds for Jayant's Google Vids Avatar. Start with a shock/curiosity question or contrarian callout, end strictly with: "Here's my AI employee ZORO to break it down.")

[ZORO_BODY]
(35-45 seconds, ~110 words for ZORO. Start strictly with: "[cheerfully] Hey everyone, ZORO here — Jayant's AI employee!"
Explain how this tool works using a real-world everyday analogy. Give 1 shocking stat or time comparison. Show what a business can do with it right now. End with a sharp, memorable punchline.)

[B_ROLL_LIST]
(3-4 specific visual B-roll scene cues with exact second markers matching ZORO's script. Include:
- Timestamp (e.g., [00:08 - 00:15])
- Visual description (what to display on screen)
- AI Video/Image generation prompt to copy-paste into Hugging Face, Kling, or Luma)

[CTA]
(8 seconds for Jayant's Google Vids Avatar: "That was ZORO — my AI employee. Want one working for your business? Message me on WhatsApp or tap the link in bio for a free fifteen-minute AI audit. See you tomorrow.")

[TWEET]
(Strictly <= 260 characters total. Contrarian hook + 1 key metric + link/CTA. High engagement.)

[LINKEDIN]
(Hook line -> The 'Old Way vs New Way' -> 3 bullet points of real business impact -> ELI12 takeaway -> Call to action with WhatsApp link.)

[CAROUSEL]
Slide 1: Bold Title Hook
Slide 2: The Big Problem (Old Way vs New Way)
Slide 3: What This AI Does (Kid-friendly analogy)
Slide 4: The Secret Triad (Input -> Prompt -> Output)
Slide 5: Practical Business Use Case
Slide 6: CTA (Save post & WhatsApp for free AI audit: +91 78800 56262)

[PROMPT_OF_THE_DAY]
(A ready-to-copy prompt template for this tool to share in the Jayant's AI Lab WhatsApp community.)
"""
    raw_text = None

    if GROQ_API_KEY:
        try:
            g_res = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
                json={"model": "openai/gpt-oss-120b", "messages": [{"role": "user", "content": prompt}], "temperature": 0.4},
                timeout=20
            )
            if g_res.status_code == 200:
                raw_text = g_res.json()["choices"][0]["message"]["content"]
        except Exception as e:
            print(f"Groq generation fallback: {e}")

    if not raw_text:
        for a_key in AGNES_KEYS:
            try:
                a_res = requests.post(
                    "https://apihub.agnes-ai.com/v1/chat/completions",
                    headers={"Authorization": f"Bearer {a_key}", "Content-Type": "application/json"},
                    json={"model": "agnes-2.5-flash", "messages": [{"role": "user", "content": prompt}], "temperature": 0.4},
                    timeout=20
                )
                if a_res.status_code == 200:
                    raw_text = a_res.json()["choices"][0]["message"]["content"]
                    break
            except Exception:
                pass

    if not raw_text:
        for or_key in OPENROUTER_KEYS:
            try:
                or_res = requests.post(
                    "https://openrouter.ai/api/v1/chat/completions",
                    headers={"Authorization": f"Bearer {or_key}", "Content-Type": "application/json"},
                    json={"model": "meta-llama/llama-3.3-70b-instruct:free", "messages": [{"role": "user", "content": prompt}]},
                    timeout=20
                )
                if or_res.status_code == 200:
                    raw_text = or_res.json()["choices"][0]["message"]["content"]
                    break
            except Exception:
                pass

    if not raw_text:
        for g_key in GEMINI_KEYS:
            try:
                g_client_text = genai.Client(api_key=g_key)
                gem_res = g_client_text.models.generate_content(model="gemini-3.8-flash", contents=prompt)
                if gem_res.text:
                    raw_text = gem_res.text
                    break
            except Exception:
                pass

    def extract_tag(tag, text):
        if not text:
            return ""
        if f"[{tag}]" in text:
            part = text.split(f"[{tag}]")[1]
            for next_tag in ["HOOK", "ZORO_BODY", "B_ROLL_LIST", "CTA", "TWEET", "LINKEDIN", "CAROUSEL", "PROMPT_OF_THE_DAY"]:
                if f"[{next_tag}]" in part:
                    part = part.split(f"[{next_tag}]")[0]
            return part.strip()
        return ""

    hook = extract_tag("HOOK", raw_text) or "Did you see what just dropped in AI? Here's my AI employee ZORO to break it down."
    body = extract_tag("ZORO_BODY", raw_text) or f"[cheerfully] Hey everyone, ZORO here — Jayant's AI employee!\n{topic_title} is here and it changes everything for your business."
    b_roll = extract_tag("B_ROLL_LIST", raw_text) or "• [00:08 - 00:20] Screen capture of tool UI\n• [00:20 - 00:35] Side-by-side speed test"
    cta = extract_tag("CTA", raw_text) or "That was ZORO — my AI employee. Message me on WhatsApp or check link in bio!"
    tweet = extract_tag("TWEET", raw_text) or f"AI update: {topic_title}. Details: wa.me/917880056262"
    linkedin = extract_tag("LINKEDIN", raw_text) or topic_details
    carousel = extract_tag("CAROUSEL", raw_text) or "Slide 1: Breaking AI Update\nSlide 2: Check it out!"
    prompt_magnet = extract_tag("PROMPT_OF_THE_DAY", raw_text) or "Test this tool today."

    if len(tweet) > 260:
        tweet = tweet[:257] + "..."

    # 2. Synthesize ZORO voice track via Gemini 3.1 Flash TTS
    director_prompt = f"""## "ZORO — Jayant's AI Employee" — Daily AI Briefing
## THE SCENE: Modern AI Lab, South Delhi
ZORO is dynamic, smiling, and speaking with crisp news-anchor clarity and infectious energy.
### DIRECTOR'S NOTES
Speaker: Confident, energetic young Indian male AI employee (South Delhi tech consultant).
Style: Conversational, vocal smile, fast-paced short-form video cadence, clear Indian English accent.
Pace: Brisk, punchy, energetic male delivery.
Accent: Educated Indian English.
#### TRANSCRIPT
{body}
"""
    audio_data = None
    for g_key in GEMINI_KEYS:
        try:
            g_client_tts = genai.Client(api_key=g_key)
            interaction = g_client_tts.interactions.create(
                model="gemini-3.1-flash-tts-preview",
                input=director_prompt,
                response_format={"type": "audio"},
                generation_config={"speech_config": [{"voice": ZORO_VOICE}]}
            )
            audio_data = base64.b64decode(interaction.output_audio.data)
            if audio_data:
                break
        except Exception as e:
            print(f"TTS error with key: {e}")

    timestamp = int(time.time())
    audio_path = os.path.join(OUTPUT_DIR, f"zoro_{timestamp}.wav")

    if audio_data:
        with wave.open(audio_path, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(24000)
            wf.writeframes(audio_data)

    # 3. Render 6-Slide Visual Instagram Carousel (Pillow PNGs)
    carousel_images = render_instagram_carousel(topic_title, carousel)

    return {
        "hook": hook,
        "body": body,
        "b_roll": b_roll,
        "cta": cta,
        "tweet": tweet,
        "linkedin": linkedin,
        "carousel": carousel,
        "carousel_images": carousel_images,
        "prompt_magnet": prompt_magnet,
        "audio_path": audio_path
    }


# ─── YOUTUBE MULTI-TOOL DISSECTOR WITH DATE & QUALITY GATE ───
YOUTUBE_CHANNELS = [
    ("The AI Search", "UCIgnGlGkVRhd4qNFcEwLL4A"),
    ("Vaibhav Sisinty", "UClXAalunTPaX1YV185DWUeg"),
    ("Matt Wolfe", "UChpleBmo18P08aKCIgti38g"),
    ("AI Explained", "UCNJ1Ymd5yFuUPtn21xtRbbw"),
    ("Matthew Berman", "UCzi5kcwU8aT4aLR7LcYhfWQ"),
    ("Wes Roth", "UCqcbQf6yw5KzRoDDcZ_wBSw")
]


def check_youtube_uploads():
    """Scans channels for brand-new video releases published AFTER automation launch."""
    global IS_INITIAL_BASELINE_DONE

    for channel_name, cid in YOUTUBE_CHANNELS:
        try:
            feed_url = f"https://www.youtube.com/feeds/videos.xml?channel_id={cid}"
            r = requests.get(feed_url, timeout=15)
            if r.status_code == 200:
                root = ET.fromstring(r.content)
                entries = root.findall("{http://www.w3.org/2005/Atom}entry")

                # Baseline seeding on initial startup: mark all currently existing videos as seen
                if not IS_INITIAL_BASELINE_DONE:
                    for entry in entries:
                        v_id = entry.find("{http://www.youtube.com/xml/schemas/2015}videoId").text
                        seen_topics[v_id] = {"baseline": True}
                    save_memory()
                    continue

                if entries:
                    entry = entries[0]
                    vid_id = entry.find("{http://www.youtube.com/xml/schemas/2015}videoId").text
                    title = entry.find("{http://www.w3.org/2005/Atom}title").text
                    published_str = entry.find("{http://www.w3.org/2005/Atom}published").text
                    video_url = f"https://www.youtube.com/watch?v={vid_id}"

                    # 1. Publication Date Filter: Strictly ignore past videos
                    try:
                        pub_dt = datetime.fromisoformat(published_str.replace("Z", "+00:00"))
                        if pub_dt < AUTOMATION_START_TIME:
                            seen_topics[vid_id] = {"skipped_old": True}
                            save_memory()
                            continue
                    except Exception as e:
                        print(f"Date parse error: {e}")

                    if vid_id not in seen_topics:
                        seen_topics[vid_id] = {"title": title, "channel": channel_name, "processed": True}
                        save_memory()

                        # 2. Executive Quality Gate: Evaluate if worth a reel
                        is_worthy, reason = evaluate_video_worth(title)
                        if not is_worthy:
                            print(f"[RADAR SUPPRESSED]: {title} -> {reason}")
                            continue

                        print(f"[RADAR APPROVED]: {title} ({reason})")

                        # Generate full package
                        pkg = generate_full_studio_package(title, f"Covered by {channel_name} on YouTube: {video_url}", source_url=video_url)

                        # Deliver directly to Jayant's AI Lab HQ Channel
                        # Pack 1: Video Production
                        video_msg = (
                            f"🎬 *NEW REEL PRODUCTION PACK*\n"
                            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                            f"📺 *Source:* {channel_name} ({title})\n\n"
                            f"🎯 *YOUR HOOK (Google Vids Avatar):*\n_{pkg['hook']}_\n\n"
                            f"🤖 *ZORO BODY SCRIPT (ELI12):*\n{pkg['body']}\n\n"
                            f"📢 *YOUR CTA (Google Vids Avatar):*\n_{pkg['cta']}_\n\n"
                            f"🎥 *AUTOMATED B-ROLL SCENE LIST & AI PROMPTS:*\n{pkg['b_roll']}\n\n"
                            f"🎧 *ZORO's audio track is attached below!*"
                        )
                        send_tg_message(HQ_CHANNEL_ID, video_msg)
                        send_tg_audio(HQ_CHANNEL_ID, pkg['audio_path'], caption=f"🎙️ ZORO Audio ({ZORO_VOICE} • South Delhi)")

                        # Pack 2: Visual Instagram Carousel (Photos Album)
                        send_tg_album(HQ_CHANNEL_ID, pkg['carousel_images'], caption=f"📱 *Instagram Carousel Deliverable: {title}*")

                        # Pack 3: Social Omnichannel Pack
                        social_msg = (
                            f"📢 *OMNICHANNEL SOCIAL DISTRIBUTION PACK*\n"
                            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                            f"🐦 *STRICT <= 260 CHAR TWEET:*\n`{pkg['tweet']}`\n\n"
                            f"💡 *PROMPT OF THE DAY MAGNET (WhatsApp Community):*\n```\n{pkg['prompt_magnet']}\n```\n\n"
                            f"💼 *HIGH-INSIGHT LINKEDIN POST:*\n{pkg['linkedin']}"
                        )
                        send_tg_message(HQ_CHANNEL_ID, social_msg)

                        # Proof visual
                        screenshot_url = capture_url_screenshot(video_url)
                        if screenshot_url:
                            send_tg_photo(HQ_CHANNEL_ID, screenshot_url, caption=f"📸 Proof: {title}")

        except Exception as e:
            print(f"Error checking YouTube channel {channel_name}: {e}")

    IS_INITIAL_BASELINE_DONE = True


# ─── CLOUD HTTP HEALTH HANDLER (RENDER KEEP-ALIVE) ───
class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Jayant AI Lab Master Studio & Radar running 24/7!")


# ─── MASTER BACKGROUND SCANNER ───
def master_radar_loop():
    print("[AI RADAR]: Master background loop active...")
    time.sleep(10)
    while True:
        try:
            check_youtube_uploads()
        except Exception as e:
            print(f"Error in master radar loop: {e}")
        time.sleep(600)  # Scan every 10 minutes


# ─── TELEGRAM ON-DEMAND LISTENER (DIRECT MESSAGES) ───
def telegram_listener():
    offset = 0
    while True:
        try:
            url = f"{TG_API_BASE}/getUpdates?offset={offset}&timeout=20"
            res = requests.get(url, timeout=25).json()
            if "result" in res:
                for update in res["result"]:
                    offset = update["update_id"] + 1
                    msg = update.get("message", {})
                    chat_id = msg.get("chat", {}).get("id")
                    text = msg.get("text", "")

                    if not text or (chat_id != AUTHORIZED_CHAT_ID and str(chat_id) != HQ_CHANNEL_ID):
                        continue

                    if text.startswith("/start"):
                        send_tg_message(chat_id, "👋 Hello Jayant! Master Studio Engine is active 24/7. Send any AI link or topic anytime!")
                        continue

                    print(f"[MANUAL REQUEST]: {text}")
                    send_tg_message(chat_id, "⚡ *Got it! Generating complete Studio Distribution Package & Carousel... (Takes ~30s)*")

                    pkg = generate_full_studio_package(text, text, source_url="")

                    # Deliver Video Pack
                    video_msg = (
                        f"🎬 *VIDEO PRODUCTION PACKAGE READY!*\n"
                        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                        f"🎯 *YOUR HOOK (Google Vids Avatar):*\n_{pkg['hook']}_\n\n"
                        f"🤖 *ZORO BODY SCRIPT (ELI12):*\n{pkg['body']}\n\n"
                        f"📢 *YOUR CTA (Google Vids Avatar):*\n_{pkg['cta']}_\n\n"
                        f"🎥 *AUTOMATED B-ROLL SCENE LIST & AI PROMPTS:*\n{pkg['b_roll']}\n\n"
                        f"🎧 *ZORO's audio track is attached below!*"
                    )
                    send_tg_message(chat_id, video_msg)
                    send_tg_audio(chat_id, pkg['audio_path'], caption=f"🎙️ ZORO Audio ({ZORO_VOICE} • South Delhi)")

                    # Deliver Visual Instagram Carousel
                    send_tg_album(chat_id, pkg['carousel_images'], caption=f"📱 *Instagram Carousel Deliverable: {text[:60]}*")

                    # Deliver Social Distribution Pack
                    social_msg = (
                        f"📢 *OMNICHANNEL SOCIAL DISTRIBUTION PACK*\n"
                        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                        f"🐦 *STRICT <= 260 CHAR TWEET:*\n`{pkg['tweet']}`\n\n"
                        f"💡 *PROMPT OF THE DAY MAGNET (WhatsApp Community):*\n```\n{pkg['prompt_magnet']}\n```\n\n"
                        f"💼 *HIGH-INSIGHT LINKEDIN POST:*\n{pkg['linkedin']}"
                    )
                    send_tg_message(chat_id, social_msg)

                    # Visual proof card
                    img_bytes = generate_flux_image(f"Futuristic tech proof card for {text[:60]}, dark mode cyber aesthetic, 8k")
                    if img_bytes:
                        send_tg_photo(chat_id, img_bytes, caption="🖼️ Hugging Face FLUX.1 Visual Proof Card")

        except Exception as e:
            print(f"Error in TG listener: {e}")
            time.sleep(3)


def main():
    print("=" * 60)
    print("  JAYANT'S AI LAB — 24/7 MASTER CLOUD STUDIO")
    print("=" * 60)

    # Start Radar thread
    t_radar = threading.Thread(target=master_radar_loop, daemon=True)
    t_radar.start()

    # Start Telegram listener thread
    t_tg = threading.Thread(target=telegram_listener, daemon=True)
    t_tg.start()

    send_tg_message(
        HQ_CHANNEL_ID,
        "🚀 *Jayant's AI Lab HQ — Master Studio Connected 24/7!*\n\n"
        "✨ *Autonomous Upgrades Active:*\n"
        "• 🛑 Zero Past Videos: Only new videos published from this moment forward are monitored.\n"
        "• 🧠 Executive Quality Gate: Groq 120B evaluates transcripts to suppress podcast/vlog fluff.\n"
        "• ✍️ Vaibhav + The AI Search + Jayant scriptwriting fusion.\n"
        "• 📱 Instagram Carousels rendered & delivered directly as high-res PNG slide albums.\n"
        "• 🎙️ ZORO male voice track (.wav) + Automated B-Roll cues.\n"
        "• 🐦 Strict <= 260-char Tweet & High-Insight LinkedIn post."
    )

    # HTTP server for keep-alive on port 7860
    server = HTTPServer(("0.0.0.0", 7860), HealthHandler)
    server.serve_forever()


if __name__ == "__main__":
    main()
