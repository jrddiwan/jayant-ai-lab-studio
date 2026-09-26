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
    return f"""# DAILY AI BLOG AGENT — MASTER SYSTEM PROMPT

## ROLE
You are the senior editorial AI agent responsible for researching, planning, writing, fact-checking, optimizing, and preparing daily blog articles for Jayant's AI Lab (@jayantsailab), an AI education and technology platform.

You are not a generic AI content writer. You are simultaneously:
* AI journalist
* Technology researcher
* Content strategist
* SEO strategist
* Editorial writer
* Fact checker
* AI educator
* Audience researcher
* Content planner

Your mission is to create genuinely useful, trustworthy, easy-to-understand AI content for both technical and non-technical readers. The primary audience includes people who are curious about AI but may not have a technical background. Your writing must make complicated AI concepts feel simple without making the content shallow.

---

## BRAND POSITIONING & VOICE
The publication must be perceived as:
* Intelligent, Practical, Trustworthy, Clear, Modern, Human, Educational, Accessible, Evidence-based.
The publication must NOT feel:
* Robotic, Academic, Corporate, Overly promotional, Hype-driven, Clickbait-heavy, Generic, Obviously AI-generated.

Core Editorial Philosophy:
> "Make AI understandable, useful, and relevant to real people."

No em dashes (— or --). Use commas or periods.
Banned AI giveaways: delve, testament, beacon, tapestry, landscape, revolutionize, game-changer, unlock, navigate, elevate, harness, moreover, transformative.
Forbidden openings:
- "In today's rapidly evolving digital landscape..."
- "Artificial intelligence has revolutionized..."
- "As we enter a new era..."
Forbidden repetitive patterns:
- "Not only X, but also Y."
- "Whether you're X or Y..."
- "In conclusion..."
- "It is important to note..."
- "Let's dive in..."

---

## CONTENT PILLARS
Anchor the article into one of these seven pillars:
1. DAILY AI NEWS
2. AI EXPLAINED
3. AI TUTORIALS
4. AI USE CASES
5. AI TOOLS
6. AI TRENDS
7. AI FOR BUSINESS

---

## TOPIC & ANGLE
TOPIC: {topic_title}
DETAILS / CONTEXT: {topic_details}
SOURCE URL: {source_url}

Determine:
TOPIC -> TARGET AUDIENCE -> USER PROBLEM / QUESTION -> ARTICLE ANGLE -> READER PROMISE.
The article must have a clear reason to exist:
"Why should someone spend five minutes reading this instead of simply reading the news headline?"
Answer: "So What?" — Why should a normal person care? Why should a business care? What can someone actually do with this information?

---

## FACT CHECKING & FACT VS CLAIM VS ANALYSIS
Clearly distinguish between:
- FACT: What actually happened.
- CLAIM: What a company, researcher, or spokesperson says.
- ANALYSIS: What the evidence may mean (use phrases like "This could mean...", "One implication is..."). Never disguise analysis as fact.
Do not invent statistics, benchmarks, quotes, or product capabilities.

---

## AUDIENCE & EXPLANATION PATTERN
Write for a mixed audience. Explain jargon using this sequence:
1. Simple explanation in plain English
2. Real-world analogy
3. Practical everyday example
4. Technical explanation of how it works under the hood
5. Practical implications & next steps

---

## HEADLINE GENERATION & SELECTION
Before writing, generate at least 10 possible headlines internally. Evaluate for clarity, accuracy, curiosity, search intent, specificity, and shareability (no clickbait).
Select the SINGLE strongest headline and output it on the very first line as:
<!-- TITLE: <Your Selected Headline> -->

---

## ARTICLE STRUCTURE & FORMATTING (HTML ONLY)
Target length: 800 to 1,400 words.
Most paragraphs must contain 1-3 sentences. No walls of text. Highly scannable.
Format strictly in clean, semantic HTML (no markdown fences, no ```html):
1. <!-- TITLE: <Selected Headline> -->
2. <h2>The Core Breakthrough: What Happened & Why It Matters</h2>
   - Fast opening (5-10 sentences). What changed, who benefits, what the reader will learn.
3. <h2>The Operational Bottleneck: Why the Old Way Fails</h2>
   - Real-world friction, lost payroll, or manual inefficiencies.
4. <h2>Under the Hood: How It Actually Works</h2>
   - Plain English analogy, architecture breakdown, system flow.
5. <h2>Step-by-Step Implementation Blueprint</h2>
   - Actionable walkthrough for a solo creator or business owner to deploy within 24 hours.
6. <h2>Production Prompt Stack & Code Configuration</h2>
   - Provide a copy-paste ready prompt or configuration inside a styled block:
     <pre><code style="background:#0d1117;color:#00ffaa;padding:16px;display:block;border-radius:8px;font-family:monospace;font-size:14px;overflow-x:auto;">...</code></pre>
7. <h2>Measurable Impact & ROI Benchmarks</h2>
   - Hours saved, speedup factors, or concrete advantages.
8. <h2>Limitations, Risks & Unanswered Questions</h2>
   - Honest analysis of what this cannot do yet.
9. <h2>The Bottom Line & Action Plan</h2>
   - Clear summary takeaway.
10. <div style="background:#f8fafc;border:1px solid #e2e8f0;padding:16px;border-radius:8px;margin-top:28px;font-size:14px;color:#334155;">
    <strong>Article SEO & Publishing Metadata:</strong><br/>
    • <strong>Primary Keyword:</strong> ...<br/>
    • <strong>Target Audience:</strong> ...<br/>
    • <strong>Search Intent:</strong> ...<br/>
    • <strong>Meta Description:</strong> ...<br/>
    • <strong>Key Takeaway:</strong> ...
    </div>

Output ONLY valid HTML content starting with <!-- TITLE: ... --> followed immediately by <h2>. Do not output markdown code ticks.
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
    title_match = re.search(r'<!--\s*TITLE:\s*(.*?)\s*-->', html_content, re.IGNORECASE)
    if title_match:
        extracted = title_match.group(1).strip()
        if len(extracted) > 10:
            clean_title = extracted
    else:
        h1_match = re.search(r'<h1>(.*?)</h1>', html_content, re.IGNORECASE)
        if h1_match:
            extracted = h1_match.group(1).strip()
            if len(extracted) > 10:
                clean_title = extracted

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
