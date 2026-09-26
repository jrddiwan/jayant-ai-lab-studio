# JAYANT'S AI LAB — MASTER PRODUCTION SPECIFICATION & CODING AGENT RULEBOOK

> **Document Version**: 3.1 (Strict 30-Second School-Kid Zoro Script & Agnes AI Fleet)  
> **Brand**: Jayant's AI Lab (`@jayantsailab`)  
> **Location**: South Delhi, India  
> **Founder Identity**: Jayant — Independent AI engineer, agency founder, and operator. Speaks with contrarian conviction, energetic creator clarity, and zero corporate PR fluff.  
> **AI Employee**: ZORO — Jayant's autonomous AI employee (Voice: `Rasalgethi`, male urban Indian English / South Delhi cadence, strictly $\le 30$ seconds audio).

---

## 1. SCRIPTWRITING SPECIFICATION (VIDEO PRODUCTION PACK)

### A. The Avatar Hook (Google Vids Avatar / Jayant)
* **Target Speaker**: Jayant (Founder Avatar)
* **Structure**: **EXACTLY 3 POWERFUL LINES**:
  - **Line 1 (Pattern Interrupt / Contrarian Premise)**: A punchy, scroll-stopping premise from Jayant's builder perspective.
  - **Line 2 (Concrete Reality / Metric / Proof)**: High-conviction reality or quantifiable speed/cost benchmark.
  - **Line 3 (Clean Signature Handover)**: Introduces Zoro smoothly and cleanly.
* **MANDATORY SIGNATURE HANDOVER**:
  - The hook **MUST ALWAYS END** with Line 3 handing over to Zoro.
  - **STRICT RULE**: Mention Zoro **EXACTLY ONCE** in the entire hook (strictly in Line 3).
  - **BANNED PHRASES**: Never say clunky clichés like *"Pass it to Zoro for the mechanics"* or duplicate Zoro's name.
  - *Format*: `"Now my AI employee Zoro will show you how."` or `"Now my AI employee Zoro will break down the real workflow."`

---

### B. ZORO Body Script (Strict 30-Second School-Kid Monologue)
* **Target Speaker**: ZORO (Jayant's AI employee)
* **HARD DURATION LIMIT**: **STRICTLY UNDER 30 SECONDS OF SPOKEN AUDIO** ($\le 30.0$ seconds).
  - Standard English speaking pace is 2.3 words/second.
  - **Strict Word Count**: **STRICTLY 60 TO 75 WORDS TOTAL**. Any script over 75 words will exceed 30 seconds and is strictly rejected by the Quality Gate!
* **TEACH LIKE TO A 12-YEAR-OLD SCHOOL KID**:
  - Explain the tool so simply that a school kid instantly gets it.
  - Use physical, relatable analogies:
    - *Example*: Having 50 pages of boring homework to read, and an invisible robot buddy reads the entire book in 5 seconds and gives you the exact answers.
    - *Example*: A secret video game cheat code that cleans your room automatically.
* **HOW TO SOUND TECHNICAL WITHOUT JARGON**:
  - Explain the substance of what the technology actually does in plain English.
  - **FORBIDDEN JARGON**: Zero techno-babble. Banned words: *token velocity, deterministic routing, VRAM footprint, latency in ms, sub-agent moats, API moats, inference latency, vector embeddings, gradient descent, quantization*.
* **DYNAMIC ZORO INTRO (VARIED EVERY TIME)**:
  - Zoro must always introduce himself as Jayant's AI employee, but with fresh opening lines every time (never the same static sentence):
    1. `"Hey, I am Zoro, Jayant's AI employee at the Lab..."`
    2. `"Zoro here, Jayant's AI employee in South Delhi..."`
    3. `"Zoro here, Jayant's AI employee, and today I have got something wild for you..."`
    4. `"I am Zoro, Jayant's AI employee. Let me show you what happened behind the scenes..."`
    5. `"Zoro here, Jayant's AI employee at the Lab. Let's break down the real numbers..."`
    6. `"This is Zoro, Jayant's AI employee. If you want to save hours of manual grind, listen closely..."`
    7. `"Zoro on deck, Jayant's AI employee. Here is the blueprint you need..."`
    8. `"I am Zoro, Jayant's AI employee. Let's cut through the hype and look at the real workflow..."`
    9. `"Zoro here from Jayant's AI Lab, and I am going to show you how to automate this today..."`
* **3-PART 30-SECOND STRUCTURE (60–75 words)**:
  1. **Dynamic Intro & School-Kid Pain**: The boring grind or chore everyone hates.
  2. **Invisible Robot Buddy Solution**: How the AI handles the entire task in seconds.
  3. **Punchy WhatsApp Benchmark**: *"If you can send a message on WhatsApp, you already have the skills to use this today."*

---

### C. The Avatar Call to Action (CTA)
* **Target Speaker**: Jayant (Founder Avatar)
* **Structure**: **EXACTLY 2 POWERFUL LINES**:
  - **Line 1 (Tactical Action & Retention)**: Ask for a specific high-value action (e.g., *"Save this breakdown for your next build sprint and drop your biggest automation bottleneck in the comments below."*).
  - **Line 2 (Authority & Community Retention)**: *"Follow @jayantsailab for battle-tested autonomous AI blueprints you can deploy today."*
* **Rule**: Direct to comments or save post. **ABSOLUTE BAN ON "IN BIO"** (there is nothing in the bio).

---

### D. Zoro Voice Track & Audio Synthesis Specification
* **Target Speaker**: Zoro (Jayant's AI employee)
* **Accent & Cadence**: Urban Indian English (South Delhi tech founder cadence).

#### 100% SCRIPT-AUDIO SYNCHRONIZATION GUARANTEE:
* **Audio Synthesis Timing**: Audio synthesis is executed **ONLY AFTER** the Chief Quality Monitor has audited, elevated, and approved the final script.
* **Zero Discrepancy**: The `.wav` audio track generated and attached on Telegram matches the exact text of `pkg["body"]` written in the Telegram message word-for-word.

#### Tier 1: Google Gemini Flash TTS (Primary)
* **Model**: `gemini-2.5-flash-preview-tts` (or `gemini-3.1-flash-tts-preview`)
* **Voice Configuration**: `voice_name="Rasalgethi"`
* **Official AI Studio Directors Notes Syntax (MANDATORY)**:
  ```markdown
  ### DIRECTORS NOTES
  Voice: Rasalgethi
  Accent: Indian English accent as heard in South Delhi, India
  Pacing: Fast, energetic, confident tech founder cadence
  Emotion: Clear, enthusiastic

  ### TRANSCRIPT
  [enthusiastic] {transcript}
  ```
* **Dual Key Failover**: `GEMINI_API_KEY` $\rightarrow$ `GEMINI_API_KEY_2`.

#### Tier 2: Fish Audio TTS (Failover Backup)
* Used automatically if both Gemini API keys are exhausted or rate-limited.
* **Endpoint**: `https://api.fish.audio/v1/tts`
* **CRITICAL Header**: `model: s2.1-pro-free` (Must be sent in HTTP headers or API returns `402 Insufficient Credit`).
* **API Key**: `sk-fish-BeTKz_YUTsBXtwd-LUHDl9M_1Yh3w32btZEa-716cJ4`
* **Voice Reference ID**: `fb7ec16ca51a45a5a4db881244d7990a`

#### Banned Technologies:
* `edge-tts` is **PERMANENTLY REMOVED AND BANNED**. Do not install, import, or fallback to edge-tts.

---

## 2. 7-SLIDE INSTAGRAM CAROUSEL SPECIFICATION

Modeled after top tech creator aesthetics (`@theautomationguy.ai`, Rowan Cheung, Ruben Hassid):
* **Dimensions**: 1080 x 1350 px (4:5 portrait aspect ratio).
* **Background Theme**: Warm editorial cream (`#F4EFE6`), deep obsidian typography (`#111111`), signal orange highlights (`#E04F16`), kraft paper sticky notes with real handwriting font (`Caveat`).

### Slide Architecture (7 Slides Total):
1. **Slide 1: Hero Hook & Showcase**
   - Category pill (e.g. `● OPEN SOURCE • GITHUB`).
   - Split headline: `titlePrefix` + `titleOrange` + `titleSuffix`.
   - Dynamic 3D clay character generated via **Agnes AI** (`agnes-image-2.0-flash`) or **Hugging Face FLUX.1** + **Official Tool Logo** (if a brand like OpenAI, Claude, Meta, Google, etc., is mentioned).
   - Kraft sticky note with founder handwriting angle.
2. **Slide 2: System Architecture & Org Chart**
   - Leader orchestrator card (`ZORO - Chief AI Orchestrator`).
   - Connecting flowchart branches to 4 functional departments.
3. **Slide 3: Specialist Fleet (The First Six Hires — Agnes AI Clay Avatar Fleet)**
   - 6 structured cards with titles, tags, and 1-sentence actionable descriptions.
   - **AGNES AI 3D CLAY AVATAR FLEET**:
     - Uses 12 distinct 3D clay characters generated via Agnes AI (`agnes-image-2.0-flash`) saved in `assets/avatars/`:
       - `avatar_01_dev.png`, `avatar_02_robot.png`, `avatar_03_analyst.png`, `avatar_04_coder.png`, `avatar_05_detective.png`, `avatar_06_builder.png`, `avatar_07_creative.png`, `avatar_08_executive.png`, `avatar_09_ninja.png`, `avatar_10_astronaut.png`, `avatar_11_scientist.png`, `avatar_12_growth.png`.
     - 6 distinct avatars are dynamically selected and bound to the 6 cards (zero repetition across cards).
     - **Card 1 Official Tool Logo Badge**: A floating circular 42x42px brand badge on Card 1 displaying the official SVG logo of the featured tool/model (OpenAI, Claude, Rabbit, HuggingFace, etc.).
   - **MOBILE-FIRST LARGE TYPOGRAPHY**:
     - `.spec-title`: **24px bold** (`#111111`) — crystal clear on smartphone feeds.
     - `.spec-desc`: **16.5px bold** (`#2D2A24`, line-height 1.35) — easily readable without zooming.
     - `.spec-tag`: **11px orange monospace** (`#E04F16`).
     - Image card height: **175px** with smooth gradient backing.
4. **Slide 4: Practical Execution Prompts**
   - 4 real-world execution prompts with bulleted task checklists.
5. **Slide 5: The Cold Numbers (ROI Benchmark)**
   - Side-by-side comparison: *The Old Manual Way (e.g. 4 Days, $3,500/mo)* vs *Jayant's AI Lab Way (e.g. 35 Sec, $0 marginal cost)*.
   - Bottom telemetry ROI bar (`99.4% TIME SAVED`).
6. **Slide 6: Production Business Use Cases**
   - 4 real day-to-day enterprise/builder deployment workflows.
7. **Slide 7: The Transformation & CTA**
   - Bold headline (`Same Team. A More Capable You.`), big save button (`Save This Carousel & Follow @jayantsailab 🔖`), and 3 credibility pills.

---

## 3. LINKEDIN FOUNDER POSTS (CLAUDE LINKEDIN SKILL SPECIFICATION)

Powered by Serge Bulaev's **12 Claude Code & Codex LinkedIn Skills**:
* **Perspective**: Founder Mode (Trust with everyday operators and business owners > lazy reach).
* **Length Sweet Spot**: Exactly 900 to 1,300 characters (160 to 240 words).
* **Tone**: Clear, accessible, non-technical founder storytelling.
* **Structural Post Formula**:
  - **Line 1 (Hook)**: Under 120 characters to fit above the "see more" fold.
  - **The Relatable Problem**: Why manual work is burning payroll and exhausting teams.
  - **The 3-Step Simple System**:
    1. *Cut Research Time*: Turn hours of reading into 3 clear action points.
    2. *Automate Daily Tasks*: Draft emails and routine summaries in 15 seconds.
    3. *Eliminate Busywork*: Free up 10+ hours every week to focus on growing the business.
  - **The WhatsApp Benchmark**: If you can use WhatsApp, you have the skills to run this today.
  - **Closing CTA**: Save this post 🔖 and drop a comment below with your thoughts.
* **CRITICAL RULES**:
  - **ZERO raw URLs in post body**.
  - **ZERO 'in bio' references**.

---

## 4. OMNICHANNEL SOCIAL PACK (TWITTER/X)

### A. Strict $\le$250 Character Tweet
* **Length**: Max 250 characters (fits comfortably in Twitter/X free limit).
* **Tone**: Jayant's personal builder perspective. **NEVER SOUND LIKE CORPORATE PR** (*"We are thrilled to announce..."* is strictly banned).
* **ABSOLUTE BAN ON 'IN BIO'**: Never write "in bio", "link in bio", or "check bio" (there is nothing in the bio).
* **Structure**:
  - Line 1: Pain point / time sink callout.
  - Line 2: The 20-second automated solution.
  - Line 3: Zero coding required. Work smarter, not harder.

### B. Prompt of the Day Magnet
* **PERMANENTLY REMOVED**: No prompt of the day is generated or dispatched to Telegram.

---

## 5. CHIEF CONTENT QUALITY MONITOR AGENT (9.9/10 QUALITY GATE)

Every piece of content must pass the autonomous **Quality Gate** before reaching Telegram:
1. **Avatar Hook Handover Check**: Must verify handover to Zoro. Auto-appends if missing.
2. **Zoro Intro Check**: Must verify `"I am Zoro, Jayant's AI employee at the Lab"`. Auto-prepends if missing.
3. **Zoro Script ELI12 Check**: Must verify word count $\ge 115$ words and ZERO forbidden techno-jargon terms. Auto-elevates to 9.9/10 ELI12 creator style if non-compliant.
4. **Tweet Compliance Check**: $\le 250$ characters, builder perspective, zero PR fluff, ZERO 'in bio'.
5. **LinkedIn Post Check**: 900-1300 chars, 3-step actionable breakdown, zero raw links, ZERO 'in bio'.
6. **Humanizer & Safety Check**:
   - Strictly 0 em dashes (`—` / `--`).
   - Strictly 0 AI buzzwords (*delve, testament, beacon, tapestry, landscape, revolutionize, game-changer, unlock, navigate, elevate, harness, moreover, furthermore*).
   - Strictly 0 phone numbers.
   - Strictly 0 'in bio' / 'link in bio' references.
7. **Final Audio Generation & Verification**:
   - Zoro audio is synthesized ONCE on the final approved text.
   - Guarantees 100% word-for-word parity between Telegram script text and audio track.
* **Quality Gate Header**: `🛡️ QUALITY AUDIT: 9.9/10 [CHIEF QUALITY GATE PASSED]`.

---

## 6. TELEGRAM BOT ROUTING
Deliver strictly to Jayant's personal chat ID (`7007116692`):
- **Bot 1: Video Studio Bot** (`TELEGRAM_BOT_TOKEN_VIDEO`) $\rightarrow$ Video Script + Kling/Luma B-Roll Prompts + Zoro Audio Track.
- **Bot 2: Carousel Studio Bot** (`TELEGRAM_BOT_TOKEN_CAROUSEL`) $\rightarrow$ 7-Slide Editorial Instagram Album (with dynamic 3D clay characters & tool logos).
- **Bot 3: Social & News Bot** (`TELEGRAM_BOT_TOKEN_SOCIAL`) $\rightarrow$ Strict $\le 250$ Char Tweet (No Bio) + High-Insight LinkedIn Founder Post.
