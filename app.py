# Jayant's AI Lab — Telegram Bot Controller with AI Radar Scanner (Hugging Face Spaces Ready)
# Runs 24/7 in the cloud on Hugging Face Spaces (Docker / Python)

import os
import time
import json
import wave
import base64
import threading
import requests
import xml.etree.ElementTree as ET
from http.server import HTTPServer, BaseHTTPRequestHandler
from google import genai

# Credentials — injected via Render Environment Variables
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
AUTHORIZED_CHAT_ID = int(os.getenv("AUTHORIZED_CHAT_ID", "7007116692"))
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

OUTPUT_DIR = "telegram_outputs"
SEEN_FILE = "seen_topics.json"
os.makedirs(OUTPUT_DIR, exist_ok=True)

TG_API_BASE = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"
client = genai.Client(api_key=GEMINI_API_KEY)

if os.path.exists(SEEN_FILE):
    try:
        with open(SEEN_FILE, "r", encoding="utf-8") as f:
            seen_ids = set(json.load(f))
    except Exception:
        seen_ids = set()
else:
    seen_ids = set()


def save_seen_ids():
    try:
        with open(SEEN_FILE, "w", encoding="utf-8") as f:
            json.dump(list(seen_ids)[-300:], f)
    except Exception as e:
        print(f"Error saving seen ids: {e}")


def send_tg_message(chat_id, text, reply_markup=None):
    url = f"{TG_API_BASE}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}
    if reply_markup:
        payload["reply_markup"] = reply_markup
    try:
        requests.post(url, json=payload, timeout=15)
    except Exception as e:
        print(f"Error sending message: {e}")


def send_tg_audio(chat_id, audio_path, caption=""):
    url = f"{TG_API_BASE}/sendAudio"
    try:
        with open(audio_path, "rb") as f:
            files = {"audio": f}
            data = {"chat_id": chat_id, "caption": caption}
            requests.post(url, files=files, data=data, timeout=30)
    except Exception as e:
        print(f"Error sending audio: {e}")


def generate_scripts_and_audio(topic_text):
    prompt = f"""You are the lead viral content strategist for Jayant's AI Lab.
The user provided this breaking AI topic:
"{topic_text}"

Create a viral short-form video script with 3 parts:
1. HOOK (for Jayant's Google Vids avatar, 6-8s): Start with curiosity/shock or a question, end with: "Here's my AI employee ZORO to break it down."
2. ZORO_BODY (for AI employee ZORO, 35-45s, ~100-120 words):
   - Start with: "[cheerfully] Hey everyone, ZORO here — Jayant's AI employee!"
   - Explain what dropped in plain English (no technical jargon).
   - Give 1-2 shocking numbers, speed/cost comparisons, or benchmark wins.
   - Give a practical business or real-world use case.
   - End with a punchy conclusion line (e.g. "This is AI as a reflex. Not a conversation!").
3. CTA (for Jayant's avatar, 8s): "That was ZORO — my AI employee. Want one working for your business? Message me on WhatsApp or tap the link in bio for a free fifteen-minute AI audit. See you tomorrow."

Format your output strictly as:
[HOOK]
<hook text>

[ZORO_BODY]
<body text>

[CTA]
<cta text>
"""
    models_to_try = ["gemini-2.5-pro", "gemini-3.8-flash", "gemini-2.5-flash-preview-tts"]
    raw_text = None
    for m in models_to_try:
        try:
            res = client.models.generate_content(model=m, contents=prompt)
            raw_text = res.text
            break
        except Exception:
            time.sleep(1)

    if not raw_text:
        raw_text = f"[HOOK]\nDid you see what just happened in AI? Here's my AI employee ZORO to break it down.\n\n[ZORO_BODY]\n[cheerfully] Hey everyone, ZORO here — Jayant's AI employee!\n{topic_text}\nThis is a huge game changer for businesses.\n\n[CTA]\nThat was ZORO — my AI employee. Want one working for your business? Message me on WhatsApp!"

    hook = "Check this out! Here's my AI employee ZORO to break it down."
    body = "Hey everyone, ZORO here — Jayant's AI employee! Big update today."
    cta = "That was ZORO — my AI employee. Message me on WhatsApp or check link in bio!"

    if "[HOOK]" in raw_text and "[ZORO_BODY]" in raw_text:
        parts = raw_text.split("[ZORO_BODY]")
        hook = parts[0].replace("[HOOK]", "").strip()
        subparts = parts[1].split("[CTA]")
        body = subparts[0].strip()
        if len(subparts) > 1:
            cta = subparts[1].strip()

    director_prompt = f"""## "ZORO — Jayant's AI Employee" — Daily AI Briefing
## THE SCENE: Modern AI Lab, South Delhi
ZORO is dynamic, smiling, and speaking with crisp news-anchor clarity and infectious energy.
### DIRECTOR'S NOTES
Style: Conversational, vocal smile, fast-paced (short-form video cadence), clear Indian English accent (South Delhi).
Pace: Brisk, punchy, energetic.
Accent: Educated Indian English.
#### TRANSCRIPT
{body}
"""
    interaction = client.interactions.create(
        model="gemini-3.1-flash-tts-preview",
        input=director_prompt,
        response_format={"type": "audio"},
        generation_config={
            "speech_config": [
                {"voice": "Rasalgethi"}
            ]
        }
    )
    audio_data = base64.b64decode(interaction.output_audio.data)
    timestamp = int(time.time())
    audio_path = os.path.join(OUTPUT_DIR, f"zoro_{timestamp}.wav")

    with wave.open(audio_path, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(24000)
        wf.writeframes(audio_data)

    return hook, body, cta, audio_path


def fetch_huggingface_new():
    items = []
    try:
        url = "https://huggingface.co/api/models?sort=createdAt&direction=-1&limit=25"
        res = requests.get(url, timeout=10).json()
        for m in res:
            mid = m.get("id", "")
            if any(org in mid.lower() for org in ["qwen", "deepseek", "meta", "mistral", "google", "flash", "vision", "omni", "reason"]):
                items.append({
                    "id": f"hf_{mid}",
                    "title": f"HuggingFace Model Drop: {mid}",
                    "desc": f"New model uploaded to HF Hub. Downloads: {m.get('downloads', 0)}, Likes: {m.get('likes', 0)}"
                })
    except Exception as e:
        print(f"HF Scanner error: {e}")
    return items


def fetch_reddit_ai():
    items = []
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
    subreddits = ["LocalLLaMA", "artificial"]
    for sub in subreddits:
        try:
            url = f"https://www.reddit.com/r/{sub}/hot.json?limit=15"
            res = requests.get(url, headers=headers, timeout=10)
            if res.status_code == 200:
                posts = res.json().get("data", {}).get("children", [])
                for p in posts:
                    data = p.get("data", {})
                    pid = data.get("id", "")
                    title = data.get("title", "")
                    score = data.get("score", 0)
                    if score > 50 and any(k in title.lower() for k in ["released", "benchmark", "beats", "dropped", "v3", "new model", "faster", "flash", "out"]):
                        items.append({
                            "id": f"reddit_{pid}",
                            "title": title,
                            "desc": f"r/{sub} post with {score} upvotes. {data.get('selftext', '')[:200]}"
                        })
        except Exception as e:
            print(f"Reddit scanner error ({sub}): {e}")
    return items


def fetch_rss_feeds():
    items = []
    feeds = [
        ("HN AI", "https://hnrss.org/newest?q=AI+OR+LLM+OR+model&points=50"),
        ("OpenAI News", "https://openai.com/news/rss.xml"),
    ]
    for source_name, url in feeds:
        try:
            res = requests.get(url, timeout=10)
            if res.status_code == 200:
                root = ET.fromstring(res.content)
                for item in root.findall(".//item")[:5]:
                    title = item.find("title").text if item.find("title") is not None else ""
                    link = item.find("link").text if item.find("link") is not None else ""
                    if title:
                        items.append({
                            "id": f"rss_{hash(title)}",
                            "title": f"[{source_name}] {title}",
                            "desc": f"Link: {link}"
                        })
        except Exception as e:
            print(f"RSS error ({source_name}): {e}")
    return items


def scan_and_alert():
    print("[AI RADAR] Background scanner started...")
    time.sleep(10)

    while True:
        try:
            all_items = []
            all_items.extend(fetch_huggingface_new())
            all_items.extend(fetch_reddit_ai())
            all_items.extend(fetch_rss_feeds())

            fresh_items = [it for it in all_items if it["id"] not in seen_ids]

            if fresh_items:
                print(f"[RADAR]: Found {len(fresh_items)} fresh AI signals. Evaluating via Gemini...")

                candidates_text = "\n".join([f"- ID: {it['id']} | Title: {it['title']} | Info: {it['desc']}" for it in fresh_items[:12]])
                eval_prompt = f"""You are the chief AI scout for Jayant's AI Lab.
Review these fresh AI signals detected across HuggingFace, Reddit, and News:
{candidates_text}

Pick the single most shocking, viral, or groundbreaking AI release (if any meet this standard).
Look for: benchmark wins (beats GPT, beats Claude), massive new model drops (Qwen, DeepSeek, Llama), or new paradigms (like Jev).

If none are truly viral or groundbreaking, reply with: NONE

If you find a winning story, reply in this EXACT format:
WINNER_ID: <the ID>
HEADLINE: <crisp viral headline>
WHY_IT_MATTERS: <2 sentences on why everyday businesses or tech enthusiasts should care>
KEY_STATS: <benchmark or stat>
"""
                eval_output = None
                for emodel in ["gemini-2.5-pro", "gemini-3.8-flash", "gemini-2.5-flash-preview-tts"]:
                    try:
                        res = client.models.generate_content(model=emodel, contents=eval_prompt)
                        eval_output = res.text.strip()
                        break
                    except Exception:
                        time.sleep(1)

                if eval_output and "WINNER_ID:" in eval_output:
                    lines = eval_output.split("\n")
                    winner_id = ""
                    headline = ""
                    why = ""
                    stats = ""
                    for line in lines:
                        if line.startswith("WINNER_ID:"):
                            winner_id = line.replace("WINNER_ID:", "").strip()
                        elif line.startswith("HEADLINE:"):
                            headline = line.replace("HEADLINE:", "").strip()
                        elif line.startswith("WHY_IT_MATTERS:"):
                            why = line.replace("WHY_IT_MATTERS:", "").strip()
                        elif line.startswith("KEY_STATS:"):
                            stats = line.replace("KEY_STATS:", "").strip()

                    for it in fresh_items:
                        seen_ids.add(it["id"])
                    save_seen_ids()

                    alert_text = (
                        f"🚨 *AI RADAR ALERT — BREAKING DROP DETECTED!*\n"
                        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                        f"🔥 *{headline}*\n\n"
                        f"📊 *Key Highlights:* {stats}\n\n"
                        f"💡 *Why It Matters:* {why}\n\n"
                        f"👉 _Reply with *'MAKE'* to immediately generate the Hook, ZORO Script & Voice Audio!_"
                    )
                    send_tg_message(AUTHORIZED_CHAT_ID, alert_text)
                    print(f"[ALERT SENT]: {headline}")

                else:
                    for it in fresh_items:
                        seen_ids.add(it["id"])
                    save_seen_ids()

        except Exception as e:
            print(f"Error in Radar loop: {e}")

        time.sleep(480)


def bot_polling():
    offset = 0
    last_topic = "Latest viral AI release"
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

                    if chat_id != AUTHORIZED_CHAT_ID or not text:
                        continue

                    if text.startswith("/start"):
                        send_tg_message(
                            chat_id,
                            "👋 Hello Jayant! Jayant AI Lab Studio is running 24/7 in the cloud on Hugging Face Spaces! Send me any topic or reply 'MAKE' to the latest radar alert!"
                        )
                        continue

                    topic_to_use = text
                    if text.strip().upper() == "MAKE":
                        topic_to_use = last_topic

                    last_topic = topic_to_use
                    print(f"[GENERATING FOR TOPIC]: {topic_to_use}")
                    send_tg_message(chat_id, "⚡ *Got it! Generating Hook, ZORO Script & Audio now... (Takes ~25s)*")

                    hook, body, cta, audio_path = generate_scripts_and_audio(topic_to_use)

                    reply_text = (
                        f"🎬 *NEW VIDEO ASSETS READY!*\n\n"
                        f"🎯 *YOUR HOOK (Record in Google Vids):*\n_{hook}_\n\n"
                        f"🤖 *ZORO'S BODY SCRIPT:*\n{body}\n\n"
                        f"📢 *YOUR CTA (Record in Google Vids):*\n_{cta}_\n\n"
                        f"🎧 *ZORO's Audio is attached below!*"
                    )
                    send_tg_message(chat_id, reply_text)
                    send_tg_audio(chat_id, audio_path, caption="🎙️ ZORO Audio (Rasalgethi • South Delhi)")
                    print("[SUCCESS] Assets and audio delivered to Telegram!")

        except Exception as e:
            print(f"Error in bot loop: {e}")
            time.sleep(3)


# Simple HTTP handler so Hugging Face Spaces knows the container is alive and healthy on port 7860
class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Jayant AI Lab Studio & AI Radar is running 24/7!")


def main():
    print("=" * 60)
    print("  JAYANT'S AI LAB — CLOUD DEPLOYMENT (HUGGING FACE SPACES)")
    print("=" * 60)

    # Start Radar scanner thread
    radar_thread = threading.Thread(target=scan_and_alert, daemon=True)
    radar_thread.start()

    # Start Telegram polling thread
    bot_thread = threading.Thread(target=bot_polling, daemon=True)
    bot_thread.start()

    send_tg_message(
        AUTHORIZED_CHAT_ID,
        "☁️ *Jayant's AI Lab Studio is now running 24/7 in the Cloud on Hugging Face Spaces!*\n\n"
        "You can safely close and turn off your laptop now. AI Radar will continue scanning the internet and pinging your phone uninterrupted! 🚀"
    )

    # Run lightweight HTTP server on port 7860 (Hugging Face default)
    server = HTTPServer(("0.0.0.0", 7860), HealthHandler)
    server.serve_forever()


if __name__ == "__main__":
    main()
