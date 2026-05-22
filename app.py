"""
Resume Analyzer — Appraa Tech
ATS scoring · Job Description Matching · Bullet Point Rewriter
Powered by GPT-4o-mini
"""

import os
import io
import json
import math
import streamlit as st

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Resume Analyzer | Appraa Tech",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:ital,wght@0,300;0,400;0,500;0,600;0,700;0,800;1,400&display=swap');

*, html, body, [class*="css"] {
    font-family: 'Inter', sans-serif !important;
    box-sizing: border-box;
}

/* Hide Streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 1.5rem !important; padding-bottom: 3rem !important; }

/* ── Background ── */
.stApp { background: #f0f2f8; }

/* ── Top nav bar ── */
.top-nav {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0.75rem 1.5rem;
    background: #ffffff;
    border-bottom: 1px solid #e2e8f0;
    border-radius: 12px;
    margin-bottom: 1.5rem;
    box-shadow: 0 1px 4px rgba(0,0,0,0.05);
}
.top-nav-brand {
    display: flex;
    align-items: center;
    gap: 10px;
    font-weight: 700;
    font-size: 1.1rem;
    color: #0f172a;
    letter-spacing: -0.3px;
}
.top-nav-brand span {
    background: linear-gradient(135deg, #6366f1, #8b5cf6);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}
.nav-badge {
    background: #f0fdf4;
    color: #16a34a;
    border: 1px solid #bbf7d0;
    border-radius: 20px;
    font-size: 0.72rem;
    font-weight: 600;
    padding: 3px 10px;
    letter-spacing: 0.3px;
}
.nav-badge-warn {
    background: #fffbeb;
    color: #b45309;
    border: 1px solid #fde68a;
    border-radius: 20px;
    font-size: 0.72rem;
    font-weight: 600;
    padding: 3px 10px;
    letter-spacing: 0.3px;
}

/* ── Hero ── */
.hero-section {
    background: linear-gradient(135deg, #1e1b4b 0%, #312e81 40%, #4338ca 80%, #6366f1 100%);
    border-radius: 16px;
    padding: 3rem 2.5rem 2.5rem 2.5rem;
    color: white;
    margin-bottom: 2rem;
    position: relative;
    overflow: hidden;
}
.hero-section::before {
    content: '';
    position: absolute;
    top: -50%;
    right: -10%;
    width: 400px;
    height: 400px;
    background: radial-gradient(circle, rgba(139,92,246,0.3) 0%, transparent 70%);
    border-radius: 50%;
}
.hero-section::after {
    content: '';
    position: absolute;
    bottom: -30%;
    left: 10%;
    width: 300px;
    height: 300px;
    background: radial-gradient(circle, rgba(99,102,241,0.2) 0%, transparent 70%);
    border-radius: 50%;
}
.hero-eyebrow {
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    opacity: 0.65;
    margin-bottom: 0.75rem;
}
.hero-title {
    font-size: 2.4rem;
    font-weight: 800;
    line-height: 1.15;
    letter-spacing: -1px;
    margin: 0 0 0.75rem 0;
}
.hero-subtitle {
    font-size: 1.05rem;
    opacity: 0.78;
    font-weight: 400;
    max-width: 560px;
    line-height: 1.6;
    margin: 0 0 1.75rem 0;
}
.hero-pills {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
}
.hero-pill {
    background: rgba(255,255,255,0.12);
    border: 1px solid rgba(255,255,255,0.2);
    border-radius: 20px;
    padding: 5px 14px;
    font-size: 0.82rem;
    font-weight: 500;
    backdrop-filter: blur(4px);
}

/* ── Cards ── */
.card {
    background: #ffffff;
    border-radius: 14px;
    border: 1px solid #e2e8f0;
    box-shadow: 0 2px 12px rgba(0,0,0,0.05);
    padding: 1.5rem;
    margin-bottom: 1.25rem;
}
.card-header {
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 1px;
    text-transform: uppercase;
    color: #94a3b8;
    margin-bottom: 0.75rem;
    display: flex;
    align-items: center;
    gap: 6px;
}
.card-title {
    font-size: 1.1rem;
    font-weight: 700;
    color: #0f172a;
    margin-bottom: 0.4rem;
}

/* ── Score gauge ── */
.gauge-wrap {
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 1.5rem 0 0.5rem 0;
}
.gauge-context {
    font-size: 0.85rem;
    color: #64748b;
    text-align: center;
    margin-top: 0.5rem;
}
.gauge-rating {
    font-size: 1rem;
    font-weight: 700;
    text-align: center;
    margin-top: 0.25rem;
}

/* ── Score breakdown bars ── */
.breakdown-row {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 0.75rem;
}
.breakdown-label {
    font-size: 0.82rem;
    color: #475569;
    font-weight: 500;
    width: 140px;
    flex-shrink: 0;
}
.breakdown-bar-bg {
    flex: 1;
    height: 8px;
    background: #f1f5f9;
    border-radius: 4px;
    overflow: hidden;
}
.breakdown-bar-fill {
    height: 100%;
    border-radius: 4px;
    transition: width 0.6s ease;
}
.breakdown-score {
    font-size: 0.82rem;
    font-weight: 600;
    color: #0f172a;
    width: 32px;
    text-align: right;
    flex-shrink: 0;
}

/* ── One-liner profile ── */
.profile-card {
    background: linear-gradient(135deg, #f5f3ff, #ede9fe);
    border: 1px solid #ddd6fe;
    border-radius: 12px;
    padding: 1.25rem 1.5rem;
    margin: 0.75rem 0 1.25rem 0;
}
.profile-card p {
    font-size: 1rem;
    color: #3730a3;
    font-style: italic;
    font-weight: 500;
    margin: 0;
    line-height: 1.65;
}

/* ── Result items ── */
.result-item {
    display: flex;
    align-items: flex-start;
    gap: 10px;
    padding: 0.65rem 0;
    border-bottom: 1px solid #f1f5f9;
    font-size: 0.9rem;
    color: #374151;
    line-height: 1.5;
}
.result-item:last-child { border-bottom: none; }
.result-icon { flex-shrink: 0; margin-top: 1px; }

/* ── Keywords ── */
.kw-grid { display: flex; flex-wrap: wrap; gap: 8px; margin-top: 0.5rem; }
.kw-found {
    display: inline-flex; align-items: center; gap: 5px;
    background: #f0fdf4; color: #15803d; border: 1px solid #bbf7d0;
    border-radius: 20px; padding: 4px 12px; font-size: 0.8rem; font-weight: 500;
}
.kw-missing {
    display: inline-flex; align-items: center; gap: 5px;
    background: #fef2f2; color: #b91c1c; border: 1px solid #fecaca;
    border-radius: 20px; padding: 4px 12px; font-size: 0.8rem; font-weight: 500;
}
.kw-jd {
    display: inline-flex; align-items: center; gap: 5px;
    background: #eff6ff; color: #1d4ed8; border: 1px solid #bfdbfe;
    border-radius: 20px; padding: 4px 12px; font-size: 0.8rem; font-weight: 500;
}

/* ── Match score ring ── */
.match-score-wrap {
    text-align: center;
    padding: 1.5rem;
}
.match-score-num {
    font-size: 3.5rem;
    font-weight: 800;
    line-height: 1;
}
.match-score-label {
    font-size: 0.85rem;
    color: #64748b;
    margin-top: 0.3rem;
}

/* ── Bullet rewriter ── */
.bullet-before {
    background: #fef2f2;
    border: 1px solid #fecaca;
    border-radius: 8px;
    padding: 0.85rem 1rem;
    font-size: 0.88rem;
    color: #7f1d1d;
    margin-bottom: 6px;
    font-style: italic;
}
.bullet-after {
    background: #f0fdf4;
    border: 1px solid #bbf7d0;
    border-radius: 8px;
    padding: 0.85rem 1rem;
    font-size: 0.88rem;
    color: #14532d;
    font-weight: 500;
    margin-bottom: 1.25rem;
}
.bullet-arrow {
    text-align: center;
    font-size: 1.2rem;
    margin: 4px 0;
    color: #6366f1;
}

/* ── Tip box ── */
.tip-box {
    background: #fefce8;
    border: 1px solid #fde68a;
    border-radius: 10px;
    padding: 1rem 1.25rem;
    font-size: 0.88rem;
    color: #78350f;
    margin: 0.75rem 0;
}
.tip-box strong { color: #92400e; }

/* ── Download button area ── */
.download-area {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 10px;
    padding: 1rem 1.5rem;
    margin-top: 1rem;
    font-size: 0.85rem;
    color: #64748b;
}

/* ── Footer ── */
.page-footer {
    text-align: center;
    padding: 2.5rem 0 1rem 0;
    font-size: 0.78rem;
    color: #94a3b8;
}
.page-footer a { color: #6366f1; text-decoration: none; }
.page-footer a:hover { text-decoration: underline; }

/* ── Streamlit tab styling ── */
div[data-baseweb="tab-list"] {
    background: transparent !important;
    gap: 4px !important;
    border-bottom: 2px solid #e2e8f0 !important;
    padding-bottom: 0 !important;
}
div[data-baseweb="tab"] {
    background: transparent !important;
    border-radius: 8px 8px 0 0 !important;
    font-weight: 500 !important;
    font-size: 0.9rem !important;
    color: #64748b !important;
    padding: 0.6rem 1.2rem !important;
}
div[data-baseweb="tab"][aria-selected="true"] {
    color: #6366f1 !important;
    border-bottom: 2px solid #6366f1 !important;
}
div[data-baseweb="tab-panel"] { padding-top: 1.5rem !important; }

/* ── Override Streamlit primary button ── */
div.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #6366f1, #4f46e5) !important;
    border: none !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    padding: 0.65rem 2rem !important;
    box-shadow: 0 4px 14px rgba(99,102,241,0.35) !important;
    transition: all 0.2s !important;
}
div.stButton > button[kind="primary"]:hover {
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 20px rgba(99,102,241,0.45) !important;
}
div.stButton > button[kind="secondary"] {
    border-radius: 10px !important;
    font-weight: 500 !important;
    border: 1px solid #e2e8f0 !important;
    background: white !important;
    color: #374151 !important;
}

/* File uploader */
div[data-testid="stFileUploadDropzone"] {
    border: 2px dashed #c7d2fe !important;
    border-radius: 12px !important;
    background: #fafaff !important;
}
</style>
""", unsafe_allow_html=True)


# ── Helpers ───────────────────────────────────────────────────────────────────

def extract_text_from_pdf(file_bytes: bytes) -> str:
    text = ""
    try:
        import pdfplumber
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            for page in pdf.pages:
                pt = page.extract_text()
                if pt:
                    text += pt + "\n"
        if text.strip():
            return text
    except Exception:
        pass
    try:
        import PyPDF2
        reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
        for page in reader.pages:
            text += (page.extract_text() or "") + "\n"
        return text
    except Exception as e:
        raise ValueError(f"Could not extract text from PDF: {e}")


def extract_text_from_docx(file_bytes: bytes) -> str:
    try:
        from docx import Document
        doc = Document(io.BytesIO(file_bytes))
        return "\n".join(p.text for p in doc.paragraphs if p.text.strip())
    except Exception as e:
        raise ValueError(f"Could not extract text from DOCX: {e}")


def get_api_key() -> str | None:
    try:
        return st.secrets["OPENAI_API_KEY"]
    except Exception:
        pass
    return os.environ.get("OPENAI_API_KEY")


def score_color(score: int) -> str:
    if score >= 85:
        return "#10b981"
    elif score >= 70:
        return "#6366f1"
    elif score >= 55:
        return "#f59e0b"
    else:
        return "#ef4444"


def score_rating(score: int) -> tuple[str, str]:
    """Returns (label, color)"""
    if score >= 85:
        return "Excellent", "#10b981"
    elif score >= 70:
        return "Good", "#6366f1"
    elif score >= 55:
        return "Fair", "#f59e0b"
    else:
        return "Needs Work", "#ef4444"


def render_gauge(score: int, size: int = 180):
    """Render an SVG circular gauge for the score."""
    radius = 70
    cx, cy = size // 2, size // 2
    circ = 2 * math.pi * radius
    fill = (score / 100) * circ
    gap = circ - fill
    color = score_color(score)
    rating, _ = score_rating(score)

    return f"""
    <div class="gauge-wrap">
      <svg width="{size}" height="{size}" viewBox="0 0 {size} {size}">
        <!-- Track -->
        <circle cx="{cx}" cy="{cy}" r="{radius}" fill="none"
          stroke="#e2e8f0" stroke-width="14"/>
        <!-- Fill -->
        <circle cx="{cx}" cy="{cy}" r="{radius}" fill="none"
          stroke="{color}" stroke-width="14"
          stroke-dasharray="{fill:.2f} {gap:.2f}"
          stroke-linecap="round"
          transform="rotate(-90 {cx} {cy})"/>
        <!-- Score number -->
        <text x="{cx}" y="{cy - 8}" text-anchor="middle"
          font-family="Inter,sans-serif" font-size="38" font-weight="800"
          fill="#0f172a">{score}</text>
        <!-- Label -->
        <text x="{cx}" y="{cy + 16}" text-anchor="middle"
          font-family="Inter,sans-serif" font-size="11" fill="#94a3b8"
          font-weight="500" letter-spacing="0.5">ATS SCORE</text>
      </svg>
      <div class="gauge-rating" style="color:{color}">{rating}</div>
      <div class="gauge-context">out of 100 &nbsp;·&nbsp; {score_context(score)}</div>
    </div>
    """


def score_context(score: int) -> str:
    if score >= 85:
        return "Top 15% of resumes"
    elif score >= 70:
        return "Above average"
    elif score >= 55:
        return "Room to improve"
    else:
        return "Significant gaps found"


def render_breakdown(breakdown: dict):
    """Render score breakdown bars."""
    labels = {
        "achievements": ("Quantified Results", 25),
        "keywords": ("Tech Keywords", 25),
        "structure": ("Resume Structure", 20),
        "language": ("Language & Verbs", 15),
        "completeness": ("Completeness", 15),
    }
    html = '<div style="margin-top:0.5rem">'
    for key, (label, max_pts) in labels.items():
        val = breakdown.get(key, 0)
        pct = min(100, round(val / max_pts * 100))
        color = score_color(round(val / max_pts * 100))
        html += f"""
        <div class="breakdown-row">
          <div class="breakdown-label">{label}</div>
          <div class="breakdown-bar-bg">
            <div class="breakdown-bar-fill" style="width:{pct}%;background:{color}"></div>
          </div>
          <div class="breakdown-score">{val}/{max_pts}</div>
        </div>"""
    html += "</div>"
    return html


# ── LLM calls ────────────────────────────────────────────────────────────────

ANALYSIS_PROMPT = """You are an expert ATS resume analyst. Analyze the resume below and return ONLY a valid JSON object.

Required JSON structure:
{{
  "ats_score": <integer 0-100>,
  "score_breakdown": {{
    "achievements": <0-25, points for quantified metrics and results>,
    "keywords": <0-25, points for relevant tech/industry keywords>,
    "structure": <0-20, points for clear sections, formatting signals>,
    "language": <0-15, points for action verbs and clarity>,
    "completeness": <0-15, points for contact info, skills, education>
  }},
  "one_liner": "<Single punchy sentence summarizing the candidate>",
  "strengths": ["<strength 1>", "<strength 2>", "<strength 3>", "<strength 4>"],
  "missing_keywords": ["<keyword 1>", "<keyword 2>", ...],
  "improvements": ["<specific actionable tip 1>", "<specific actionable tip 2>", ...],
  "suggested_titles": ["<Job Title 1>", "<Job Title 2>", "<Job Title 3>"]
}}

Rules:
- ats_score must equal the sum of score_breakdown values
- missing_keywords: 6-10 keywords absent from the resume that appear in most tech/relevant job descriptions
- improvements: 5-7 specific, actionable tips referencing actual resume content
- strengths: 3-5 genuine strengths based only on what exists in the resume
- suggested_titles: 3 job titles this resume is best suited for

Resume:
---
{resume_text}
---

Return only the JSON object, no markdown, no extra text."""


JD_MATCH_PROMPT = """You are an expert ATS specialist. Compare the resume against the job description and return ONLY a valid JSON object.

JSON structure:
{{
  "match_score": <integer 0-100>,
  "matched_keywords": ["<keyword found in both>", ...],
  "missing_keywords": ["<keyword in JD but not resume>", ...],
  "recommendation": "<2-sentence overall assessment>",
  "tailoring_tips": ["<specific tip 1>", "<specific tip 2>", "<specific tip 3>", "<specific tip 4>"]
}}

Rules:
- match_score: how well the resume matches this specific JD (not general ATS)
- matched_keywords: skills/tools/concepts that appear in both (list 5-10)
- missing_keywords: important JD requirements missing from resume (list 5-10)
- tailoring_tips: specific changes to make this resume better for this JD

Resume:
---
{resume_text}
---

Job Description:
---
{jd_text}
---

Return only the JSON object."""


BULLET_REWRITE_PROMPT = """You are an expert resume writer. Rewrite each bullet point to be stronger:
- Start with a powerful action verb (Led, Engineered, Delivered, Architected, Reduced, Increased, etc.)
- Add specific metrics where plausible (%, $, time saved, team size)
- Make it concise and impactful (1-2 lines max)
- Follow STAR-lite format: Action + What + Impact

Return ONLY a valid JSON object:
{{
  "rewrites": [
    {{"original": "<original bullet>", "rewritten": "<improved bullet>"}},
    ...
  ]
}}

Bullets to rewrite:
---
{bullets}
---

Return only the JSON object."""


def call_openai(prompt: str, api_key: str) -> dict:
    """Generic OpenAI GPT-4o-mini call returning parsed JSON."""
    from openai import OpenAI
    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        max_tokens=1500,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": "You are an expert career analyst. Always respond with valid JSON only."},
            {"role": "user", "content": prompt},
        ]
    )
    raw = response.choices[0].message.content.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    return json.loads(raw.strip())


def demo_analysis() -> dict:
    return {
        "ats_score": 72,
        "score_breakdown": {
            "achievements": 15,
            "keywords": 18,
            "structure": 15,
            "language": 12,
            "completeness": 12,
        },
        "one_liner": "Full-stack engineer with 5+ years building scalable web applications, blending strong Python/React expertise with a product-minded approach to shipping user-centric features.",
        "strengths": [
            "Clear end-to-end project ownership across multiple roles",
            "Strong backend skills with Python, Django, and REST API design",
            "Evidence of cross-functional collaboration and Agile experience",
            "Progressive career growth with increasing scope",
        ],
        "missing_keywords": [
            "CI/CD", "Docker", "Kubernetes", "AWS / cloud platform",
            "GraphQL", "TypeScript", "unit testing", "microservices",
        ],
        "improvements": [
            "Quantify every bullet — replace 'improved performance' with 'reduced load time by 40%'.",
            "Add a grouped Skills section: Languages · Frameworks · Cloud · Tools.",
            "Include a 2-3 line professional summary optimized for ATS keyword scanning.",
            "Mention cloud platforms (AWS/GCP/Azure) — they appear in 80%+ of tech JDs.",
            "Replace weak verbs ('worked on', 'helped with') with 'architected', 'led', 'delivered'.",
            "Add GitHub URL and LinkedIn to the contact header.",
        ],
        "suggested_titles": ["Software Engineer", "Backend Developer", "Full Stack Engineer"],
    }


# ── UI Components ─────────────────────────────────────────────────────────────

def render_nav(api_key):
    status_html = (
        '<span class="nav-badge">🟢 API Connected</span>'
        if api_key else
        '<span class="nav-badge-warn">⚠️ Demo Mode</span>'
    )
    st.markdown(f"""
    <div class="top-nav">
      <div class="top-nav-brand">
        📄 &nbsp;<span>Appraa Tech</span> &nbsp;Resume Analyzer
      </div>
      <div style="display:flex;align-items:center;gap:12px">
        {status_html}
        <a href="https://appraatech.com" target="_blank"
           style="font-size:0.8rem;color:#6366f1;text-decoration:none;font-weight:500">
          appraatech.com ↗
        </a>
      </div>
    </div>
    """, unsafe_allow_html=True)


def render_hero():
    st.markdown("""
    <div class="hero-section">
      <div class="hero-eyebrow">AI-Powered Career Tools</div>
      <h1 class="hero-title">Land more interviews.<br>Beat the ATS.</h1>
      <p class="hero-subtitle">
        Upload your resume to get an instant ATS compatibility score, keyword gap analysis,
        job description matching, and AI-powered bullet rewrites — all in seconds.
      </p>
      <div class="hero-pills">
        <span class="hero-pill">📊 ATS Score</span>
        <span class="hero-pill">🎯 Job Match</span>
        <span class="hero-pill">✍️ Bullet Rewriter</span>
        <span class="hero-pill">🔍 Keyword Analysis</span>
        <span class="hero-pill">⚡ GPT-4o-mini</span>
      </div>
    </div>
    """, unsafe_allow_html=True)


def render_analysis_tab(api_key):
    """Tab 1: Resume Analysis"""

    col_upload, col_tip = st.columns([3, 2])

    with col_upload:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-header">📎 UPLOAD RESUME</div>', unsafe_allow_html=True)
        uploaded_file = st.file_uploader(
            "Drag & drop your resume here",
            type=["pdf", "docx"],
            help="Supports PDF and DOCX — max 10 MB",
            key="resume_uploader",
        )
        st.markdown('</div>', unsafe_allow_html=True)

        btn_col1, btn_col2 = st.columns([2, 1])
        with btn_col1:
            analyze_btn = st.button(
                "Analyze Resume →",
                type="primary",
                use_container_width=True,
                disabled=(uploaded_file is None and bool(api_key)),
                key="analyze_btn",
            )
        with btn_col2:
            if not api_key:
                demo_btn = st.button("View Demo", use_container_width=True, key="demo_btn_main")
            else:
                demo_btn = False

    with col_tip:
        st.markdown("""
        <div class="card" style="height:100%">
          <div class="card-header">💡 TIPS FOR BEST RESULTS</div>
          <div class="result-item">
            <span class="result-icon">📄</span>
            <span>Use a <strong>text-based PDF</strong> (not scanned image)</span>
          </div>
          <div class="result-item">
            <span class="result-icon">📝</span>
            <span>DOCX files from Word give the cleanest extraction</span>
          </div>
          <div class="result-item">
            <span class="result-icon">🎯</span>
            <span>Have a job description ready to try the <strong>Job Match</strong> tab</span>
          </div>
          <div class="result-item">
            <span class="result-icon">✍️</span>
            <span>Copy weak bullets to test the <strong>Bullet Rewriter</strong></span>
          </div>
        </div>
        """, unsafe_allow_html=True)

    # ── Analysis logic ──
    result = None
    is_demo = False

    if demo_btn and not api_key:
        result = demo_analysis()
        is_demo = True
        st.info("Demo mode — upload your resume + add an API key for real analysis.", icon="ℹ️")

    elif analyze_btn and uploaded_file:
        file_bytes = uploaded_file.read()
        fname = uploaded_file.name.lower()

        with st.spinner("Parsing resume..."):
            try:
                if fname.endswith(".pdf"):
                    resume_text = extract_text_from_pdf(file_bytes)
                elif fname.endswith(".docx"):
                    resume_text = extract_text_from_docx(file_bytes)
                else:
                    st.error("Unsupported format. Upload PDF or DOCX.")
                    return
                if not resume_text.strip():
                    st.error("Couldn't extract text — the file may be image-based. Try a text-based PDF or DOCX.")
                    return
                st.session_state["resume_text"] = resume_text
            except Exception as e:
                st.error(f"Error reading file: {e}")
                return

        if api_key:
            with st.spinner("Analyzing with GPT-4o-mini..."):
                try:
                    prompt = ANALYSIS_PROMPT.format(resume_text=resume_text[:8000])
                    result = call_openai(prompt, api_key)
                    is_demo = False
                except json.JSONDecodeError:
                    st.error("Unexpected response from AI. Please try again.")
                    return
                except Exception as e:
                    st.error(f"API error: {e}")
                    return
        else:
            result = demo_analysis()
            is_demo = True
            st.warning("No API key found — showing demo output, not based on your resume.", icon="⚠️")

    if result:
        render_analysis_results(result, is_demo)


def render_analysis_results(result: dict, is_demo: bool):
    score = result["ats_score"]
    breakdown = result.get("score_breakdown", {})
    rating_label, rating_color = score_rating(score)

    st.markdown("---")

    # ── Row 1: Gauge + Breakdown ──
    col_gauge, col_breakdown = st.columns([1, 2])

    with col_gauge:
        st.markdown('<div class="card" style="text-align:center">', unsafe_allow_html=True)
        st.markdown('<div class="card-header" style="justify-content:center">📊 YOUR SCORE</div>', unsafe_allow_html=True)
        st.markdown(render_gauge(score), unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with col_breakdown:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-header">📈 SCORE BREAKDOWN</div>', unsafe_allow_html=True)
        st.markdown(render_breakdown(breakdown), unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    # ── Profile one-liner ──
    st.markdown(f"""
    <div class="card">
      <div class="card-header">🧠 AI PROFILE SUMMARY</div>
      <div class="profile-card">
        <p>"{result.get('one_liner', '')}"</p>
      </div>
      <div style="display:flex;gap:8px;flex-wrap:wrap">
        {''.join(f'<span class="kw-jd">{t}</span>' for t in result.get('suggested_titles', []))}
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Row 2: Strengths + Improvements ──
    col_str, col_imp = st.columns(2)

    with col_str:
        items_html = "".join(
            f'<div class="result-item"><span class="result-icon">✅</span><span>{s}</span></div>'
            for s in result.get("strengths", [])
        )
        st.markdown(f"""
        <div class="card">
          <div class="card-header">✅ KEY STRENGTHS</div>
          {items_html}
        </div>
        """, unsafe_allow_html=True)

    with col_imp:
        items_html = "".join(
            f'<div class="result-item"><span class="result-icon">🔧</span><span>{s}</span></div>'
            for s in result.get("improvements", [])
        )
        st.markdown(f"""
        <div class="card">
          <div class="card-header">🔧 ACTION ITEMS</div>
          {items_html}
        </div>
        """, unsafe_allow_html=True)

    # ── Row 3: Keywords ──
    missing = result.get("missing_keywords", [])
    kw_html = "".join(f'<span class="kw-missing">✕ {kw}</span>' for kw in missing)
    st.markdown(f"""
    <div class="card">
      <div class="card-header">🔍 MISSING KEYWORDS</div>
      <p style="font-size:0.85rem;color:#64748b;margin:0 0 0.75rem 0">
        These appear frequently in job descriptions for your target roles but are absent from your resume.
        Adding them naturally can significantly boost ATS pass rates.
      </p>
      <div class="kw-grid">{kw_html}</div>
    </div>
    """, unsafe_allow_html=True)

    # ── Download report ──
    report_lines = [
        "RESUME ANALYSIS REPORT — APPRAA TECH",
        "=" * 45,
        f"ATS Score: {score}/100 ({score_rating(score)[0]})",
        "",
        "SCORE BREAKDOWN",
        "-" * 30,
    ]
    labels = {
        "achievements": ("Quantified Results", 25),
        "keywords": ("Tech Keywords", 25),
        "structure": ("Resume Structure", 20),
        "language": ("Language & Verbs", 15),
        "completeness": ("Completeness", 15),
    }
    for key, (lbl, mx) in labels.items():
        report_lines.append(f"  {lbl}: {breakdown.get(key, 0)}/{mx}")
    report_lines += [
        "",
        "AI PROFILE SUMMARY",
        "-" * 30,
        result.get("one_liner", ""),
        "",
        "SUGGESTED JOB TITLES",
        "-" * 30,
    ]
    for t in result.get("suggested_titles", []):
        report_lines.append(f"  • {t}")
    report_lines += ["", "KEY STRENGTHS", "-" * 30]
    for s in result.get("strengths", []):
        report_lines.append(f"  • {s}")
    report_lines += ["", "ACTION ITEMS", "-" * 30]
    for i in result.get("improvements", []):
        report_lines.append(f"  • {i}")
    report_lines += ["", "MISSING KEYWORDS", "-" * 30]
    for kw in missing:
        report_lines.append(f"  • {kw}")
    report_lines += ["", "=" * 45, "Generated by Appraa Tech Resume Analyzer", "appraatech.com"]

    report_text = "\n".join(report_lines)
    col_dl, _ = st.columns([1, 2])
    with col_dl:
        st.download_button(
            "⬇ Download Report (.txt)",
            data=report_text,
            file_name="resume_analysis_appraatech.txt",
            mime="text/plain",
            use_container_width=True,
        )


def render_jd_match_tab(api_key):
    """Tab 2: Job Description Matcher"""

    st.markdown("""
    <div class="card">
      <div class="card-header">🎯 HOW IT WORKS</div>
      <div style="display:flex;gap:2rem;flex-wrap:wrap">
        <div style="flex:1;min-width:180px">
          <div style="font-size:1.5rem;margin-bottom:6px">1️⃣</div>
          <div style="font-weight:600;font-size:0.9rem;color:#0f172a">Upload your resume</div>
          <div style="font-size:0.82rem;color:#64748b;margin-top:4px">PDF or DOCX</div>
        </div>
        <div style="flex:1;min-width:180px">
          <div style="font-size:1.5rem;margin-bottom:6px">2️⃣</div>
          <div style="font-weight:600;font-size:0.9rem;color:#0f172a">Paste the job description</div>
          <div style="font-size:0.82rem;color:#64748b;margin-top:4px">From LinkedIn, Indeed, etc.</div>
        </div>
        <div style="flex:1;min-width:180px">
          <div style="font-size:1.5rem;margin-bottom:6px">3️⃣</div>
          <div style="font-weight:600;font-size:0.9rem;color:#0f172a">Get your match score</div>
          <div style="font-size:0.82rem;color:#64748b;margin-top:4px">With tailoring tips</div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-header">📎 YOUR RESUME</div>', unsafe_allow_html=True)
        jd_resume_file = st.file_uploader(
            "Upload resume (PDF or DOCX)",
            type=["pdf", "docx"],
            key="jd_resume_uploader",
        )
        # Check if already uploaded in analysis tab
        if not jd_resume_file and "resume_text" in st.session_state:
            st.caption("✅ Using resume from Analysis tab")
        st.markdown("</div>", unsafe_allow_html=True)

    with col_right:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.markdown('<div class="card-header">📋 JOB DESCRIPTION</div>', unsafe_allow_html=True)
        jd_text = st.text_area(
            "Paste the full job description here",
            height=180,
            placeholder="Paste job description from LinkedIn, Indeed, company website...",
            key="jd_text_input",
        )
        st.markdown("</div>", unsafe_allow_html=True)

    match_btn = st.button("Check Job Match →", type="primary", key="match_btn", use_container_width=False)

    if match_btn:
        # Get resume text
        resume_text = None
        if jd_resume_file:
            file_bytes = jd_resume_file.read()
            fname = jd_resume_file.name.lower()
            with st.spinner("Parsing resume..."):
                try:
                    if fname.endswith(".pdf"):
                        resume_text = extract_text_from_pdf(file_bytes)
                    elif fname.endswith(".docx"):
                        resume_text = extract_text_from_docx(file_bytes)
                except Exception as e:
                    st.error(f"Error reading resume: {e}")
                    return
        elif "resume_text" in st.session_state:
            resume_text = st.session_state["resume_text"]
        else:
            st.warning("Upload a resume above, or analyze one in the Analysis tab first.", icon="⚠️")
            return

        if not jd_text.strip():
            st.warning("Please paste a job description.", icon="⚠️")
            return

        if not api_key:
            st.markdown("""
            <div class="tip-box">
              <strong>Demo Mode:</strong> Job matching requires a live OpenAI API key.
              Add your key in Streamlit secrets to enable this feature.
            </div>
            """, unsafe_allow_html=True)
            return

        with st.spinner("Matching resume against job description..."):
            try:
                prompt = JD_MATCH_PROMPT.format(
                    resume_text=resume_text[:6000],
                    jd_text=jd_text[:4000],
                )
                result = call_openai(prompt, api_key)
            except Exception as e:
                st.error(f"Analysis error: {e}")
                return

        render_jd_match_results(result)


def render_jd_match_results(result: dict):
    score = result.get("match_score", 0)
    color = score_color(score)
    rating_label, _ = score_rating(score)

    st.markdown("---")

    col_score, col_rec = st.columns([1, 2])

    with col_score:
        st.markdown(f"""
        <div class="card" style="text-align:center">
          <div class="card-header" style="justify-content:center">🎯 JD MATCH</div>
          {render_gauge(score)}
          <div style="font-size:0.85rem;color:#64748b;margin-top:0.5rem">
            vs. this specific job
          </div>
        </div>
        """, unsafe_allow_html=True)

    with col_rec:
        rec = result.get("recommendation", "")
        tips_html = "".join(
            f'<div class="result-item"><span class="result-icon">💡</span><span>{t}</span></div>'
            for t in result.get("tailoring_tips", [])
        )
        st.markdown(f"""
        <div class="card">
          <div class="card-header">📋 RECOMMENDATION</div>
          <p style="font-size:0.92rem;color:#374151;line-height:1.65;margin:0 0 1rem 0">{rec}</p>
          <div class="card-header" style="margin-top:0.5rem">✏️ TAILORING TIPS</div>
          {tips_html}
        </div>
        """, unsafe_allow_html=True)

    col_matched, col_missing = st.columns(2)

    with col_matched:
        matched_html = "".join(f'<span class="kw-found">✓ {kw}</span>' for kw in result.get("matched_keywords", []))
        st.markdown(f"""
        <div class="card">
          <div class="card-header">✅ MATCHED KEYWORDS</div>
          <div class="kw-grid">{matched_html}</div>
        </div>
        """, unsafe_allow_html=True)

    with col_missing:
        missing_html = "".join(f'<span class="kw-missing">✕ {kw}</span>' for kw in result.get("missing_keywords", []))
        st.markdown(f"""
        <div class="card">
          <div class="card-header">❌ GAPS TO CLOSE</div>
          <div class="kw-grid">{missing_html}</div>
        </div>
        """, unsafe_allow_html=True)


def render_bullet_tab(api_key):
    """Tab 3: Bullet Point Rewriter"""

    st.markdown("""
    <div class="card">
      <div class="card-header">✍️ HOW IT WORKS</div>
      <p style="font-size:0.9rem;color:#374151;margin:0;line-height:1.6">
        Paste your weak resume bullets below — one per line. The AI will rewrite each one
        with a strong action verb, specific impact, and metrics where plausible.
        Use these as a starting point, then personalize with your real numbers.
      </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-header">📝 YOUR BULLETS (one per line)</div>', unsafe_allow_html=True)
    bullets_input = st.text_area(
        "Paste your resume bullets here",
        height=200,
        placeholder=(
            "worked on backend APIs\n"
            "helped with data migration project\n"
            "improved website performance\n"
            "managed a team of developers"
        ),
        key="bullets_input",
    )
    st.markdown("</div>", unsafe_allow_html=True)

    rewrite_btn = st.button("Rewrite Bullets →", type="primary", key="rewrite_btn")

    if rewrite_btn:
        if not bullets_input.strip():
            st.warning("Paste at least one bullet point above.", icon="⚠️")
            return

        if not api_key:
            st.markdown("""
            <div class="tip-box">
              <strong>Demo Mode:</strong> The Bullet Rewriter requires a live OpenAI API key.
              Add your key in Streamlit secrets to enable this feature.
            </div>
            """, unsafe_allow_html=True)
            return

        bullets = [b.strip() for b in bullets_input.strip().split("\n") if b.strip()]
        if len(bullets) > 10:
            st.warning("Please limit to 10 bullets at a time.", icon="⚠️")
            return

        with st.spinner(f"Rewriting {len(bullets)} bullet{'s' if len(bullets) > 1 else ''}..."):
            try:
                prompt = BULLET_REWRITE_PROMPT.format(bullets="\n".join(f"- {b}" for b in bullets))
                result = call_openai(prompt, api_key)
            except Exception as e:
                st.error(f"Rewrite error: {e}")
                return

        render_bullet_results(result)


def render_bullet_results(result: dict):
    rewrites = result.get("rewrites", [])
    if not rewrites:
        st.error("No rewrites returned. Try again.")
        return

    st.markdown("---")
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown('<div class="card-header">✨ REWRITTEN BULLETS</div>', unsafe_allow_html=True)

    all_rewritten = []
    for item in rewrites:
        original = item.get("original", "")
        rewritten = item.get("rewritten", "")
        all_rewritten.append(rewritten)
        st.markdown(f"""
        <div class="bullet-before">❌ {original}</div>
        <div class="bullet-arrow">↓</div>
        <div class="bullet-after">✅ {rewritten}</div>
        """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

    # Copy-ready output
    st.markdown("""
    <div class="tip-box">
      <strong>Tip:</strong> These are AI-generated starting points. Replace placeholder metrics
      (%, $, team size) with your real numbers before adding to your resume.
    </div>
    """, unsafe_allow_html=True)

    copy_text = "\n".join(f"• {b}" for b in all_rewritten)
    st.download_button(
        "⬇ Download Rewritten Bullets (.txt)",
        data=copy_text,
        file_name="rewritten_bullets_appraatech.txt",
        mime="text/plain",
    )


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    api_key = get_api_key()

    render_nav(api_key)
    render_hero()

    tab1, tab2, tab3 = st.tabs([
        "📊 Resume Analysis",
        "🎯 Job Description Match",
        "✍️ Bullet Rewriter",
    ])

    with tab1:
        render_analysis_tab(api_key)

    with tab2:
        render_jd_match_tab(api_key)

    with tab3:
        render_bullet_tab(api_key)

    # Footer
    st.markdown("""
    <div class="page-footer">
      Built by <a href="https://appraatech.com" target="_blank">Appraa Tech</a>
      &nbsp;·&nbsp; Powered by OpenAI GPT-4o-mini
      &nbsp;·&nbsp; <a href="https://github.com/appraatech-cyber/resume-analyzer" target="_blank">GitHub ↗</a>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
