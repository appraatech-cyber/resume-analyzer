"""
Resume Analyzer — Appraa Tech LLC
Analyzes resumes for ATS compatibility, strengths, missing keywords, and improvement suggestions.
"""

import os
import io
import json
import streamlit as st

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Resume Analyzer | Appraa Tech",
    page_icon="📄",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ── Custom CSS — Appraa Tech blue/white theme ─────────────────────────────────
st.markdown("""
<style>
/* Import Inter font */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

/* Hide default Streamlit chrome */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {visibility: hidden;}

/* Page background */
.stApp {
    background: linear-gradient(135deg, #f0f6ff 0%, #ffffff 60%, #e8f4fd 100%);
}

/* Hero header */
.hero-header {
    background: linear-gradient(135deg, #1a56db 0%, #1e40af 50%, #1d4ed8 100%);
    color: white;
    padding: 2.5rem 2rem 2rem 2rem;
    border-radius: 16px;
    margin-bottom: 2rem;
    text-align: center;
    box-shadow: 0 8px 32px rgba(26, 86, 219, 0.25);
}
.hero-header h1 {
    font-size: 2.2rem;
    font-weight: 700;
    margin: 0 0 0.4rem 0;
    letter-spacing: -0.5px;
}
.hero-header p {
    font-size: 1.05rem;
    opacity: 0.88;
    margin: 0;
    font-weight: 300;
}
.hero-badge {
    display: inline-block;
    background: rgba(255,255,255,0.18);
    border: 1px solid rgba(255,255,255,0.3);
    border-radius: 20px;
    padding: 4px 14px;
    font-size: 0.78rem;
    font-weight: 500;
    letter-spacing: 0.5px;
    margin-bottom: 1rem;
    text-transform: uppercase;
}

/* Upload zone */
.upload-section {
    background: white;
    border: 2px dashed #93c5fd;
    border-radius: 12px;
    padding: 2rem;
    text-align: center;
    margin-bottom: 1.5rem;
    transition: border-color 0.2s;
}

/* Score card */
.score-card {
    background: linear-gradient(135deg, #1a56db, #1e40af);
    color: white;
    border-radius: 16px;
    padding: 2rem;
    text-align: center;
    margin: 1.5rem 0;
    box-shadow: 0 6px 24px rgba(26, 86, 219, 0.3);
}
.score-number {
    font-size: 5rem;
    font-weight: 700;
    line-height: 1;
    margin: 0.3rem 0;
}
.score-label {
    font-size: 0.9rem;
    opacity: 0.82;
    text-transform: uppercase;
    letter-spacing: 1px;
    font-weight: 500;
}
.score-rating {
    font-size: 1.3rem;
    font-weight: 600;
    margin-top: 0.5rem;
}

/* Result sections */
.result-card {
    background: white;
    border-radius: 12px;
    padding: 1.5rem;
    margin: 1rem 0;
    box-shadow: 0 2px 12px rgba(0,0,0,0.06);
    border-left: 4px solid #1a56db;
}
.result-card h3 {
    color: #1a56db;
    font-size: 1rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin: 0 0 1rem 0;
}
.result-card ul {
    margin: 0;
    padding-left: 1.2rem;
}
.result-card li {
    color: #374151;
    margin-bottom: 0.5rem;
    line-height: 1.5;
}

/* One-liner box */
.oneliner-card {
    background: linear-gradient(135deg, #eff6ff, #dbeafe);
    border: 1px solid #bfdbfe;
    border-radius: 12px;
    padding: 1.5rem;
    margin: 1rem 0;
    text-align: center;
}
.oneliner-card p {
    font-size: 1.1rem;
    color: #1e3a8a;
    font-style: italic;
    font-weight: 500;
    margin: 0;
    line-height: 1.6;
}

/* Demo mode banner */
.demo-banner {
    background: linear-gradient(135deg, #fef3c7, #fde68a);
    border: 1px solid #f59e0b;
    border-radius: 10px;
    padding: 1rem 1.5rem;
    margin: 1rem 0;
    color: #92400e;
    font-size: 0.9rem;
}

/* Keywords pills */
.keyword-pill {
    display: inline-block;
    background: #fee2e2;
    color: #991b1b;
    border-radius: 20px;
    padding: 4px 12px;
    font-size: 0.82rem;
    font-weight: 500;
    margin: 3px;
}

/* Divider */
.section-divider {
    border: none;
    border-top: 1px solid #e5e7eb;
    margin: 1.5rem 0;
}

/* Footer */
.footer {
    text-align: center;
    color: #9ca3af;
    font-size: 0.8rem;
    padding: 2rem 0 1rem 0;
}
.footer a {
    color: #1a56db;
    text-decoration: none;
}
</style>
""", unsafe_allow_html=True)

# ── Helpers ───────────────────────────────────────────────────────────────────

def extract_text_from_pdf(file_bytes: bytes) -> str:
    """Extract text from a PDF file using pdfplumber (preferred) or PyPDF2."""
    text = ""
    try:
        import pdfplumber
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        if text.strip():
            return text
    except Exception:
        pass

    # Fallback to PyPDF2
    try:
        import PyPDF2
        reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
        for page in reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        raise ValueError(f"Could not extract text from PDF: {e}")


def extract_text_from_docx(file_bytes: bytes) -> str:
    """Extract text from a DOCX file using python-docx."""
    try:
        from docx import Document
        doc = Document(io.BytesIO(file_bytes))
        paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
        return "\n".join(paragraphs)
    except Exception as e:
        raise ValueError(f"Could not extract text from DOCX: {e}")


def get_api_key() -> str | None:
    """Return OpenAI API key from Streamlit secrets or environment variable."""
    # 1. Streamlit secrets (for Community Cloud deploy)
    try:
        return st.secrets["OPENAI_API_KEY"]
    except Exception:
        pass
    # 2. Environment variable (local development)
    return os.environ.get("OPENAI_API_KEY")


def score_to_rating(score: int) -> str:
    if score >= 85:
        return "Excellent ✦"
    elif score >= 70:
        return "Good"
    elif score >= 55:
        return "Fair"
    else:
        return "Needs Work"


# ── LLM Analysis ─────────────────────────────────────────────────────────────

ANALYSIS_PROMPT = """You are an expert ATS (Applicant Tracking System) resume analyst and career coach. Analyze the following resume and return ONLY a valid JSON object — no markdown, no extra text.

The JSON must have exactly these keys:
{{
  "ats_score": <integer 0-100>,
  "one_liner": "<A single punchy sentence summarizing the candidate's professional identity>",
  "strengths": ["<strength 1>", "<strength 2>", "<strength 3>", "<optionally strength 4>", "<optionally strength 5>"],
  "missing_keywords": ["<keyword 1>", "<keyword 2>", ...],
  "improvements": ["<specific actionable improvement 1>", "<specific actionable improvement 2>", ...]
}}

Scoring criteria for ats_score:
- Quantified achievements (metrics, numbers): up to 20 pts
- Action verbs and strong language: up to 15 pts
- Relevant keywords for tech roles: up to 20 pts
- Clear structure (sections, formatting signals): up to 15 pts
- Contact info completeness: up to 10 pts
- Skills section quality: up to 10 pts
- Education and certifications: up to 10 pts

For missing_keywords: focus on common tech job description keywords this resume lacks (frameworks, tools, methodologies, soft skills). List 5-10 keywords.
For improvements: give 4-6 specific, actionable suggestions referencing actual content in the resume.
For strengths: identify 3-5 genuine strengths based on what is actually in the resume.

Resume text:
---
{resume_text}
---

Return only the JSON object."""


def analyze_with_anthropic(resume_text: str, api_key: str) -> dict:
    """Call OpenAI GPT-4o-mini to analyze the resume."""
    from openai import OpenAI

    client = OpenAI(api_key=api_key)

    prompt = ANALYSIS_PROMPT.format(resume_text=resume_text[:8000])  # cap at 8k chars

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        max_tokens=1024,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": "You are an expert ATS resume analyst. Always respond with valid JSON only."},
            {"role": "user", "content": prompt}
        ]
    )

    raw = response.choices[0].message.content.strip()

    # Strip any accidental markdown fences
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()

    return json.loads(raw)


def demo_analysis() -> dict:
    """Return a realistic demo result when no API key is present."""
    return {
        "ats_score": 72,
        "one_liner": "Full-stack engineer with 5+ years building scalable web applications, blending strong Python/React expertise with a product-minded approach to shipping user-centric features.",
        "strengths": [
            "Clear demonstration of end-to-end project ownership across multiple roles",
            "Strong backend skills with Python, Django, and REST API design",
            "Evidence of cross-functional collaboration and Agile team experience",
            "Progressive career growth with increasing responsibility",
        ],
        "missing_keywords": [
            "CI/CD", "Docker", "Kubernetes", "AWS / cloud platform", "GraphQL",
            "TypeScript", "unit testing", "system design", "microservices", "performance optimization"
        ],
        "improvements": [
            "Add quantified metrics to each bullet — e.g., 'reduced load time by 40%' instead of 'improved performance'.",
            "Include a Skills section with explicit groupings: Languages, Frameworks, Cloud, Tools.",
            "Add a 2–3 line professional summary at the top optimized for ATS keyword scanning.",
            "Mention cloud platforms (AWS, GCP, or Azure) if you have experience — they appear in 80%+ of tech JDs.",
            "Use stronger action verbs: replace 'worked on' / 'helped with' with 'architected', 'led', 'delivered'.",
            "Add GitHub URL and LinkedIn profile to the contact header.",
        ],
    }


# ── UI ────────────────────────────────────────────────────────────────────────

def render_hero():
    st.markdown("""
    <div class="hero-header">
        <div class="hero-badge">Appraa Tech LLC</div>
        <h1>📄 Resume Analyzer</h1>
        <p>Get an instant ATS compatibility score, keyword gaps, and actionable feedback — powered by AI.</p>
    </div>
    """, unsafe_allow_html=True)


def render_results(result: dict, is_demo: bool):
    if is_demo:
        st.markdown("""
        <div class="demo-banner">
            <strong>Demo Mode</strong> — No API key detected. Showing sample analysis output.
            Set the <code>ANTHROPIC_API_KEY</code> environment variable to analyze real resumes.
        </div>
        """, unsafe_allow_html=True)

    # Score card
    score = result["ats_score"]
    rating = score_to_rating(score)
    st.markdown(f"""
    <div class="score-card">
        <div class="score-label">ATS Compatibility Score</div>
        <div class="score-number">{score}</div>
        <div class="score-rating">{rating}</div>
    </div>
    """, unsafe_allow_html=True)

    # Progress bar (visual reinforcement)
    st.progress(score / 100)

    # One-liner
    st.markdown(f"""
    <div class="oneliner-card">
        <p>"{result['one_liner']}"</p>
    </div>
    """, unsafe_allow_html=True)

    # Three columns of detail
    col1, col2 = st.columns(2)

    with col1:
        strengths_html = "".join(f"<li>{s}</li>" for s in result["strengths"])
        st.markdown(f"""
        <div class="result-card">
            <h3>✅ Key Strengths</h3>
            <ul>{strengths_html}</ul>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        improvements_html = "".join(f"<li>{s}</li>" for s in result["improvements"])
        st.markdown(f"""
        <div class="result-card">
            <h3>🔧 Improvements</h3>
            <ul>{improvements_html}</ul>
        </div>
        """, unsafe_allow_html=True)

    # Missing keywords as pills
    keywords_pills = "".join(
        f'<span class="keyword-pill">{kw}</span>' for kw in result["missing_keywords"]
    )
    st.markdown(f"""
    <div class="result-card" style="border-left-color:#ef4444;">
        <h3 style="color:#dc2626;">🔍 Missing Keywords</h3>
        <p style="color:#6b7280; font-size:0.85rem; margin: 0 0 0.8rem 0;">
            Add these to your resume to match common tech job descriptions:
        </p>
        <div>{keywords_pills}</div>
    </div>
    """, unsafe_allow_html=True)


def render_footer():
    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
    st.markdown("""
    <div class="footer">
        Built by <a href="https://appraatech.com" target="_blank">Appraa Tech LLC</a> &nbsp;·&nbsp;
        Powered by <a href="https://anthropic.com" target="_blank">Anthropic Claude</a> &nbsp;·&nbsp;
        <a href="https://github.com/SatyaKoppula" target="_blank">GitHub</a>
    </div>
    """, unsafe_allow_html=True)


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    render_hero()

    api_key = get_api_key()

    # Show API key status
    if api_key:
        st.success("API key detected — ready to analyze real resumes.", icon="🔑")
    else:
        st.info(
            "No API key found. Running in **demo mode**. "
            "Set `ANTHROPIC_API_KEY` in your environment or Streamlit secrets to enable live analysis.",
            icon="ℹ️",
        )

    st.markdown("### Upload Your Resume")
    uploaded_file = st.file_uploader(
        "Drag & drop or click to upload",
        type=["pdf", "docx"],
        help="Supported formats: PDF, DOCX — max 10 MB",
    )

    analyze_btn = st.button(
        "Analyze Resume →",
        type="primary",
        disabled=(uploaded_file is None and api_key is not None),
        use_container_width=True,
    )

    # If no file but no API key, allow demo run
    if (uploaded_file is None) and not api_key:
        if st.button("▶ Run Demo Analysis", use_container_width=True):
            render_results(demo_analysis(), is_demo=True)
            render_footer()
            return

    if analyze_btn or (uploaded_file is not None and not api_key):
        if uploaded_file is not None:
            file_bytes = uploaded_file.read()
            filename = uploaded_file.name.lower()

            with st.spinner("Parsing resume..."):
                try:
                    if filename.endswith(".pdf"):
                        resume_text = extract_text_from_pdf(file_bytes)
                    elif filename.endswith(".docx"):
                        resume_text = extract_text_from_docx(file_bytes)
                    else:
                        st.error("Unsupported file type. Please upload PDF or DOCX.")
                        return

                    if not resume_text.strip():
                        st.error("Could not extract text from this file. It may be image-based. Please try a text-based PDF or DOCX.")
                        return
                except Exception as e:
                    st.error(f"Error reading file: {e}")
                    return

            if api_key:
                with st.spinner("Analyzing with Claude AI..."):
                    try:
                        result = analyze_with_anthropic(resume_text, api_key)
                        render_results(result, is_demo=False)
                    except json.JSONDecodeError:
                        st.error("AI returned an unexpected response. Please try again.")
                    except Exception as e:
                        st.error(f"API error: {e}")
            else:
                # No API key but file uploaded — show demo with notice
                st.warning("No API key set. Showing demo output (not based on your actual resume).")
                render_results(demo_analysis(), is_demo=True)

        elif not api_key:
            render_results(demo_analysis(), is_demo=True)

    render_footer()


if __name__ == "__main__":
    main()
