# Jayant's AI Lab — Autonomous Blogger Publisher via Email
# Utilizes Groq 120B (1,000 RPD) to produce comprehensive, SEO-optimized 800-1200 word articles
# Automatically dispatches to Blogger secret email ("Post using email") to publish live immediately.

import os
import re
import time
import json
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()

BLOGGER_POST_EMAIL = os.getenv("BLOGGER_POST_EMAIL", "")
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", os.getenv("EMAIL_USER", "jrddiwan@gmail.com"))
SMTP_PASS = os.getenv("SMTP_PASS", os.getenv("EMAIL_PASS", ""))

BLOGGER_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "blogger_outputs"))
os.makedirs(BLOGGER_DIR, exist_ok=True)


def build_blogger_prompt(topic_title, topic_details="", source_url=""):
    return f"""You are the Principal AI Research Director & Senior Tech Columnist for Jayant's AI Lab (@jayantsailab).
Write a comprehensive, publication-grade 800 to 1,200 word deep-dive technical article for Blogger.

TOPIC: {topic_title}
DETAILS / CONTEXT: {topic_details}
SOURCE URL: {source_url}

CONSTRAINTS & VOICE:
- Direct, insightful founder voice (Jayant's AI Lab).
- No em dashes (— or --). Use commas or periods.
- Banned AI giveaways: delve, testament, beacon, tapestry, landscape, revolutionize, game-changer, unlock, navigate, elevate, harness, moreover.
- Do not mention any phone numbers.
- Format strictly as clean, modern HTML with inline CSS styling (no markdown fences). Use semantic tags: <h2>, <h3>, <p>, <ul>, <li>, <blockquote>, <pre><code>.

ARTICLE STRUCTURE (Output only the HTML body):
1. <h2>Executive Summary: The Breakthrough in Plain English</h2>
   - What dropped, why it matters, and who benefits immediately.
2. <h2>The Bottleneck: Why Manual Workflows Are Burning Payroll</h2>
   - Contrast the old slow way vs. the new autonomous system.
3. <h2>Under the Hood: Architecture & How It Actually Works</h2>
   - Real system flow, components, and simple everyday analogies.
4. <h2>Step-by-Step Implementation Blueprint</h2>
   - Concrete tutorial on how a business owner or solo creator can deploy this today.
5. <h2>Production Prompt Stack & Execution Template</h2>
   - Provide a copy-paste ready prompt or configuration inside a styled <pre><code style="background:#1e1e1e;color:#00ffaa;padding:12px;display:block;border-radius:8px;"> block.
6. <h2>Measurable Impact & ROI Benchmarks</h2>
   - Specific hours saved, speedup factors, or cost deltas.
7. <h2>The Bottom Line & Next Steps</h2>
   - Clear takeaway, invite to join Jayant's AI Lab community, save the article, and connect on Telegram & X/Twitter.

Output ONLY valid HTML content starting with <h2> and ending with the author footer block. Do not include markdown ticks (```html).
"""


def generate_blogger_article_html(topic_title, topic_details="", source_url="", call_llm_func=None):
    """
    Generates a full 800-1200 word SEO article using Groq 120B (with OpenRouter/Gemini failover).
    """
    prompt = build_blogger_prompt(topic_title, topic_details, source_url)

    if call_llm_func:
        # Utilize Groq 120B specifically for deep long-form article synthesis
        raw_html = call_llm_func(prompt, preferred="groq_120b", temperature=0.5, timeout=45)
    else:
        raw_html = None

    if not raw_html:
        clean_topic = topic_title.split(" - ")[0].split(". ")[0].strip()
        raw_html = f"""<h2>Executive Summary: {clean_topic}</h2>
<p>The pace of artificial intelligence breakthroughs continues to accelerate, but for business owners and builders, the true challenge is separating marketing buzz from operational leverage. Today we are breaking down <strong>{clean_topic}</strong>, how it works behind the scenes, and how you can integrate it into your operations right now.</p>

<h2>The Bottleneck: Why Manual Workflows Are Burning Payroll</h2>
<p>Traditional teams spend dozens of hours every week performing repetitive research, manual drafting, and manual reviews. With this new workflow, you can replace hours of friction with deterministic automated pipelines.</p>

<h2>Step-by-Step Implementation Blueprint</h2>
<ul>
  <li><strong>Step 1: Rapid Ingestion</strong> - Capture raw data, papers, or customer requests instantly.</li>
  <li><strong>Step 2: Autonomous Execution</strong> - Route tasks through specialized models to perform the heavy lifting.</li>
  <li><strong>Step 3: Human-in-the-Loop QA</strong> - Run a final quality pass before publishing or deployment.</li>
</ul>

<h2>The Bottom Line</h2>
<p>The teams that thrive this year will be the ones that engineer lean, sovereign systems. For more production-tested blueprints and daily AI intelligence, follow <strong>Jayant's AI Lab</strong>.</p>
"""

    # Clean any accidental markdown code fences
    cleaned = raw_html.strip()
    if cleaned.startswith("```html"):
        cleaned = cleaned[7:]
    elif cleaned.startswith("```"):
        cleaned = cleaned[3:]
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]
    cleaned = cleaned.strip()

    # Style wrap for Blogger
    styled_html = f"""<div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif; line-height: 1.7; color: #222; max-width: 780px; margin: 0 auto; font-size: 16px;">
{cleaned}
<hr style="border: none; border-top: 1px solid #e0e0e0; margin: 35px 0;" />
<div style="background: #f8f9fa; border-left: 4px solid #00c853; padding: 16px; border-radius: 4px; font-size: 14px; color: #444;">
  <p style="margin: 0 0 8px 0;"><strong>Published by Jayant's AI Lab</strong> — South Delhi, India</p>
  <p style="margin: 0;">Autonomous AI Engineering, Daily Tech Intelligence & Production Workflows. Connect on Telegram: <a href="https://t.me/jayantsailab" style="color: #0070f3; text-decoration: none;">@jayantsailab</a></p>
</div>
</div>"""

    return styled_html


def publish_to_blogger(title, html_content, image_paths=None, image_bytes_list=None):
    """
    Publishes an article to Blogger via its official "Post using email" gateway.
    Subject line becomes the Blog Post Title (with tags).
    Email body becomes the HTML post content.
    Attachments become post images.
    """
    ts = int(time.time())
    safe_slug = re.sub(r'[^a-zA-Z0-9_-]', '_', title[:40])
    local_file = os.path.join(BLOGGER_DIR, f"{ts}_{safe_slug}.html")

    try:
        with open(local_file, "w", encoding="utf-8") as f:
            f.write(html_content)
        print(f"[BLOGGER]: Article saved locally -> {os.path.basename(local_file)}")
    except Exception as e:
        print(f"[BLOGGER SAVE WARN]: {e}")

    load_dotenv()
    post_email = os.getenv("BLOGGER_POST_EMAIL", BLOGGER_POST_EMAIL)
    smtp_pass = os.getenv("SMTP_PASS", SMTP_PASS)
    smtp_user = os.getenv("SMTP_USER", SMTP_USER)
    smtp_host = os.getenv("SMTP_HOST", SMTP_HOST)
    smtp_port = int(os.getenv("SMTP_PORT", str(SMTP_PORT)))

    if not post_email:
        print("[BLOGGER INFO]: BLOGGER_POST_EMAIL not configured in .env. Article saved locally only.")
        return False, "BLOGGER_POST_EMAIL not set in .env"

    if not smtp_pass:
        print("[BLOGGER INFO]: SMTP_PASS (Gmail App Password) not configured in .env. Article saved locally only.")
        return False, "SMTP_PASS not set in .env"

    # Clean title for Blogger Subject
    clean_title = title.split(" - ")[0].split(". ")[0].strip()
    subject = f"[AI Tools, Automation, Jayant's AI Lab] {clean_title}"

    msg = MIMEMultipart("mixed")
    msg["Subject"] = subject
    msg["From"] = smtp_user
    msg["To"] = post_email
    msg["Date"] = datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S +0000")

    # Add HTML body
    part_html = MIMEText(html_content, "html", "utf-8")
    msg.attach(part_html)

    # Attach any images
    if image_paths:
        for idx, img_p in enumerate(image_paths):
            if img_p and os.path.exists(img_p):
                try:
                    with open(img_p, "rb") as img_f:
                        img_data = img_f.read()
                        mime_img = MIMEImage(img_data)
                        mime_img.add_header("Content-Disposition", f"attachment; filename=visual_asset_{idx+1}.png")
                        msg.attach(mime_img)
                        print(f"[BLOGGER]: Attached image -> {os.path.basename(img_p)}")
                except Exception as e:
                    print(f"[BLOGGER IMG ATTACH ERROR]: {e}")

    if image_bytes_list:
        for idx, b_data in enumerate(image_bytes_list):
            if b_data and len(b_data) > 1000:
                try:
                    mime_img = MIMEImage(b_data)
                    mime_img.add_header("Content-Disposition", f"attachment; filename=concept_card_{idx+1}.png")
                    msg.attach(mime_img)
                    print(f"[BLOGGER]: Attached concept card bytes ({len(b_data)} bytes)")
                except Exception as e:
                    print(f"[BLOGGER BYTES ATTACH ERROR]: {e}")

    # Dispatch via SMTP
    try:
        print(f"[BLOGGER]: Connecting to SMTP ({smtp_host}:{smtp_port}) as {smtp_user}...")
        server = smtplib.SMTP(smtp_host, smtp_port, timeout=30)
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(smtp_user, smtp_pass)
        server.sendmail(smtp_user, [post_email], msg.as_string())
        server.quit()
        print(f"[BLOGGER SUCCESS]: Article published live to Blogger via email -> '{clean_title}'")
        return True, "Published to Blogger successfully"
    except Exception as e:
        print(f"[BLOGGER SMTP ERROR]: Failed dispatching to {post_email}: {e}")
        return False, str(e)
