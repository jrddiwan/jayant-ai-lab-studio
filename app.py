# Jayant's AI Lab — Master Autonomous Studio Engine
# Cloud Host: Render.com (24/7 Always-On)
# Features:
# - Multi-Platform Multi-Source Radar:
#   * Tech News: The Verge, Ars Technica, TechCrunch, Wired, MIT Tech Review, MarkTechPost, Simon Willison
#   * Reddit AI: r/LocalLLaMA, r/artificial, r/MachineLearning, r/singularity, r/ChatGPT
#   * GitHub Trending: topic:llm & topic:artificial-intelligence
#   * Hugging Face Hub: Top models (DeepSeek, Meta, Qwen, Mistral, Google, etc.)
#   * X / Twitter Radar: @GoogleAI, @AIatMeta, @NVIDIAAI, @VaibhavSisinty, @opencode, @higgsfield_ai,
#                         @TheRundownAI, @FinanceYF5, @GoogleAIStudio, @OpenAI, @sama, @AnthropicAI,
#                         @DeepSeek, @GoogleDeepMind, @xAI, @karpathy
#   * 5 Live News & Search APIs with Strict Daily Quotas:
#       - Tavily (25/day cap, 1000/mo limit)
#       - Newsdata.io (150/day cap, 200/day limit)
#       - NewsAPI.org (80/day cap, 100/day limit)
#       - SerpAPI (6/day cap, 250/mo limit)
#       - FreeNewsAPI.io (2,500/day cap, 2 req/sec throttle)
#   * YouTube Channels with Baseline Publication Filter (Zero Past Videos)
# - Executive Quality Gate: Evaluates news items with Groq 120B / Gemini to filter fluff
# - Multi-Creator Master Scriptwriting: Vaibhav Sisinty Hook + AI Search ELI12 + Jayant Triad
# - Gemini 3.1 Flash TTS: ZORO Confident Male Voice with South Delhi Cadence (Rasalgethi)
# - 4 Distinct Instagram Carousel Styles (1080x1350 Portrait PNGs via Playwright):
#   1. Cyberpunk Glassmorphism (Anton + Frosted Glass + Emerald Glow)
#   2. Minimalist Bold Editorial (Syne + High Contrast + Electric Yellow Accent + Giant Numbers)
#   3. Framework & Comparison Matrix (Space Grotesk + Split Old vs New Table + Progress Rail)
#   4. Tweet-to-Carousel Hero (Authentic Dark-Mode X Card Mockup + Teardown Cards)
# - Strict <= 260 Char Tweet & High-Insight LinkedIn Post
# - "Prompt of the Day" WhatsApp Community Template
# - Strict Zero Phone Numbers Exposed (+91 78800 56262 banned)
# - Central Delivery Strictly to Jayant's Personal Telegram DM (7007116692)

import os
import sys
import io
import time
import json
import wave
import re

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if sys.stderr and hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")
import base64
import random
import threading
import requests
import urllib.request
import urllib.parse
from datetime import datetime, timezone
import xml.etree.ElementTree as ET
from http.server import HTTPServer, BaseHTTPRequestHandler
from PIL import Image
from google import genai
from dotenv import load_dotenv

# ─── LOAD ENVIRONMENT VARIABLES ───
load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_BOT_TOKEN_VIDEO = os.getenv("TELEGRAM_BOT_TOKEN_VIDEO", TELEGRAM_BOT_TOKEN)
TELEGRAM_BOT_TOKEN_CAROUSEL = os.getenv("TELEGRAM_BOT_TOKEN_CAROUSEL", TELEGRAM_BOT_TOKEN)
TELEGRAM_BOT_TOKEN_SOCIAL = os.getenv("TELEGRAM_BOT_TOKEN_SOCIAL", TELEGRAM_BOT_TOKEN)
AUTHORIZED_CHAT_ID = int(os.getenv("AUTHORIZED_CHAT_ID", "7007116692"))
ZORO_VOICE = os.getenv("ZORO_VOICE", "Rasalgethi")
TARGET_CHAT_ID = AUTHORIZED_CHAT_ID  # Deliver strictly to Jayant's personal DM

# ─── MULTI-KEY POOLS ───
GEMINI_KEYS = [k for k in [os.getenv("GEMINI_API_KEY_2", ""), os.getenv("GEMINI_API_KEY", "")] if k]
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
AGNES_KEYS = [k for k in [os.getenv("AGNES_API_KEY", ""), os.getenv("AGNES_API_KEY_2", "")] if k]
HF_TOKENS = [k for k in [os.getenv("HF_TOKEN", ""), os.getenv("HF_TOKEN_2", "")] if k]
OPENROUTER_KEYS = [k for k in [os.getenv("OPENROUTER_API_KEY", ""), os.getenv("OPENROUTER_API_KEY_2", "")] if k]

CF_CREDS = []
if os.getenv("CF_ACCOUNT") and os.getenv("CF_TOKEN"):
    CF_CREDS.append((os.getenv("CF_ACCOUNT"), os.getenv("CF_TOKEN")))
if os.getenv("CF_ACCOUNT_2") and os.getenv("CF_TOKEN_2"):
    CF_CREDS.append((os.getenv("CF_ACCOUNT_2"), os.getenv("CF_TOKEN_2")))

# ─── 5 NEWS & SEARCH APIS ───
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "")
NEWSDATA_API_KEY = os.getenv("NEWSDATA_API_KEY", "")
NEWSAPI_API_KEY = os.getenv("NEWSAPI_API_KEY", "")
SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY", "")
FREENEWSAPI_API_KEY = os.getenv("FREENEWSAPI_API_KEY", "")

TG_API_BASE = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"
OUTPUT_DIR = "telegram_outputs"
CAROUSEL_DIR = "carousel_outputs"
SEEN_FILE = "seen_topics.json"
QUOTA_FILE = "api_quota.json"

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(CAROUSEL_DIR, exist_ok=True)

# Baseline timestamp: Only accept releases published after startup
AUTOMATION_START_TIME = datetime.now(timezone.utc)
IS_INITIAL_BASELINE_DONE = False

# HTTP headers for public feeds
COMMON_HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"}

# ─── MEMORY & DEDUPLICATION ───
if os.path.exists(SEEN_FILE):
    try:
        with open(SEEN_FILE, "r", encoding="utf-8") as f:
            seen_topics = json.load(f)
    except Exception:
        seen_topics = {}
else:
    seen_topics = {}

# Rolling real-time activity feed for live web dashboard
RECENT_FEED = []


def save_memory():
    try:
        with open(SEEN_FILE, "w", encoding="utf-8") as f:
            json.dump(seen_topics, f, indent=2)
    except Exception as e:
        print(f"Error saving memory: {e}")


# ─── STRICT API QUOTA MANAGER (RESPECTS ALL LIMITS) ───
API_LIMITS = {
    "TAVILY": 25,        # 1,000 / month limit -> max 25 calls/day
    "NEWSDATA": 150,     # 200 / day limit -> max 150 calls/day
    "NEWSAPI": 80,       # 100 / day limit -> max 80 calls/day
    "SERPAPI": 6,        # 250 / month limit -> max 6 calls/day
    "FREENEWSAPI": 2500  # 5,000 / day limit -> max 2,500 calls/day (with 600ms sleep)
}


class QuotaManager:
    @staticmethod
    def _load():
        if os.path.exists(QUOTA_FILE):
            try:
                with open(QUOTA_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                pass
        return {"date": datetime.now(timezone.utc).strftime("%Y-%m-%d"), "usage": {}}

    @staticmethod
    def _save(data):
        try:
            with open(QUOTA_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Quota save error: {e}")

    @classmethod
    def can_call(cls, service_name):
        data = cls._load()
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        if data.get("date") != today:
            data = {"date": today, "usage": {}}
            cls._save(data)

        used = data["usage"].get(service_name, 0)
        limit = API_LIMITS.get(service_name, 50)
        return used < limit

    @classmethod
    def record_call(cls, service_name):
        data = cls._load()
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        if data.get("date") != today:
            data = {"date": today, "usage": {}}

        data["usage"][service_name] = data["usage"].get(service_name, 0) + 1
        cls._save(data)
        print(f"[QUOTA]: {service_name} used {data['usage'][service_name]} / {API_LIMITS.get(service_name, 0)} today")


# ─── TELEGRAM BROADCAST HELPERS ───
def _get_tg_base(bot_token=None):
    token = bot_token or TELEGRAM_BOT_TOKEN
    return f"https://api.telegram.org/bot{token}"


def send_tg_message(chat_id, text, bot_token=None):
    url = f"{_get_tg_base(bot_token)}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}
    try:
        r = requests.post(url, json=payload, timeout=15)
        if r.status_code != 200:
            print(f"[TG sendMessage Markdown rejected ({r.status_code})]: {r.text[:80]}. Retrying plain text...")
            requests.post(url, json={"chat_id": chat_id, "text": text}, timeout=15)
    except Exception as e:
        print(f"Error sending TG message: {e}")


def send_tg_photo(chat_id, photo_url_or_bytes, caption="", bot_token=None):
    url = f"{_get_tg_base(bot_token)}/sendPhoto"
    try:
        if isinstance(photo_url_or_bytes, str) and photo_url_or_bytes.startswith("http"):
            r = requests.post(url, json={"chat_id": chat_id, "photo": photo_url_or_bytes, "caption": caption, "parse_mode": "Markdown"}, timeout=20)
            if r.status_code != 200:
                requests.post(url, json={"chat_id": chat_id, "photo": photo_url_or_bytes, "caption": caption}, timeout=20)
        else:
            files = {"photo": photo_url_or_bytes}
            data = {"chat_id": chat_id, "caption": caption, "parse_mode": "Markdown"}
            r = requests.post(url, files=files, data=data, timeout=25)
            if r.status_code != 200:
                requests.post(url, files={"photo": photo_url_or_bytes}, data={"chat_id": chat_id, "caption": caption}, timeout=25)
    except Exception as e:
        print(f"Error sending TG photo: {e}")


def send_tg_audio(chat_id, audio_path, caption="", bot_token=None):
    url = f"{_get_tg_base(bot_token)}/sendAudio"
    try:
        with open(audio_path, "rb") as f:
            files = {"audio": f}
            data = {"chat_id": chat_id, "caption": caption}
            requests.post(url, files=files, data=data, timeout=35)
    except Exception as e:
        print(f"Error sending TG audio: {e}")


def send_tg_album(chat_id, images, caption="", bot_token=None):
    """Sends 7 carousel slides as an Instagram swipeable album (JPEG 92% compressed)."""
    url = f"{_get_tg_base(bot_token)}/sendMediaGroup"
    try:
        media = []
        files = {}
        for idx, img_ref in enumerate(images):
            attach_name = f"photo_{idx}"
            item = {"type": "photo", "media": f"attach://{attach_name}"}
            try:
                with Image.open(img_ref) as img:
                    rgb_img = img.convert("RGB")
                    buf = io.BytesIO()
                    rgb_img.save(buf, format="JPEG", quality=92, optimize=True)
                    img_bytes = buf.getvalue()
                files[attach_name] = (f"slide_{idx+1}.jpg", img_bytes, "image/jpeg")
            except Exception:
                files[attach_name] = open(img_ref, "rb")

            if idx == 0 and caption:
                item["caption"] = caption
                item["parse_mode"] = "Markdown"
            media.append(item)

        if files:
            data = {"chat_id": chat_id, "media": json.dumps(media)}
            res = requests.post(url, data=data, files=files, timeout=90)
            if res.status_code != 200:
                print(f"[TG sendMediaGroup failed ({res.status_code})]: {res.text[:80]}. Retrying without Markdown...")
                if media and "parse_mode" in media[0]:
                    del media[0]["parse_mode"]
                files_retry = {}
                for idx, img_ref in enumerate(images):
                    attach_name = f"photo_{idx}"
                    try:
                        with Image.open(img_ref) as img:
                            rgb_img = img.convert("RGB")
                            buf = io.BytesIO()
                            rgb_img.save(buf, format="JPEG", quality=92, optimize=True)
                            img_bytes = buf.getvalue()
                        files_retry[attach_name] = (f"slide_{idx+1}.jpg", img_bytes, "image/jpeg")
                    except Exception:
                        pass
                if files_retry:
                    res = requests.post(url, data={"chat_id": chat_id, "media": json.dumps(media)}, files=files_retry, timeout=90)
            return res.status_code == 200
    except Exception as e:
        print(f"Error sending TG album: {e}")
    return False


# ─── VISUAL GENERATION (AGNES AI / FLUX.1) ───
def generate_agnes_image(prompt, save_path):
    """Generates cinematic AI background art using Agnes AI with FLUX.1 failover."""
    for key in AGNES_KEYS:
        try:
            r = requests.post(
                "https://apihub.agnes-ai.com/v1/images/generations",
                headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
                json={
                    "model": "agnes-image-2.0-flash",
                    "prompt": f"{prompt}, dark atmospheric cinematic lighting, octane render, 8k, neon emerald green and obsidian dark mode, clean composition without text",
                    "size": "1024x1024"
                },
                timeout=30
            )
            if r.status_code == 200:
                data = r.json().get("data", [])
                if data and data[0].get("url"):
                    urllib.request.urlretrieve(data[0]["url"], save_path)
                    return True
        except Exception:
            pass

    raw_flux = generate_flux_image(f"{prompt}, dark cinematic octane render, 8k")
    if raw_flux:
        with open(save_path, "wb") as f:
            f.write(raw_flux)
        return True
    return False


def generate_flux_image(prompt):
    """Generate high-res visual proof card via Hugging Face FLUX.1-schnell with Cloudflare fallback."""
    for token in HF_TOKENS:
        try:
            api_url = "https://api-inference.huggingface.co/models/black-forest-labs/FLUX.1-schnell"
            headers = {"Authorization": f"Bearer {token}"}
            res = requests.post(api_url, headers=headers, json={"inputs": prompt}, timeout=25)
            if res.status_code == 200 and res.content:
                return res.content
        except Exception:
            pass

    for account, token in CF_CREDS:
        try:
            cf_url = f"https://api.cloudflare.com/client/v4/accounts/{account}/ai/run/@cf/bytedance/stable-diffusion-xl-lightning"
            r = requests.post(cf_url, headers={"Authorization": f"Bearer {token}"}, json={"prompt": prompt}, timeout=20)
            if r.status_code == 200 and r.content:
                return r.content
        except Exception:
            pass
    return None


# ─── 5-STYLE INSTAGRAM CAROUSEL RENDERER (FLAGSHIP EDITORIAL 7-SLIDE ENGINE) ───
CAROUSEL_STYLES = {
    "editorial": "carousel_style_editorial_pro.html",
    "cyber": "carousel_style_1_cyber.html",
    "minimal": "carousel_style_2_minimal.html",
    "matrix": "carousel_style_3_matrix.html",
    "tweet": "carousel_style_4_tweet.html"
}


def render_instagram_carousel(topic_title, topic_details, style="editorial"):
    """
    Renders ultra-crisp 1080x1350 portrait carousel slides.
    Flagship: 'editorial' produces 7 warm, magazine-grade slides modeled after @theautomationguy.ai
    with high-contrast branding for Jayant's AI Lab (@jayantsailab).
    Alternative styles: 'cyber', 'minimal', 'matrix', 'tweet'.
    """
    if style == "auto" or style not in CAROUSEL_STYLES:
        chosen_style = "editorial"
    else:
        chosen_style = style

    template_file = CAROUSEL_STYLES.get(chosen_style, "carousel_style_editorial_pro.html")
    print(f"[CAROUSEL]: Rendering with Style [{chosen_style}] -> {template_file}")

    carousel_json = None

    if chosen_style == "editorial":
        system_prompt = (
            "You are the chief design and content director for Jayant's AI Lab (@jayantsailab). "
            "Generate a structured 7-slide viral Instagram carousel modeled after top tech creators (@theautomationguy.ai, Rowan Cheung, Ruben Hassid). "
            "Every slide must have high information density, crisp typography, and actionable value. Return ONLY valid JSON."
        )
        user_prompt = f"""TOPIC: {topic_title}
DETAILS: {topic_details}

Generate all 7 slides in this exact narrative sequence:
- Slide 1 (slideType: 'hero'): Arresting hook headline split into titlePrefix, titleOrange (accent phrase), titleSuffix. Subtitle pill. Terminal box with 4 verified active items. Kraft sticky note with handwriting tone.
- Slide 2 (slideType: 'org_chart'): System Architecture & Orchestration. Leader orchestrator card + 4 department/fleet cards (01 to 04 with titles & descriptions). Sticky note.
- Slide 3 (slideType: 'grid_cards'): 6 Specialist Fleet items (01 to 06) with catchy uppercase tag, title, and 1-sentence actionable description. Sticky note.
- Slide 4 (slideType: 'workflows'): 4 Practical Execution Prompts (e.g., '01. Launch feature sprint', '02. Code audit') with 3-4 bullet tasks each. Sticky note.
- Slide 5 (slideType: 'benchmark'): The Cold Numbers. Side-by-side comparison: Old Manual Way (e.g. 4 Days, high retainers) vs Jayant's AI Lab Way (e.g. 35 Sec, $0 marginal cost). Bottom telemetry ROI highlight. Sticky note.
- Slide 6 (slideType: 'workflows'): 4 Production Business Use Cases (real day-to-day enterprise/builder deployments). Sticky note.
- Slide 7 (slideType: 'cta_final'): The Transformation. Bold headline ('Same Team. A More Capable You.'), clear value proposition, large button text ('Save This Carousel & Follow @jayantsailab'), 3 pills, and quote sign-off. Sticky note.

Return JSON strictly matching this schema:
{{
  "categoryTag": "SHORT CATEGORY (e.g. ● OPEN SOURCE • GITHUB, ● AUTONOMOUS WORKFLOW, ● LLM BENCHMARK)",
  "slides": [
    {{
      "slideType": "hero",
      "tagline": "NEW AI BREAKTHROUGH",
      "titlePrefix": "Someone",
      "titleOrange": "Open-Sourced",
      "titleSuffix": "an Entire AI Agency.",
      "subtitlePrefix": "250+ Specialized Agents. One System.",
      "subtitleHighlight": "FREE.",
      "terminalTitle": "ARCHITECTURE // AUTONOMOUS AGENT ORG",
      "repoUrl": "https://github.com/jayantsailab/agents",
      "terminalItems": [
        "✔ C-Suite Strategy Agent (Online)",
        "✔ Full-Stack Code Auditor (Active)",
        "✔ Autonomous Growth Engine (Synced)",
        "✔ Zero-Trust Security Gate (Verified)"
      ],
      "stickyNote": "Not just a chatbot.<br>A full team.",
      "stickyRotate": "2deg",
      "footerRight": "I'LL SHOW YOU WHAT THEY BUILT ➔"
    }},
    {{
      "slideType": "org_chart",
      "tagline": "THE ORG CHART",
      "titlePrefix": "Not Just Chatbots.",
      "titleOrange": "A Full Org Chart",
      "titleSuffix": "Of AI Workers.",
      "leaderTitle": "Chief AI Orchestrator (ZORO)",
      "leaderSub": "Receives one high-level prompt → coordinates the entire department fleet",
      "orgCards": [
        {{"num": "01", "title": "Engineering Fleet", "desc": "Code generation, CI/CD linting, automated PR reviews & refactoring"}},
        {{"num": "02", "title": "Marketing Engine", "desc": "Copywriting, programmatic SEO, carousel scripts & audience research"}},
        {{"num": "03", "title": "Ops & Finance", "desc": "Budget tracking, pipeline auditing, API rate-limit monitoring"}},
        {{"num": "04", "title": "Research & QA", "desc": "Paper verification, benchmark stress-tests, hallucination checks"}}
      ],
      "badgeBarLeft": "250+ AGENTS AND COUNTING...",
      "stickyNote": "Like a company.<br>But AI & open source.",
      "stickyRotate": "-2deg",
      "footerRight": "NEXT: MEET THE SPECIALISTS ➔"
    }},
    {{
      "slideType": "grid_cards",
      "tagline": "THE FIRST SIX HIRES",
      "titlePrefix": "You Don't Hire 250 People.",
      "titleOrange": "You Assemble",
      "titleSuffix": "Them.",
      "specialists": [
        {{"num": "01", "tag": "BUILD SHIP REPEAT", "title": "Frontend Engineer", "desc": "Generates UI components, layout systems, and responsive screens in seconds."}},
        {{"num": "02", "tag": "SYSTEM SCALES", "title": "Backend Architect", "desc": "Creates secure APIs, schema migrations, and high-throughput pipelines."}},
        {{"num": "03", "tag": "SECURITY FIRST", "title": "Code Auditor", "desc": "Catches exposed keys, SQL vulnerabilities, and logic flaws before merge."}},
        {{"num": "04", "tag": "REAL BENCHMARK", "title": "Reality Checker", "desc": "Stress tests outputs, verifies facts, and halts hallucinated claims."}},
        {{"num": "05", "tag": "GROWTH ENGINE", "title": "Content Strategist", "desc": "Transforms raw code updates into viral visual carousels and threads."}},
        {{"num": "06", "tag": "RETENTION MAGNET", "title": "Community Lead", "desc": "Engages questions, routes support requests, and builds user loyalty."}}
      ],
      "stickyNote": "Different skills.<br>Same goal.<br>Real work.",
      "stickyRotate": "3deg",
      "footerRight": "NEXT: REAL WORKFLOWS ➔"
    }},
    {{
      "slideType": "workflows",
      "tagline": "EXECUTION IN ACTION",
      "titlePrefix": "Imagine Giving Your Lab",
      "titleOrange": "One Single",
      "titleSuffix": "Instruction.",
      "workflows": [
        {{
          "prompt": "01. Launch a new feature sprint.",
          "tasks": ["Research user requests", "Write PRD & architecture", "Generate UI code", "Run test suite & deploy"]
        }},
        {{
          "prompt": "02. Audit entire codebase security.",
          "tasks": ["Scan for hardcoded keys", "Check API permission scopes", "Verify auth tokens", "Output patched branch"]
        }},
        {{
          "prompt": "03. Produce 30 days of tech content.",
          "tasks": ["Scrape trending AI papers", "Write viral creator hooks", "Render 7-slide decks", "Format X threads & posts"]
        }},
        {{
          "prompt": "04. Benchmark local LLM latency.",
          "tasks": ["Deploy quantized weights", "Run inference batch tests", "Compare RAM vs GPU", "Generate cost ledger"]
        }}
      ],
      "stickyNote": "You set the goal.<br>They handle the rest.",
      "stickyRotate": "-1deg",
      "footerRight": "NEXT: THE RAW NUMBERS ➔"
    }},
    {{
      "slideType": "benchmark",
      "tagline": "THE COLD NUMBERS",
      "titlePrefix": "Manual Chaos vs",
      "titleOrange": "Autonomous",
      "titleSuffix": "Execution.",
      "oldStat": "4 Days",
      "oldSub": "Per audit or feature deployment",
      "oldItems": [
        "• $3,500/mo contractor retainer",
        "• Context lost across meetings",
        "• Prone to human oversight",
        "• Bottlenecked by business hours"
      ],
      "newStat": "35 Sec",
      "newSub": "Autonomous local agent pipeline",
      "newItems": [
        "• $0 marginal inference cost",
        "• 24/7 continuous autonomous execution",
        "• Deterministic verification & tests",
        "• Scales to 100+ tasks in parallel"
      ],
      "roiHighlight": "99.4% TIME SAVED",
      "stickyNote": "Numbers don't lie.",
      "stickyRotate": "2deg",
      "footerRight": "NEXT: HOW TO DEPLOY ➔"
    }},
    {{
      "slideType": "workflows",
      "tagline": "DAY-TO-DAY INTEGRATION",
      "titlePrefix": "Where To Plug",
      "titleOrange": "This Pipeline",
      "titleSuffix": "In Your Business.",
      "workflows": [
        {{
          "prompt": "01. Client Onboarding Sprint",
          "tasks": ["Parse intake form & contract", "Generate workspace & DB tables", "Send customized welcome kit", "Notify account lead"]
        }},
        {{
          "prompt": "02. Daily Intelligence Radar",
          "tasks": ["Monitor 50+ AI sources", "Filter non-actionable fluff", "Synthesize executive briefing", "Publish cross-platform"]
        }},
        {{
          "prompt": "03. Codebase Refactoring",
          "tasks": ["Identify technical debt", "Generate type-safe patches", "Run local regression tests", "Create clean pull request"]
        }},
        {{
          "prompt": "04. Customer Support Triage",
          "tasks": ["Classify ticket urgency", "Draft solution from docs", "Execute DB health check", "Escalate blockers in seconds"]
        }}
      ],
      "stickyNote": "Automate. Learn.<br>Build. Scale.",
      "stickyRotate": "-2deg",
      "footerRight": "NEXT: TAKE ACTION ➔"
    }},
    {{
      "slideType": "cta_final",
      "tagline": "THE TRANSFORMATION",
      "titlePrefix": "Same Team.",
      "titleOrange": "A More Capable",
      "titleSuffix": "You.",
      "ctaMain": "The autonomous AI workforce is officially here.",
      "ctaSub": "Stop setting payroll on fire doing repetitive manual workflows. Start deploying battle-tested open-source agents today.",
      "buttonText": "Save This Carousel & Follow @jayantsailab",
      "stickyNote": "Same curiosity.<br>Bigger leverage.",
      "stickyRotate": "1deg",
      "footerRight": "FOLLOW @JAYANTSAILAB 🔖"
    }}
  ]
}}
"""
    else:
        system_prompt = f"You are the elite Instagram creative director for Jayant's AI Lab (@jayantsailab). Generate 6 slides for an educational carousel in style '{chosen_style}'. Return ONLY valid JSON."
        user_prompt = f"""TOPIC: {topic_title}
DETAILS: {topic_details}
STYLE: {chosen_style}

Create 6 slides:
- Slide 1: High-impact hook about this topic + accent phrase
- Slide 2: The Bottleneck / Old Manual Way vs New Way
- Slide 3: Under the Hood / Core Architecture
- Slide 4: Real-World Business Leverage / Time Saved
- Slide 5: The Tactical Blueprint / System Checklist
- Slide 6: Steal This Setup & Call to Action (DM 'AUDIT' or tap link in bio)

Return JSON:
{{
  "categoryTag": "SHORT PILL (e.g. AI WORKFLOW, AUTONOMOUS AGENT, PROMPT SYSTEM)",
  "slides": [
    {{
      "id": 1,
      "slideNum": "01 / 06",
      "hookPill": "⚡ AI BREAKTHROUGH",
      "title": "MAIN HEADLINE",
      "titleGreen": "ACCENT PHRASE.",
      "subtitle": "Subtitle explaining what this unlocks.",
      "tacticalHeading": "CORE ARCHITECTURE",
      "tacticalItems": ["Point 1", "Point 2", "Point 3", "Point 4"],
      "imagePrompt": "Futuristic dark cybernetic tech architecture, neon emerald lighting, 8k",
      "footerLeft": "SWIPE FOR STEP 2 ➔",
      "footerRight": "FOLLOW @jayantsailab 🔖"
    }}
  ]
}}
"""

    if GROQ_API_KEY:
        try:
            res = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
                json={
                    "model": "openai/gpt-oss-120b",
                    "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": user_prompt}],
                    "response_format": {"type": "json_object"}
                },
                timeout=30
            )
            if res.status_code == 200:
                carousel_json = json.loads(res.json()["choices"][0]["message"]["content"])
        except Exception as e:
            print(f"Groq carousel json error: {e}")

    if not carousel_json:
        for g_key in GEMINI_KEYS:
            for gm in ["gemini-3.6-flash", "gemini-3.5-flash-lite"]:
                try:
                    c = genai.Client(api_key=g_key)
                    r = c.models.generate_content(
                        model=gm,
                        contents=f"{system_prompt}\n\n{user_prompt}",
                        config={"response_mime_type": "application/json"}
                    )
                    if r.text:
                        carousel_json = json.loads(r.text)
                        break
                except Exception:
                    pass
            if carousel_json:
                break

    if not carousel_json or "slides" not in carousel_json or not carousel_json["slides"]:
        return []

    slides = carousel_json["slides"]
    category = carousel_json.get("categoryTag", "AI BREAKTHROUGH")
    ts = int(time.time())

    # For cyberpunk style, generate Agnes AI backgrounds
    bg1, bg2 = "", ""
    if chosen_style == "cyber":
        bg1 = os.path.abspath(os.path.join(CAROUSEL_DIR, f"bg_hero_{ts}.png"))
        bg2 = os.path.abspath(os.path.join(CAROUSEL_DIR, f"bg_arch_{ts}.png"))
        p1 = slides[0].get("imagePrompt", f"Dark cyber AI core for {topic_title[:50]}")
        p2 = slides[min(2, len(slides)-1)].get("imagePrompt", f"Dark holographic AI command center for {topic_title[:50]}")
        generate_agnes_image(p1, bg1)
        generate_agnes_image(p2, bg2)

    slide_paths = []
    try:
        from playwright.sync_api import sync_playwright
        template_path = os.path.abspath(template_file).replace("\\", "/")

        with sync_playwright() as p:
            browser = p.chromium.launch(args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage"])
            page = browser.new_page(viewport={"width": 1080, "height": 1350}, device_scale_factor=2)
            page.goto(f"file:///{template_path}")

            for i, s in enumerate(slides):
                idx = i + 1
                if chosen_style == "editorial":
                    s["currentSlide"] = idx
                    s["totalSlides"] = len(slides)
                    if "categoryTag" not in s or not s["categoryTag"]:
                        s["categoryTag"] = category
                    page.evaluate("(data) => setSlide(data)", s)
                else:
                    bg_to_use = (bg1 if idx <= 3 else bg2) if chosen_style == "cyber" else ""
                    payload = {
                        "imagePath": bg_to_use.replace("\\", "/") if bg_to_use else "",
                        "categoryTag": category,
                        "slideNum": s.get("slideNum", f"0{idx} / 0{len(slides)}"),
                        "hookPill": s.get("hookPill", "⚡ AI BREAKTHROUGH"),
                        "title": s.get("title", ""),
                        "titleGreen": s.get("titleGreen", ""),
                        "subtitle": s.get("subtitle", ""),
                        "tacticalHeading": s.get("tacticalHeading", "CORE SPECIFICATIONS"),
                        "tacticalItems": s.get("tacticalItems", []),
                        "footerLeft": s.get("footerLeft", "SWIPE FOR NEXT ➔"),
                        "footerRight": s.get("footerRight", "FOLLOW @jayantsailab 🔖")
                    }
                    page.evaluate("(data) => setSlide(data)", payload)

                page.wait_for_timeout(350)
                out_file = os.path.abspath(os.path.join(CAROUSEL_DIR, f"slide_{ts}_{idx}.png"))
                page.screenshot(path=out_file)
                slide_paths.append(out_file)

            browser.close()
    except Exception as pe:
        print(f"Playwright rendering error: {pe}")

    return slide_paths


# ─── EXECUTIVE QUALITY GATE (GROQ 120B / GEMINI) ───
def evaluate_news_worth(title, summary=""):
    """
    Evaluates whether an item covers a genuine, actionable AI tool or breakthrough.
    Suppresses podcast banter, vague gossip, and non-actionable fluff.
    """
    eval_prompt = f"""You are the Executive Producer for Jayant's AI Lab.
Title: {title}
Summary: {summary}

Determine if this covers an actionable new AI tool, framework, model release, or practical automation that businesses or creators can use immediately.
If it is generic gossip, routine company politics, or vague opinions, reply strictly with:
REJECT: [Reason]

If it showcases a genuine tool, model, or workflow worthy of a dedicated breakdown, reply strictly with:
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
        except Exception:
            pass

    for g_key in GEMINI_KEYS:
        try:
            c = genai.Client(api_key=g_key)
            r = c.models.generate_content(model="gemini-3.6-flash", contents=eval_prompt)
            out = r.text.strip()
            if out.startswith("APPROVE"):
                return True, out.replace("APPROVE:", "").strip()
            else:
                return False, out.replace("REJECT:", "").strip()
        except Exception:
            pass

    return True, title


# ─── MASTER SCRIPTWRITING ENGINE (1,000 VIRAL HOOKS, LINKEDIN SKILLS, STORYTELLING & HUMANIZER) ───
def generate_full_studio_package(topic_title, topic_details, source_url="", carousel_style="auto"):
    # Dynamically select creator hook and CTA frameworks from the 1,000 Viral Hook vault & LinkedIn Skills
    hook_frameworks = [
        # Category A: 1,000 Viral Hooks (Educational & Breakdown)
        "EDUCATIONAL_60S (1,000 Hooks): 'Can you tell us how to {result} in 60 seconds? Here is exactly how much {action} you need.' High clarity, fast pace.",
        "EDUCATIONAL_DECADE (1,000 Hooks): 'It took me 10 years to learn this, but I will teach it to you in less than 60 seconds.' Condense massive complexity into pure signal.",
        "STEP_BY_STEP_TUTORIAL (1,000 Hooks): 'Everyone tells you to {action}, but nobody actually tells you how to do it. Here is the step-by-step tutorial you can save.'",
        "WAKE_UP_PAIN (1,000 Hooks): 'If I woke up with {pain_point} tomorrow and wanted {dream_result} by next week, here is exactly what I would do.'",
        
        # Category B: 1,000 Viral Hooks (Comparison & Contrarian)
        "SIDE_BY_SIDE_COMPARISON (1,000 Hooks): 'This is an old manual agency setup, and this is an autonomous agent lab. For this cost, you could have all of this.'",
        "GROUP_CONTRAST (1,000 Hooks): 'This team didn't automate this workflow, and this team did. Look at what happened to their payroll.'",
        "PSYCHO_EFFICIENCY (1,000 Hooks): 'Why do manual {action} like a normal agency when you can deploy local autonomous agents instead?'",
        
        # Category C: 1,000 Viral Hooks (Myth Busting & Warning)
        "MYTH_BUSTER (1,000 Hooks): 'They said \"{famous_quote_or_cliche}\". That is a lie. Here is what actually happens in production.'",
        "STOP_DOING_THIS (1,000 Hooks): 'Stop {action} if you actually want {dream_result}. You are burning hours without even realizing it.'",
        "DE_INFLUENCE (1,000 Hooks): 'Let me de-influence you from paying $3,000/mo retainers for manual AI tasks. Here is the local open-source setup.'",
        
        # Category D: LinkedIn Skills & Founder Mode (Serge Bulaev)
        "FOUNDER_REPRICE_CATEGORY (LinkedIn Founder Mode): 'Traditional agencies charge $4,000/month for this. Here is how we engineered it locally with $0 marginal cost.'",
        "FOUNDER_UNGLAMOROUS_BET (LinkedIn Founder Mode): 'While everyone is hyping general chatbots, we built 6 boring specialized agents that do real work.'",
        "FOUNDER_LIMIT_OF_DELEGATION (LinkedIn Founder Mode): 'You cannot delegate strategic judgment to an AI. But you can delegate the entire execution pipeline.'",
        "FOUNDER_SCARCE_SHOTS (LinkedIn Founder Mode): 'When you run a lean lab, you do not have 10 engineers. You have 10 autonomous loops running while you sleep.'",
        "FOUNDER_CONTENT_TO_PIPELINE (LinkedIn Founder Mode): 'How one open-source repo turned raw GitHub commits into qualified inbound clients without cold outreach.'"
    ]
    selected_hook = random.choice(hook_frameworks)

    # Narrative Storytelling Structure (from Storytelling Structures: Hero's Journey, Man in a Hole, About Me)
    storytelling_structures = [
        "HERO_JOURNEY: 1. Intro & Hero -> 2. Inflection Point (burning pain/symptoms) -> 3. Failed Attempts (what didn't work) -> 4. The Breakthrough (the one tool/workflow that worked) -> 5. Proof (quantifiable metrics) -> 6. Resolution / Next Step.",
        "MAN_IN_A_HOLE: 1. Comfort Zone (everything seemed fine) -> 2. The Trigger (a costly disruption or bottleneck hit) -> 3. The Crisis (realizing traditional methods failed) -> 4. The Recovery (deploying autonomous AI) -> 5. The Better Place (sovereign speed & zero overhead).",
        "ORIGIN_EPIPHANY: 1. The Starting Line -> 2. The Conflict (wasting payroll on manual tasks) -> 3. The Epiphany (agents > chatbots) -> 4. The Change (building deterministic pipelines) -> 5. The Mission (helping builders scale)."
    ]
    selected_story_structure = random.choice(storytelling_structures)

    cta_frameworks = [
        "BLUEPRINT_GIVEAWAY: Offer our lab's production prompt stack + agent workflow architecture. (Save post 🔖 and comment 'BLUEPRINT' or check link in bio).",
        "TACTICAL_CHALLENGE: Challenge founders and builders to plug this pipeline into one bottleneck today and share their benchmark in the comments.",
        "CONTRARIAN_DEBATE: Ask a high-signal polarizing question ('Is this true operational disruption or overhyped PR? Drop your take below, Jayant is replying').",
        "LAB_COMMUNITY_RETENTION: Save this teardown for your next build sprint 🔖 and follow @jayantsailab for unfiltered, production-tested AI deployments.",
        "PRIVATE_LAB_IMPLEMENTATION: If scaling a business and wanting Jayant's team to engineer this autonomous pipeline custom for your operations, tap link in bio to apply."
    ]
    selected_cta = random.choice(cta_frameworks)

    prompt = f"""You are the chief viral scriptwriter and content director for Jayant's AI Lab (@jayantsailab).
Topic: {topic_title}
Details: {topic_details}
Selected Hook Framework: {selected_hook}
Selected Storytelling Structure: {selected_story_structure}
Selected Call To Action: {selected_cta}

Write an authentic, highly engaging studio distribution package blending top creator styles (Alex Hormozi, Rowan Cheung, Dan Koe, Matt Wolfe, Justin Welsh) with Jayant's high-energy South Delhi tech authority.

STRICT HUMANIZER & WRITING RULES (Zero AI Giveaways):
1. ABSOLUTE BAN ON EM DASHES: NEVER use em dashes ('—' or '--'). Use standard commas, periods, or clean line breaks.
2. ABSOLUTE BAN ON AI BUZZWORDS: NEVER use 'delve', 'testament', 'beacon', 'tapestry', 'landscape', 'revolutionize', 'game-changer', 'unlock', 'navigate', 'elevate', 'harness', 'moreover', 'furthermore', 'in today\\'s fast-paced world', 'buckle up', 'stop scrolling', 'without further ado'.
3. NO RULE-OF-THREE CLICHES: Ban repetitive triads like 'fast, scalable, and robust' or three parallel consecutive sentences.
4. HUMAN CADENCE & RHYTHM: Alternate sentence lengths naturally. A punchy 4-word sentence. Then a conversational explanation. Write like a human builder in public, not a corporate marketing bot.
5. STORYTELLING ARC: Structure ZORO's script and the LinkedIn post using the selected Storytelling Structure ({selected_story_structure}). Show the struggle, the failed attempt, and the exact breakthrough.
6. NATURAL ZORO OPENERS: Never say '[cheerfully] Hey everyone, ZORO here!'. Open like a confident engineer: 'ZORO on deck. Let\\'s skip the marketing fluff and look at the actual numbers.', 'ZORO here from Jayant\\'s Lab. Here is the operational breakdown.', 'Alright, let\\'s see what actually shipped.'
7. DIVERSE & ORGANIC CTA: Strictly follow the selected Call To Action framework ({selected_cta}).
8. STRICT PHONE NUMBER BAN: NEVER include any phone numbers (+91 78800 56262, 7880056262, or wa.me links are STRICTLY FORBIDDEN). Always direct to Link in Bio or DM.
9. BRAND IDENTITY: Strictly 'Jayant\\'s AI Lab', handle '@jayantsailab', avatar badge 'JL'.

Return EXACT tags:

[HOOK]
(5-8 seconds for Google Vids Avatar. Deliver a punchy, arresting opening using the selected hook framework: {selected_hook}. Seamlessly transition to the lab breakdown.)

[ZORO_BODY]
(35-45 seconds, ~100-120 words for ZORO, Jayant's AI employee. Follow the {selected_story_structure} arc: identify the friction, explain the tool with a dead-simple analogy, give 1 sharp quantifiable metric, and finish with a confident takeaway. No bracketed stage directions.)

[B_ROLL_LIST]
(3-4 specific visual B-roll cues with timestamps [00:08 - 00:18] and AI video generation prompts for Kling/Luma/Runway.)

[CTA]
(6-8 seconds for Google Vids Avatar using the selected Call To Action Framework: {selected_cta}.)

[TWEET]
(Strictly <= 260 characters total. Contrarian hook + 1 key metric + link in bio / bookmark. Zero em dashes. Zero phone numbers.)

[LINKEDIN]
(Viral Hook Line -> The Friction & Problem -> Failed Alternative -> The Breakthrough 3-Step Architecture -> Quantifiable Proof & Math -> Actionable Takeaway -> Engaging closing question / Asset giveaway CTA. Humanized, zero buzzwords, zero em dashes.)

[CAROUSEL]
Slide 1: High-Impact Curiosity / Contrarian Title Hook
Slide 2: The Bottleneck (The Old Slow Way vs The Agent Way)
Slide 3: The Architecture (How it works under the hood - simple analogy)
Slide 4: Step-by-Step Blueprint (Input -> Prompt / Model -> Automated Output)
Slide 5: Quantifiable ROI (Hours saved, cost reduction, or speedup)
Slide 6: Dynamic CTA (Aligned with the selected CTA framework, saving post & following @jayantsailab)

[PROMPT_OF_THE_DAY]
(A ready-to-copy, production-grade prompt template or workflow snippet for this topic to share in the Jayant's AI Lab community.)
"""
    raw_text = None
    if GROQ_API_KEY:
        try:
            g_res = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
                json={"model": "openai/gpt-oss-120b", "messages": [{"role": "user", "content": prompt}], "temperature": 0.5},
                timeout=25
            )
            if g_res.status_code == 200:
                raw_text = g_res.json()["choices"][0]["message"]["content"]
        except Exception:
            pass

    if not raw_text:
        for g_key in GEMINI_KEYS:
            try:
                g_client = genai.Client(api_key=g_key)
                gem_res = g_client.models.generate_content(model="gemini-3.6-flash", contents=prompt)
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

    hook = extract_tag("HOOK", raw_text) or f"Stop doing manual workflows. {topic_title} just changed the math on AI automation. Let's look under the hood with ZORO."
    body = extract_tag("ZORO_BODY", raw_text) or f"ZORO here from Jayant's AI Lab. {topic_title} is live, and here is the exact benchmark you need to know."
    b_roll = extract_tag("B_ROLL_LIST", raw_text) or "• [00:08 - 00:20] Screen capture of tool UI\n• [00:20 - 00:35] Side-by-side speed test"
    cta = extract_tag("CTA", raw_text) or "Save this breakdown for your next build sprint, and follow @jayantsailab for battle-tested AI blueprints. See you in the lab."
    tweet = extract_tag("TWEET", raw_text) or f"AI update: {topic_title}. Follow @jayantsailab for production workflows."
    linkedin = extract_tag("LINKEDIN", raw_text) or topic_details
    carousel = extract_tag("CAROUSEL", raw_text) or "Slide 1: Breaking AI Update\nSlide 2: Check it out!"
    prompt_magnet = extract_tag("PROMPT_OF_THE_DAY", raw_text) or "Test this tool today."

    # ─── HUMANIZER POST-PROCESSOR (ENFORCE ZERO AI GIVEAWAYS) ───
    def humanize_text(t):
        if not t:
            return ""
        # 1. Enforce strict ban on em dashes and double dashes
        t = t.replace(" — ", ", ").replace("—", ", ").replace(" -- ", ", ").replace("--", ", ")
        # 2. Scrub AI buzzwords if any slipped through
        buzzwords = {
            "a game-changer": "a major breakthrough",
            "game-changer": "major shift",
            "delve into": "look into",
            "delve": "explore",
            "testament to": "proof of",
            "beacon of": "example of",
            "tapestry": "system",
            "landscape": "market",
            "revolutionize": "upgrade",
            "in today's fast-paced world": "today",
            "buckle up": "here is what matters",
            "stop scrolling": "look at this"
        }
        for bw, rep in buzzwords.items():
            t = re.sub(re.escape(bw), rep, t, flags=re.IGNORECASE)
        # 3. Clean up double spaces or awkward comma spacing
        t = re.sub(r' ,', ',', t)
        t = re.sub(r'\s+', ' ', t)
        return t.strip()

    hook = humanize_text(hook)
    body = humanize_text(body)
    cta = humanize_text(cta)
    tweet = humanize_text(tweet)
    linkedin = humanize_text(linkedin)

    # Strict scrub of any phone numbers
    for forbidden in ["+91 78800 56262", "+917880056262", "7880056262", "wa.me/917880056262", "wa.me/7880056262"]:
        tweet = tweet.replace(forbidden, "link in bio")
        linkedin = linkedin.replace(forbidden, "link in bio")
        cta = cta.replace(forbidden, "link in bio")

    if len(tweet) > 260:
        tweet = tweet[:257] + "..."

    # Voice track synthesis via Gemini 3.1 Flash TTS (Director's Notes steering for authentic Indian English / South Delhi cadence)
    clean_body = body.strip()
    for bracket in ["[cheerfully]", "[excitedly]", "[energetically]", "[confidently]", "[upbeat]"]:
        clean_body = clean_body.replace(bracket, "").strip()
    # For TTS synthesis, keep to ~120-150 words (punchy 45-60s reel audio)
    tts_text = clean_body[:800]

    director_input = f"""## "Jayant AI Lab Intelligence Brief"

### DIRECTOR'S NOTES
Style:
* Voice: Energetic, charismatic Indian tech authority
* Pace: Dynamic tech founder cadence, fast and punchy
* Accent: Natural urban Indian English accent from South Delhi, India

### TRANSCRIPT
{tts_text}
"""
    from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeout

    audio_data = None
    def _synthesize_voice(key, prompt_text):
        g_client_tts = genai.Client(api_key=key)
        interaction = g_client_tts.interactions.create(
            model="gemini-3.1-flash-tts-preview",
            input=prompt_text,
            response_format={"type": "audio"},
            generation_config={"speech_config": [{"voice": ZORO_VOICE}]}
        )
        return base64.b64decode(interaction.output_audio.data)

    for g_key in GEMINI_KEYS:
        executor = ThreadPoolExecutor(max_workers=1)
        try:
            future = executor.submit(_synthesize_voice, g_key, director_input)
            audio_data = future.result(timeout=20)
            executor.shutdown(wait=False, cancel_futures=True)
            if audio_data:
                break
        except FutureTimeout:
            executor.shutdown(wait=False, cancel_futures=True)
            print("[TTS Warning]: Gemini Flash TTS took >20s, proceeding without audio to keep pipeline real-time.")
            break
        except Exception as e:
            executor.shutdown(wait=False, cancel_futures=True)
            print(f"TTS error: {e}")

    timestamp = int(time.time())
    audio_path = os.path.join(OUTPUT_DIR, f"zoro_{timestamp}.wav")
    if audio_data:
        with wave.open(audio_path, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(24000)
            wf.writeframes(audio_data)

    # Render 6-slide carousel using the chosen style
    carousel_images = render_instagram_carousel(topic_title, carousel, style=carousel_style)

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


# ─── MULTI-SOURCE RADAR COLLECTORS ───

def fetch_tech_news():
    """Scans 7 top tech news RSS feeds for fresh AI stories."""
    items = []
    feeds = [
        ("The Verge AI", "https://www.theverge.com/rss/ai-artificial-intelligence/index.xml"),
        ("Ars Technica", "https://feeds.arstechnica.com/arstechnica/technology-lab"),
        ("TechCrunch AI", "https://techcrunch.com/category/artificial-intelligence/feed/"),
        ("Wired AI", "https://www.wired.com/feed/tag/ai/latest/rss"),
        ("MIT Tech Review", "https://www.technologyreview.com/feed/"),
        ("MarkTechPost", "https://www.marktechpost.com/feed/"),
        ("Simon Willison", "https://simonwillison.net/atom/everything/"),
    ]
    for name, url in feeds:
        try:
            r = requests.get(url, headers=COMMON_HEADERS, timeout=8)
            if r.status_code == 200:
                root = ET.fromstring(r.content)
                entries = root.findall(".//item")
                if not entries:
                    entries = root.findall(".//{http://www.w3.org/2005/Atom}entry")
                for entry in entries[:3]:
                    t_el = entry.find("title") if entry.find("title") is not None else entry.find("{http://www.w3.org/2005/Atom}title")
                    l_el = entry.find("link") if entry.find("link") is not None else entry.find("{http://www.w3.org/2005/Atom}link")
                    title = t_el.text.strip() if t_el is not None and t_el.text else ""
                    link = l_el.text.strip() if l_el is not None and l_el.text else (l_el.attrib.get("href", "") if l_el is not None else "")
                    if title:
                        items.append({"source": name, "title": title, "url": link, "type": "tech_news"})
        except Exception:
            pass
    return items


def fetch_reddit():
    """Scans 5 top AI subreddits via official RSS feeds."""
    items = []
    subreddits = ["LocalLLaMA", "artificial", "MachineLearning", "singularity", "ChatGPT"]
    for sub in subreddits:
        try:
            url = f"https://www.reddit.com/r/{sub}/.rss"
            r = requests.get(url, headers=COMMON_HEADERS, timeout=8)
            if r.status_code == 200:
                root = ET.fromstring(r.content)
                for entry in root.findall(".//{http://www.w3.org/2005/Atom}entry")[:3]:
                    t_el = entry.find("{http://www.w3.org/2005/Atom}title")
                    l_el = entry.find("{http://www.w3.org/2005/Atom}link")
                    title = t_el.text.strip() if t_el is not None and t_el.text else ""
                    link = l_el.attrib.get("href", "") if l_el is not None else ""
                    if title:
                        items.append({"source": f"Reddit r/{sub}", "title": title, "url": link, "type": "reddit"})
        except Exception:
            pass
    return items


def fetch_huggingface():
    """Monitors Hugging Face API for major model releases."""
    items = []
    try:
        url = "https://huggingface.co/api/models?sort=createdAt&direction=-1&limit=25"
        r = requests.get(url, headers=COMMON_HEADERS, timeout=8)
        if r.status_code == 200:
            for m in r.json():
                mid = m.get("id", "")
                if any(org in mid.lower() for org in ["qwen", "deepseek", "meta", "mistral", "google", "flash", "vision", "omni", "reason", "black-forest"]):
                    items.append({
                        "source": "Hugging Face Hub",
                        "title": f"New Model Drop: {mid}",
                        "url": f"https://huggingface.co/{mid}",
                        "type": "huggingface"
                    })
    except Exception:
        pass
    return items


def fetch_github():
    """Monitors GitHub trending repositories under topic:llm and python AI tools."""
    items = []
    try:
        url = "https://api.github.com/search/repositories?q=topic:llm+language:python&sort=updated&order=desc&per_page=8"
        r = requests.get(url, headers={"User-Agent": "JayantAILab/1.0"}, timeout=8)
        if r.status_code == 200:
            for repo in r.json().get("items", []):
                items.append({
                    "source": "GitHub Trending",
                    "title": f"Repo: {repo.get('full_name')} ({repo.get('description', '')[:70]})",
                    "url": repo.get("html_url"),
                    "type": "github"
                })
    except Exception:
        pass
    return items


def fetch_x_twitter():
    """
    Monitors all user-specified X / Twitter accounts via syndication feeds:
    @GoogleAI, @AIatMeta, @NVIDIAAI, @VaibhavSisinty, @opencode, @higgsfield_ai,
    @TheRundownAI, @FinanceYF5, @GoogleAIStudio, plus @OpenAI, @sama, @AnthropicAI,
    @DeepSeek, @GoogleDeepMind, @xAI, @karpathy.
    """
    items = []
    handles_query = "site:x.com (GoogleAI OR AIatMeta OR NVIDIAAI OR VaibhavSisinty OR opencode OR higgsfield_ai OR TheRundownAI OR FinanceYF5 OR GoogleAIStudio OR OpenAI OR AnthropicAI OR DeepSeek OR GoogleDeepMind OR xAI OR karpathy)"
    try:
        url = f"https://news.google.com/rss/search?q={urllib.parse.quote(handles_query)}&hl=en-US&gl=US&ceid=US:en"
        r = requests.get(url, headers=COMMON_HEADERS, timeout=8)
        if r.status_code == 200:
            root = ET.fromstring(r.content)
            for item in root.findall(".//item")[:6]:
                title = item.find("title").text if item.find("title") is not None else ""
                link = item.find("link").text if item.find("link") is not None else ""
                if title:
                    items.append({"source": "X / Twitter Radar", "title": title, "url": link, "type": "x_twitter"})
    except Exception:
        pass
    return items


def fetch_news_apis():
    """Queries Tavily, NewsAPI.org, SerpAPI, and Newsdata.io strictly respecting daily quotas."""
    items = []

    # 1. Tavily AI Search (budgeted cap: 25/day)
    if TAVILY_API_KEY and QuotaManager.can_call("TAVILY"):
        try:
            QuotaManager.record_call("TAVILY")
            r = requests.post(
                "https://api.tavily.com/search",
                json={"api_key": TAVILY_API_KEY, "query": "trending artificial intelligence breakthrough launch new model", "max_results": 3},
                timeout=10
            )
            if r.status_code == 200:
                for res in r.json().get("results", [])[:3]:
                    title = res.get("title", "")
                    link = res.get("url", "")
                    if title:
                        items.append({"source": "Tavily AI Search", "title": title, "url": link, "type": "api_news"})
        except Exception as e:
            print(f"Tavily fetch error: {e}")

    # 2. NewsAPI.org (budgeted cap: 80/day)
    if NEWSAPI_API_KEY and QuotaManager.can_call("NEWSAPI"):
        try:
            QuotaManager.record_call("NEWSAPI")
            url = f"https://newsapi.org/v2/everything?q=artificial+intelligence&pageSize=3&sortBy=publishedAt&apiKey={NEWSAPI_API_KEY}"
            r = requests.get(url, timeout=10)
            if r.status_code == 200:
                for art in r.json().get("articles", [])[:3]:
                    title = art.get("title", "")
                    link = art.get("url", "")
                    src = art.get("source", {}).get("name", "NewsAPI")
                    if title:
                        items.append({"source": f"NewsAPI ({src})", "title": title, "url": link, "type": "api_news"})
        except Exception as e:
            print(f"NewsAPI fetch error: {e}")

    # 3. SerpAPI Google News (budgeted cap: 6/day)
    if SERPAPI_API_KEY and QuotaManager.can_call("SERPAPI"):
        try:
            QuotaManager.record_call("SERPAPI")
            url = f"https://serpapi.com/search.json?q=AI+breakthrough+news&engine=google_news&api_key={SERPAPI_API_KEY}"
            r = requests.get(url, timeout=10)
            if r.status_code == 200:
                for res in r.json().get("news_results", [])[:3]:
                    title = res.get("title", "")
                    link = res.get("link", "")
                    src = res.get("source", {}).get("name", "Google News")
                    if title:
                        items.append({"source": f"SerpAPI ({src})", "title": title, "url": link, "type": "api_news"})
        except Exception as e:
            print(f"SerpAPI fetch error: {e}")

    # 4. Newsdata.io (budgeted cap: 150/day)
    if NEWSDATA_API_KEY and QuotaManager.can_call("NEWSDATA"):
        try:
            QuotaManager.record_call("NEWSDATA")
            url = f"https://newsdata.io/api/1/news?apikey={NEWSDATA_API_KEY}&q=artificial%20intelligence&language=en"
            r = requests.get(url, timeout=10)
            if r.status_code == 200:
                for res in r.json().get("results", [])[:3]:
                    title = res.get("title", "")
                    link = res.get("link", "")
                    src = res.get("source_id", "Newsdata")
                    if title:
                        items.append({"source": f"Newsdata ({src})", "title": title, "url": link, "type": "api_news"})
        except Exception as e:
            print(f"Newsdata fetch error: {e}")

    return items


# ─── YOUTUBE RADAR WITH PUBLICATION FILTER ───
YOUTUBE_CHANNELS = [
    ("The AI Search", "UCIgnGlGkVRhd4qNFcEwLL4A"),
    ("Vaibhav Sisinty", "UClXAalunTPaX1YV185DWUeg"),
    ("Matt Wolfe", "UChpleBmo18P08aKCIgti38g"),
    ("AI Explained", "UCNJ1Ymd5yFuUPtn21xtRbbw"),
    ("Matthew Berman", "UCzi5kcwU8aT4aLR7LcYhfWQ"),
    ("Wes Roth", "UCqcbQf6yw5KzRoDDcZ_wBSw")
]


def check_youtube_uploads():
    """Scans channels for brand-new videos published strictly AFTER startup."""
    global IS_INITIAL_BASELINE_DONE

    for channel_name, cid in YOUTUBE_CHANNELS:
        try:
            feed_url = f"https://www.youtube.com/feeds/videos.xml?channel_id={cid}"
            r = requests.get(feed_url, timeout=15)
            if r.status_code == 200:
                root = ET.fromstring(r.content)
                entries = root.findall("{http://www.w3.org/2005/Atom}entry")

                # Baseline seeding on startup: mark all existing videos as baseline seen
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

                    try:
                        pub_dt = datetime.fromisoformat(published_str.replace("Z", "+00:00"))
                        if pub_dt < AUTOMATION_START_TIME:
                            seen_topics[vid_id] = {"skipped_old": True}
                            save_memory()
                            continue
                    except Exception:
                        pass

                    if vid_id not in seen_topics:
                        seen_topics[vid_id] = {"title": title, "channel": channel_name, "processed": True}
                        save_memory()

                        is_worthy, reason = evaluate_news_worth(title)
                        RECENT_FEED.insert(0, {
                            "time": datetime.now(timezone.utc).strftime("%H:%M:%S"),
                            "source": f"YouTube ({channel_name})",
                            "title": title,
                            "url": video_url,
                            "status": "APPROVED" if is_worthy else "FILTERED",
                            "reason": reason
                        })
                        if len(RECENT_FEED) > 40:
                            RECENT_FEED.pop()

                        if not is_worthy:
                            print(f"[RADAR SUPPRESSED]: {title} -> {reason}")
                            continue

                        print(f"[RADAR APPROVED]: {title} ({reason})")
                        deliver_production_package(title, f"Covered by {channel_name} on YouTube: {video_url}", source_url=video_url, source_name=f"YouTube ({channel_name})")

        except Exception as e:
            print(f"Error checking YouTube channel {channel_name}: {e}")

    IS_INITIAL_BASELINE_DONE = True


# ─── MASTER RADAR AGGREGATOR & DISPATCHER ───
def deliver_production_package(title, details, source_url="", source_name=""):
    """Generates and delivers the complete multi-asset production package to Jayant's DM."""
    # Flagship: Warm Magazine Editorial (7 slides @theautomationguy.ai aesthetic with clear branding)
    chosen_style = "editorial"
    try:
        pkg = generate_full_studio_package(title, details, source_url=source_url, carousel_style=chosen_style)
    except Exception as e:
        print(f"[Studio Dispatch Error] Failed generating package for '{title}': {e}")
        return

    src_display = source_name or "AI Intelligence Radar"
    src_link = f"[{src_display}]({source_url})" if source_url else f"`{src_display}`"

    # 1. Video Production Package
    try:
        video_msg = (
            f"🎬 *NEW RADAR PRODUCTION PACK*\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🌐 *SOURCE:* {src_link}\n"
            f"📰 *HEADLINE:* {title}\n"
            f"🎨 *CAROUSEL STYLE:* `{chosen_style.upper()}`\n\n"
            f"🎯 *YOUR HOOK (Google Vids Avatar):*\n_{pkg.get('hook', '')}_\n\n"
            f"🤖 *ZORO BODY SCRIPT (ELI12):*\n{pkg.get('body', '')}\n\n"
            f"📢 *YOUR CTA (Google Vids Avatar):*\n_{pkg.get('cta', '')}_\n\n"
            f"🎥 *AUTOMATED B-ROLL SCENE LIST & AI PROMPTS:*\n{pkg.get('b_roll', '')}\n\n"
            f"🎧 *ZORO's audio track is attached below!*"
        )
        send_tg_message(TARGET_CHAT_ID, video_msg, bot_token=TELEGRAM_BOT_TOKEN_VIDEO)
        if pkg.get('audio_path') and os.path.exists(pkg['audio_path']):
            send_tg_audio(TARGET_CHAT_ID, pkg['audio_path'], caption=f"🎙️ ZORO Audio ({ZORO_VOICE} • South Delhi Cadence)", bot_token=TELEGRAM_BOT_TOKEN_VIDEO)
    except Exception as e:
        print(f"[Video Bot Dispatch Error]: {e}")

    # 2. Instagram Carousel Album (Delivered via Carousel Studio Bot)
    try:
        if pkg.get('carousel_images'):
            send_tg_album(TARGET_CHAT_ID, pkg['carousel_images'], caption=f"📱 *Instagram Carousel ({chosen_style.upper()}): {title[:60]}*\n🌐 *Source:* {src_link}", bot_token=TELEGRAM_BOT_TOKEN_CAROUSEL)
        else:
            print("[Carousel Bot] No carousel images generated.")
    except Exception as e:
        print(f"[Carousel Bot Dispatch Error]: {e}")

    # 3. Omnichannel Social Pack (Delivered via Social & News Bot)
    try:
        social_msg = (
            f"📢 *OMNICHANNEL SOCIAL DISTRIBUTION PACK*\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"🌐 *ORIGINAL INTEL SOURCE:* {src_link}\n\n"
            f"🐦 *STRICT <= 260 CHAR TWEET:*\n`{pkg.get('tweet', '')}`\n\n"
            f"💡 *PROMPT OF THE DAY MAGNET (WhatsApp Community):*\n```\n{pkg.get('prompt_magnet', '')}\n```\n\n"
            f"💼 *HIGH-INSIGHT LINKEDIN POST:*\n{pkg.get('linkedin', '')}"
        )
        send_tg_message(TARGET_CHAT_ID, social_msg, bot_token=TELEGRAM_BOT_TOKEN_SOCIAL)
    except Exception as e:
        print(f"[Social Bot Dispatch Error]: {e}")


LAST_DISPATCHED_TYPE = None


def check_all_radar_sources():
    """Scans all non-YouTube sources (Tech News, Reddit, HF, GitHub, X handles, News APIs) with fair multi-source interleaving."""
    global LAST_DISPATCHED_TYPE

    buckets = {
        "reddit": fetch_reddit(),
        "github": fetch_github(),
        "huggingface": fetch_huggingface(),
        "x_twitter": fetch_x_twitter(),
        "api_news": fetch_news_apis(),
        "tech_news": fetch_tech_news()
    }

    # Interleave items across sources so no single source (like The Verge / TechCrunch) starves the rest
    keys = list(buckets.keys())
    random.shuffle(keys)
    # If the last dispatched item was from a specific category, deprioritize it to ensure variety
    if LAST_DISPATCHED_TYPE in keys:
        keys.remove(LAST_DISPATCHED_TYPE)
        keys.append(LAST_DISPATCHED_TYPE)

    candidates = []
    max_len = max(len(b) for b in buckets.values()) if buckets else 0
    for i in range(max_len):
        for k in keys:
            if i < len(buckets[k]):
                candidates.append(buckets[k][i])

    for item in candidates:
        url = item.get("url") or item.get("title")
        if url in seen_topics:
            continue

        title = item.get("title", "")
        source = item.get("source", "")
        item_type = item.get("type", "news")
        seen_topics[url] = {"title": title, "source": source, "type": item_type, "date": datetime.now(timezone.utc).isoformat()}
        save_memory()

        is_worthy, reason = evaluate_news_worth(title)
        RECENT_FEED.insert(0, {
            "time": datetime.now(timezone.utc).strftime("%H:%M:%S"),
            "source": source,
            "title": title,
            "url": url,
            "status": "APPROVED" if is_worthy else "FILTERED",
            "reason": reason
        })
        if len(RECENT_FEED) > 40:
            RECENT_FEED.pop()

        if is_worthy:
            LAST_DISPATCHED_TYPE = item_type
            print(f"[RADAR HIT APPROVED]: [{source}] {title} ({reason})")
            deliver_production_package(title, f"Discovered on {source}: {url}", source_url=url, source_name=source)
            break  # Process 1 high-signal item per sweep to prevent spamming
        else:
            print(f"[RADAR HIT SUPPRESSED]: [{source}] {title} -> {reason}")


def master_radar_loop():
    print("[AI RADAR]: Master background loop active across all sources...")
    time.sleep(10)
    while True:
        try:
            check_youtube_uploads()
            check_all_radar_sources()
        except Exception as e:
            print(f"Error in master radar loop: {e}")
        time.sleep(600)  # Scan every 10 minutes


# ─── TELEGRAM ON-DEMAND LISTENER (PERSONAL DM) ───
def telegram_listener():
    offset = 0
    while True:
        try:
            url = f"{TG_API_BASE}/getUpdates?offset={offset}&timeout=20"
            res = requests.get(url, timeout=25).json()
            if "result" in res:
                for update in res["result"]:
                    offset = update["update_id"] + 1
                    msg = update.get("message") or update.get("channel_post") or {}
                    chat_id = msg.get("chat", {}).get("id")
                    text = msg.get("text", "")

                    if not text or chat_id != AUTHORIZED_CHAT_ID:
                        continue

                    if text.startswith("/start"):
                        send_tg_message(chat_id, "👋 Hello Jayant! Master Studio Engine is active 24/7. Send any AI link, topic, or command anytime!")
                        continue

                    # Allow on-demand style command: e.g., "/editorial <Topic>" or "/cyber <Topic>"
                    style = "editorial"
                    for s_key in ["editorial", "cyber", "minimal", "matrix", "tweet"]:
                        if text.lower().startswith(f"/{s_key} "):
                            style = s_key
                            text = text[len(s_key)+2:].strip()
                            break

                    print(f"[MANUAL REQUEST]: {text} (Style: {style})")
                    send_tg_message(chat_id, f"⚡ *Got it! Generating complete Studio Distribution Package & {style.upper()} Carousel... (Takes ~30s)*", bot_token=TELEGRAM_BOT_TOKEN_VIDEO)

                    pkg = generate_full_studio_package(text, text, source_url="", carousel_style=style)

                    # Video Pack (Delivered via Video Bot)
                    video_msg = (
                        f"🎬 *VIDEO PRODUCTION PACKAGE READY!*\n"
                        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
                        f"🎨 *Carousel Style:* `{style.upper()}`\n\n"
                        f"🎯 *YOUR HOOK (Google Vids Avatar):*\n_{pkg['hook']}_\n\n"
                        f"🤖 *ZORO BODY SCRIPT (ELI12):*\n{pkg['body']}\n\n"
                        f"📢 *YOUR CTA (Google Vids Avatar):*\n_{pkg['cta']}_\n\n"
                        f"🎥 *AUTOMATED B-ROLL SCENE LIST & AI PROMPTS:*\n{pkg['b_roll']}\n\n"
                        f"🎧 *ZORO's audio track is attached below!*"
                    )
                    send_tg_message(chat_id, video_msg, bot_token=TELEGRAM_BOT_TOKEN_VIDEO)
                    if os.path.exists(pkg['audio_path']):
                        send_tg_audio(chat_id, pkg['audio_path'], caption=f"🎙️ ZORO Audio ({ZORO_VOICE} • South Delhi Cadence)", bot_token=TELEGRAM_BOT_TOKEN_VIDEO)

                    # Instagram Carousel (Delivered via Carousel Bot)
                    if pkg['carousel_images']:
                        send_tg_album(chat_id, pkg['carousel_images'], caption=f"📱 *Instagram Carousel Deliverable ({style.upper()}): {text[:60]}*", bot_token=TELEGRAM_BOT_TOKEN_CAROUSEL)

                    # Social Pack (Delivered via Social Bot)
                    social_msg = (
                        f"📢 *OMNICHANNEL SOCIAL DISTRIBUTION PACK*\n"
                        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                        f"🐦 *STRICT <= 260 CHAR TWEET:*\n`{pkg['tweet']}`\n\n"
                        f"💡 *PROMPT OF THE DAY MAGNET (WhatsApp Community):*\n```\n{pkg['prompt_magnet']}\n```\n\n"
                        f"💼 *HIGH-INSIGHT LINKEDIN POST:*\n{pkg['linkedin']}"
                    )
                    send_tg_message(chat_id, social_msg, bot_token=TELEGRAM_BOT_TOKEN_SOCIAL)

                    # Hugging Face FLUX.1 visual proof card
                    img_bytes = generate_flux_image(f"Futuristic tech proof card for {text[:60]}, dark mode cyber aesthetic, 8k")
                    if img_bytes:
                        send_tg_photo(chat_id, img_bytes, caption="🖼️ Hugging Face FLUX.1 Visual Proof Card", bot_token=TELEGRAM_BOT_TOKEN_SOCIAL)

        except Exception as e:
            print(f"Error in TG listener: {e}")
            time.sleep(3)


# ─── CLOUD HTTP SERVER & MISSION CONTROL DASHBOARD ───
class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path == "/api/status":
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            payload = {
                "quotas": QuotaManager._load(),
                "recent_feed": RECENT_FEED,
                "sources_online": True,
                "bot_routing": {
                    "video_bot": "CUSTOM DEDICATED" if os.getenv("TELEGRAM_BOT_TOKEN_VIDEO") else "ROUTED VIA MASTER BOT",
                    "carousel_bot": "CUSTOM DEDICATED" if os.getenv("TELEGRAM_BOT_TOKEN_CAROUSEL") else "ROUTED VIA MASTER BOT",
                    "social_bot": "CUSTOM DEDICATED" if os.getenv("TELEGRAM_BOT_TOKEN_SOCIAL") else "ROUTED VIA MASTER BOT"
                }
            }
            self.wfile.write(json.dumps(payload).encode("utf-8"))
        elif parsed.path == "/api/trigger-radar":
            threading.Thread(target=check_all_radar_sources, daemon=True).start()
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(b'{"status": "radar_sweep_triggered"}')
        else:
            dashboard_file = os.path.join(os.path.dirname(__file__), "dashboard.html")
            if os.path.exists(dashboard_file):
                self.send_response(200)
                self.send_header("Content-type", "text/html; charset=utf-8")
                self.end_headers()
                with open(dashboard_file, "rb") as f:
                    self.wfile.write(f.read())
            else:
                self.send_response(200)
                self.send_header("Content-type", "text/plain")
                self.end_headers()
                self.wfile.write(b"Jayant AI Lab Master Studio & Radar running 24/7!")


def main():
    print("=" * 60)
    print("  JAYANT'S AI LAB — 24/7 MASTER CLOUD STUDIO & RADAR")
    print("=" * 60)

    # Start Radar thread
    t_radar = threading.Thread(target=master_radar_loop, daemon=True)
    t_radar.start()

    # Start Telegram listener thread
    t_tg = threading.Thread(target=telegram_listener, daemon=True)
    t_tg.start()

    send_tg_message(
        TARGET_CHAT_ID,
        "🚀 *Jayant's AI Lab Master Studio Connected 24/7!*\n\n"
        "✨ *Multi-Source Radar & 4-Style Carousel Upgraded:*\n"
        "• 📡 7 Tech News Feeds, 5 Reddit Subreddits, Hugging Face Hub, GitHub Trending & X Handles active.\n"
        "• 🔑 5 News & Search APIs connected with strict daily quota throttling.\n"
        "• 📱 4 Distinct Instagram Carousel Styles: Cyberpunk, Minimal Editorial, Matrix Comparison, Tweet Hero.\n"
        "• 🛑 Zero Phone Numbers: Strict scrubbing of all sensitive numbers.\n"
        "• 🎙️ ZORO male voice (.wav) with Rasalgethi South Delhi cadence.\n"
        "• ⚡ Send any topic, link, or command (e.g. `/minimal <Topic>` or `/tweet <Topic>`) for instant deliverables!"
    )

    port = int(os.getenv("PORT", "7860"))
    server = HTTPServer(("0.0.0.0", port), HealthHandler)
    server.serve_forever()


if __name__ == "__main__":
    main()
