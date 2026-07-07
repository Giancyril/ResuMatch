import streamlit as st
import json
from gemini_service import analyze_match, generate_cover_letter
from scraper import scrape_job_description
from utils import extract_text_from_pdf

# Page Configuration
st.set_page_config(
    page_title="ResuMatch — Resume Review Report",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initialize Session State
if "history" not in st.session_state:
    st.session_state.history = []
if "resume_text_state" not in st.session_state:
    st.session_state.resume_text_state = ""
if "jd_text_state" not in st.session_state:
    st.session_state.jd_text_state = ""
if "url_last_scraped" not in st.session_state:
    st.session_state.url_last_scraped = ""
if "cover_letter" not in st.session_state:
    st.session_state.cover_letter = ""

# ---------------------------------------------------------------------------
# Design system: "Document Review Report"
# ---------------------------------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,400;0,9..144,600;1,9..144,400;1,9..144,600&family=IBM+Plex+Sans:wght@300;400;500;600&family=IBM+Plex+Mono:wght@400;500;600&display=swap');

    /* ── Design Tokens ──────────────────────────────────────────────────── */
    :root {
        --paper:         #F5F2EC;
        --surface:       #FFFFFF;
        --surface-2:     #FAFAF8;
        --ink:           #1A1816;
        --ink-muted:     #6B6459;
        --ink-faint:     #A89F94;
        --rule:          #E0D8CC;
        --rule-strong:   #C8BFB3;
        --accent:        #1C4434;
        --accent-mid:    #2A5E48;
        --accent-soft:   rgba(28, 68, 52, 0.09);
        --accent-softer: rgba(28, 68, 52, 0.05);
        --flag:          #922F22;
        --flag-soft:     rgba(146, 47, 34, 0.07);
        --amber:         #8A5E12;
        --amber-soft:    rgba(138, 94, 18, 0.08);
        --radius-sm:     4px;
        --radius-md:     8px;
        --radius-lg:     12px;
        --shadow-sm:     0 1px 3px rgba(26,24,22,0.06), 0 1px 2px rgba(26,24,22,0.04);
        --shadow-md:     0 4px 16px -4px rgba(26,24,22,0.12), 0 1px 4px rgba(26,24,22,0.06);
        --shadow-lg:     0 8px 30px -8px rgba(26,24,22,0.16), 0 2px 8px rgba(26,24,22,0.06);
    }

    /* ── Global reset ───────────────────────────────────────────────────── */
    header { visibility: hidden; }
    footer { visibility: hidden; }
    #MainMenu { visibility: hidden; }

    .stApp {
        background-color: var(--paper) !important;
        background-image: 
            radial-gradient(ellipse 80% 50% at 50% -10%, rgba(28,68,52,0.06) 0%, transparent 70%);
        color: var(--ink);
        font-family: 'IBM Plex Sans', system-ui, -apple-system, sans-serif;
    }

    .block-container {
        padding-top: 0 !important;
        max-width: 1200px !important;
    }

    ::-webkit-scrollbar { width: 6px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: var(--rule-strong); border-radius: 3px; }
    ::-webkit-scrollbar-thumb:hover { background: var(--ink-muted); }

    /* ── Tab bar ────────────────────────────────────────────────────────── */
    div[data-baseweb="tab-list"],
    div[data-testid="stTabBar"] {
        gap: 0 !important;
        border-bottom: 1px solid var(--rule) !important;
        background-color: transparent !important;
        padding: 0 0.5rem !important;
    }

    button[data-baseweb="tab"],
    button[data-testid="stTab"],
    button[data-baseweb="tab"]:not([aria-selected="true"]),
    button[data-testid="stTab"]:not([aria-selected="true"]) {
        font-family: 'IBM Plex Mono', monospace !important;
        font-size: 0.72rem !important;
        font-weight: 500 !important;
        color: var(--ink-muted) !important;
        background-color: transparent !important;
        border: none !important;
        border-bottom: 2px solid transparent !important;
        padding: 12px 20px !important;
        letter-spacing: 0.12em !important;
        text-transform: uppercase !important;
        box-shadow: none !important;
        outline: none !important;
        cursor: pointer !important;
        transition: color 0.2s ease, border-color 0.2s ease !important;
        margin-bottom: -1px !important;
    }

    button[data-baseweb="tab"] p,
    button[data-baseweb="tab"] span,
    button[data-baseweb="tab"] div,
    button[data-baseweb="tab"] *,
    button[data-testid="stTab"] p,
    button[data-testid="stTab"] span,
    button[data-testid="stTab"] div,
    button[data-testid="stTab"] * {
        color: inherit !important;
        font-family: inherit !important;
        font-size: inherit !important;
        font-weight: inherit !important;
        letter-spacing: inherit !important;
        text-transform: inherit !important;
        background: transparent !important;
    }

    button[data-baseweb="tab"][aria-selected="true"],
    button[data-testid="stTab"][aria-selected="true"] {
        color: var(--ink) !important;
        font-weight: 700 !important;
        border-bottom: 2px solid var(--ink) !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] *,
    button[data-testid="stTab"][aria-selected="true"] * {
        color: var(--ink) !important;
        font-weight: 700 !important;
    }

    button[data-baseweb="tab"]:hover,
    button[data-testid="stTab"]:hover {
        color: var(--ink) !important;
        border-bottom-color: var(--rule-strong) !important;
    }
    button[data-baseweb="tab"]:hover *,
    button[data-testid="stTab"]:hover * { color: var(--ink) !important; }

    div[data-baseweb="tab-highlight"],
    div[data-baseweb="tab-border"] { display: none !important; }

    /* ── Letterhead ─────────────────────────────────────────────────────── */
    .letterhead {
        text-align: center !important;
        padding: 3.5rem 2rem 2.5rem !important;
        margin-bottom: 0 !important;
        position: relative !important;
    }
    .letterhead * {
        text-align: center !important;
    }
    .letterhead-rule {
        width: 48px;
        height: 2px;
        background: var(--accent);
        margin: 0 auto 1.25rem;
        border-radius: 1px;
    }
    .eyebrow {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.65rem;
        font-weight: 500;
        letter-spacing: 0.3em;
        text-transform: uppercase;
        color: var(--ink-muted);
        margin-bottom: 1rem;
    }
    .masthead {
        font-family: 'Fraunces', serif;
        font-size: clamp(2.5rem, 5vw, 3.5rem);
        font-weight: 600;
        color: var(--ink);
        letter-spacing: -0.03em;
        line-height: 1;
        margin-bottom: 1rem;
    }
    .masthead em {
        color: var(--accent);
        font-style: italic;
        font-weight: 400;
    }
    .deck {
        font-family: 'IBM Plex Sans', sans-serif !important;
        font-size: 0.95rem !important;
        color: var(--ink-muted) !important;
        max-width: 520px !important;
        margin: 0 auto 2rem !important;
        line-height: 1.7 !important;
        font-weight: 400 !important;
        text-align: center !important;
        display: block !important;
    }
    .letterhead-divider {
        border: none;
        border-top: 1px solid var(--rule);
        margin: 0;
    }

    /* ── Exhibit section labels ─────────────────────────────────────────── */
    .exhibit-label {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.62rem;
        font-weight: 600;
        letter-spacing: 0.2em;
        text-transform: uppercase;
        color: var(--ink-faint);
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
        gap: 0.6rem;
    }
    .exhibit-label::after {
        content: '';
        flex: 1;
        height: 1px;
        background: var(--rule);
    }

    /* ── Card containers ────────────────────────────────────────────────── */
    div[data-testid="stVerticalBlockBorderWrapper"],
    div[data-testid="stVerticalBlockBorderWrapper"] > div {
        border: 1px solid var(--rule) !important;
        background-color: var(--surface) !important;
        border-radius: var(--radius-lg) !important;
        box-shadow: var(--shadow-sm) !important;
        transition: box-shadow 0.2s ease, border-color 0.2s ease !important;
    }
    div[data-testid="stVerticalBlockBorderWrapper"]:hover {
        box-shadow: var(--shadow-md) !important;
        border-color: var(--rule-strong) !important;
    }
    div[data-testid="stVerticalBlockBorderWrapper"] {
        padding: 0.5rem !important;
    }

    /* ── Textarea ───────────────────────────────────────────────────────── */
    div[data-baseweb="textarea"] {
        border: none !important;
        background: transparent !important;
    }
    div[data-baseweb="textarea"] > div {
        background-color: var(--surface-2) !important;
        border: 1px solid var(--rule) !important;
        border-radius: var(--radius-md) !important;
        transition: border-color 0.15s ease, box-shadow 0.15s ease !important;
    }
    div[data-baseweb="textarea"]:focus-within > div {
        border-color: var(--accent) !important;
        box-shadow: 0 0 0 3px var(--accent-soft) !important;
    }
    textarea {
        background-color: var(--surface-2) !important;
        color: var(--ink) !important;
        font-family: 'IBM Plex Mono', monospace !important;
        font-size: 0.82rem !important;
        line-height: 1.65 !important;
        border: none !important;
        outline: none !important;
        box-shadow: none !important;
    }
    textarea:focus { border: none !important; outline: none !important; box-shadow: none !important; }
    textarea::placeholder { color: var(--ink-faint) !important; }

    /* ── Primary buttons ────────────────────────────────────────────────── */
    div.stButton > button {
        background: var(--accent) !important;
        color: #FFFFFF !important;
        border: none !important;
        border-radius: var(--radius-md) !important;
        padding: 0.85rem 2.5rem !important;
        font-family: 'IBM Plex Sans', sans-serif !important;
        font-weight: 600 !important;
        font-size: 0.85rem !important;
        letter-spacing: 0.02em !important;
        box-shadow: 0 2px 8px -2px rgba(28, 68, 52, 0.4), 0 1px 3px rgba(28,68,52,0.2) !important;
        transition: all 0.2s ease !important;
        width: 100% !important;
    }
    div.stButton > button:hover {
        background: var(--accent-mid) !important;
        box-shadow: 0 4px 16px -4px rgba(28, 68, 52, 0.5), 0 2px 6px rgba(28,68,52,0.2) !important;
        transform: translateY(-1px) !important;
    }
    div.stButton > button:active { transform: translateY(0) !important; }

    /* ── Download buttons ───────────────────────────────────────────────── */
    div[data-testid="stDownloadButton"] > button {
        background: var(--surface) !important;
        color: var(--accent) !important;
        border: 1.5px solid var(--accent) !important;
        border-radius: var(--radius-md) !important;
        font-family: 'IBM Plex Sans', sans-serif !important;
        font-size: 0.82rem !important;
        font-weight: 600 !important;
        width: 100% !important;
        transition: all 0.15s ease !important;
        padding: 0.6rem 1rem !important;
    }
    div[data-testid="stDownloadButton"] > button:hover {
        background: var(--accent-softer) !important;
    }

    /* ── Report headings ────────────────────────────────────────────────── */
    .report-heading {
        text-align: center;
        padding: 1.5rem 0 0.5rem;
    }
    .report-kicker {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.65rem;
        letter-spacing: 0.3em;
        text-transform: uppercase;
        color: var(--ink-muted);
    }
    .report-title {
        font-family: 'Fraunces', serif;
        font-size: 2rem;
        font-weight: 600;
        color: var(--ink);
        margin-top: 0.5rem;
        letter-spacing: -0.02em;
    }
    .section-number {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.65rem;
        font-weight: 600;
        letter-spacing: 0.2em;
        color: var(--accent);
        text-transform: uppercase;
        margin-bottom: 0.75rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    .section-number::before {
        content: '';
        display: inline-block;
        width: 8px;
        height: 8px;
        background: var(--accent);
        border-radius: 50%;
    }

    /* ── ATS Score stamp ────────────────────────────────────────────────── */
    .stamp-wrap {
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 1.5rem 0;
    }
    .stamp {
        width: 160px;
        height: 160px;
        border-radius: 50%;
        border: 2.5px solid var(--stamp-color, var(--accent));
        outline: 1px dashed var(--stamp-color, var(--accent));
        outline-offset: 5px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        transform: rotate(-6deg);
        color: var(--stamp-color, var(--accent));
        font-family: 'IBM Plex Mono', monospace;
        background: radial-gradient(ellipse at center, rgba(255,255,255,0.8) 0%, transparent 70%);
    }
    .stamp-score {
        font-size: 2.8rem;
        font-weight: 600;
        line-height: 1;
        letter-spacing: -0.02em;
    }
    .stamp-verdict {
        font-size: 0.6rem;
        font-weight: 600;
        letter-spacing: 0.16em;
        text-transform: uppercase;
        margin-top: 0.4rem;
        text-align: center;
        padding: 0 0.5rem;
    }

    /* ── Keyword pills ──────────────────────────────────────────────────── */
    .flag-list {
        display: flex;
        flex-wrap: wrap;
        gap: 0.4rem 0.6rem;
        margin-top: 0.75rem;
    }
    .flag-term {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.75rem;
        font-weight: 500;
        padding: 0.2rem 0.6rem;
        border-radius: 4px;
        border: 1px solid currentColor;
        opacity: 0.9;
    }
    .flag-term-technical { color: var(--accent) !important; background: var(--accent-softer) !important; border-color: rgba(28,68,52,0.2) !important; }
    .flag-term-tools { color: var(--amber) !important; background: var(--amber-soft) !important; border-color: rgba(138,94,18,0.2) !important; }
    .flag-term-soft { color: var(--flag) !important; background: var(--flag-soft) !important; border-color: rgba(146,47,34,0.2) !important; }

    /* ── Diff blocks ────────────────────────────────────────────────────── */
    .diff-block {
        border: 1px solid var(--rule);
        border-radius: var(--radius-md);
        margin-bottom: 1rem;
        overflow: hidden;
        background: var(--surface);
        box-shadow: var(--shadow-sm);
    }
    .diff-line {
        padding: 0.75rem 1rem;
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.8rem;
        line-height: 1.55;
        border-left: 3px solid transparent;
    }
    .diff-remove {
        background: var(--flag-soft);
        border-left-color: var(--flag);
        color: #7A241B;
        text-decoration: line-through;
        text-decoration-color: rgba(146,47,34,0.4);
    }
    .diff-add {
        background: var(--accent-softer);
        border-left-color: var(--accent);
        color: var(--accent);
        font-weight: 500;
    }
    .diff-impact {
        padding: 0.5rem 1rem;
        font-size: 0.75rem;
        color: var(--ink-muted);
        background: var(--surface-2);
        border-top: 1px solid var(--rule);
        font-family: 'IBM Plex Sans', sans-serif;
    }
    .diff-impact b { color: var(--ink); font-weight: 600; }

    /* ── File Uploader ──────────────────────────────────────────────────── */
    div[data-testid="stFileUploader"] { color: var(--ink) !important; }
    div[data-testid="stFileUploader"] label {
        color: var(--ink) !important;
        font-family: 'IBM Plex Sans', sans-serif !important;
        font-size: 0.82rem !important;
        font-weight: 600 !important;
    }
    section[data-testid="stFileUploaderDropzone"] {
        background-color: var(--surface-2) !important;
        border: 1.5px dashed var(--rule-strong) !important;
        border-radius: var(--radius-md) !important;
        padding: 1.25rem !important;
        transition: border-color 0.15s ease, background-color 0.15s ease !important;
    }
    section[data-testid="stFileUploaderDropzone"]:hover {
        border-color: var(--accent) !important;
        background-color: var(--accent-softer) !important;
    }
    section[data-testid="stFileUploaderDropzone"] p,
    section[data-testid="stFileUploaderDropzone"] span { color: var(--ink-muted) !important; font-size: 0.82rem !important; }
    section[data-testid="stFileUploaderDropzone"] small { color: var(--ink-faint) !important; font-size: 0.75rem !important; }
    section[data-testid="stFileUploaderDropzone"] button {
        background-color: var(--surface) !important;
        color: var(--ink) !important;
        border: 1px solid var(--rule-strong) !important;
        border-radius: var(--radius-sm) !important;
        padding: 6px 14px !important;
        font-family: 'IBM Plex Sans', sans-serif !important;
        font-size: 0.78rem !important;
        font-weight: 600 !important;
        box-shadow: var(--shadow-sm) !important;
        transition: all 0.15s ease !important;
    }
    section[data-testid="stFileUploaderDropzone"] button:hover {
        border-color: var(--accent) !important;
        color: var(--accent) !important;
        background-color: var(--accent-softer) !important;
    }
    div[data-testid="stUploadedFile"] {
        background-color: var(--accent-softer) !important;
        border: 1px solid rgba(28,68,52,0.15) !important;
        border-radius: var(--radius-sm) !important;
        padding: 4px 10px !important;
    }
    div[data-testid="stUploadedFile"] span,
    div[data-testid="stUploadedFile"] div { color: var(--ink) !important; }
    div[data-testid="stUploadedFile"] button { color: var(--flag) !important; }

    /* ── Text input (URL Scraper) ────────────────────────────────────────── */
    div[data-baseweb="input"] {
        border: none !important;
        background: transparent !important;
        outline: none !important;
        box-shadow: none !important;
    }
    div[data-baseweb="input"] > div {
        background-color: var(--surface-2) !important;
        border: 1px solid var(--rule) !important;
        border-radius: var(--radius-md) !important;
        transition: all 0.15s ease !important;
        box-shadow: none !important;
    }
    div[data-baseweb="input"]:focus-within > div,
    div[data-baseweb="input"] > div:focus-within,
    div[data-baseweb="input"] div:focus-within {
        border-color: var(--accent) !important;
        box-shadow: 0 0 0 3px var(--accent-soft) !important;
    }
    input {
        background-color: var(--surface-2) !important;
        color: var(--ink) !important;
        font-family: 'IBM Plex Mono', monospace !important;
        font-size: 0.85rem !important;
        line-height: 1.6 !important;
        border: none !important;
        outline: none !important;
        box-shadow: none !important;
    }
    input:focus { border: none !important; outline: none !important; box-shadow: none !important; }
    input::placeholder { color: var(--ink-faint) !important; }
    div[data-testid="stTextInput"] label p {
        color: var(--ink) !important;
        font-family: 'IBM Plex Sans', sans-serif !important;
        font-size: 0.82rem !important;
        font-weight: 600 !important;
    }

    /* ── Alert boxes ────────────────────────────────────────────────────── */
    div[data-testid="stAlert"] {
        background-color: var(--surface) !important;
        color: var(--ink) !important;
        border: 1px solid var(--rule) !important;
        border-radius: var(--radius-md) !important;
        box-shadow: var(--shadow-sm) !important;
    }
    div[data-testid="stAlert"] p,
    div[data-testid="stAlert"] span,
    div[data-testid="stAlert"] div,
    div[data-testid="stAlert"] svg { color: var(--ink) !important; fill: var(--ink) !important; }
</style>
""", unsafe_allow_html=True)

# ── Letterhead ───────────────────────────────────────────────────────────────
st.markdown("""
<div class="letterhead">
    <div class="eyebrow">AI-Powered Resume Intelligence</div>
    <div class="masthead">Resu<em>Match</em></div>
    <p class="deck">Upload your resume and a target job description. Gemini scores the match, flags keyword gaps, suggests bullet rewrites, generates skill roadmaps, and drafts your cover letter.</p>
</div>
<hr class="letterhead-divider">
""", unsafe_allow_html=True)




# Create workspace tabs
tab_single, tab_multi, tab_cover = st.tabs([
    "Single Resume Review",
    "Multi-Resume Comparison",
    "Cover Letter Workspace"
])

# ---------------------------------------------------------------------------
# Tab 1: Single Resume Review
# ---------------------------------------------------------------------------
with tab_single:
    # URL Scraper Input (Full Width above the two side-by-side exhibits)
    with st.container(border=True):
        st.markdown('<span class="exhibit-label">Auto-Scrape Target Role URL</span>', unsafe_allow_html=True)
        url_input = st.text_input(
            "Paste Job Posting URL (LinkedIn, Indeed, Lever, Greenhouse, etc.)",
            value=st.session_state.url_last_scraped if st.session_state.url_last_scraped else "",
            placeholder="https://...",
            key="jd_url_input_single",
            label_visibility="visible"
        )
        
        if url_input.strip() and url_input != st.session_state.url_last_scraped:
            with st.spinner("Scraping job description..."):
                try:
                    scraped_text = scrape_job_description(url_input)
                    st.session_state.jd_text_state = scraped_text
                    st.session_state.url_last_scraped = url_input
                    st.success("Successfully scraped Job Description! The text has been populated in Exhibit B below.")
                except Exception as e:
                    st.error(f"Scraping failed: {e}")

    # Side-by-side Exhibits
    col1, col2 = st.columns(2)

    with col1:
        with st.container(border=True):
            st.markdown('<span class="exhibit-label">Exhibit A — Resume</span>', unsafe_allow_html=True)
            
            uploaded_resume = st.file_uploader(
                "Upload Resume (PDF or TXT)",
                type=["pdf", "txt"],
                key="resume_uploader_single",
                label_visibility="visible"
            )
            
            if uploaded_resume is not None:
                try:
                    file_bytes = uploaded_resume.read()
                    if uploaded_resume.name.endswith(".pdf"):
                        st.session_state.resume_text_state = extract_text_from_pdf(file_bytes)
                    else:
                        st.session_state.resume_text_state = file_bytes.decode("utf-8", errors="ignore")
                    st.markdown(f'<p style="font-size: 0.72rem; color: var(--accent); font-family: monospace; margin: -5px 0 10px 0;">✔ Loaded {len(st.session_state.resume_text_state)} chars. You can edit below.</p>', unsafe_allow_html=True)
                except Exception as ex:
                    st.error(f"Error loading resume file: {ex}")
            
            resume_input = st.text_area(
                "Resume Plain Text",
                value=st.session_state.resume_text_state,
                height=260,
                placeholder="Or paste your resume text here...",
                label_visibility="collapsed",
                key="resume_text_area_single"
            )
            st.session_state.resume_text_state = resume_input

    with col2:
        with st.container(border=True):
            st.markdown('<span class="exhibit-label">Exhibit B — Target Role</span>', unsafe_allow_html=True)
            
            uploaded_jd = st.file_uploader(
                "Upload Job Description (PDF or TXT)",
                type=["pdf", "txt"],
                key="jd_uploader_single",
                label_visibility="visible"
            )
            
            if uploaded_jd is not None:
                try:
                    file_bytes = uploaded_jd.read()
                    if uploaded_jd.name.endswith(".pdf"):
                        st.session_state.jd_text_state = extract_text_from_pdf(file_bytes)
                    else:
                        st.session_state.jd_text_state = file_bytes.decode("utf-8", errors="ignore")
                    st.markdown(f'<p style="font-size: 0.72rem; color: var(--accent); font-family: monospace; margin: -5px 0 10px 0;">✔ Loaded {len(st.session_state.jd_text_state)} chars. You can edit below.</p>', unsafe_allow_html=True)
                except Exception as ex:
                    st.error(f"Error loading job description: {ex}")
            
            jd_input = st.text_area(
                "Job Description Plain Text",
                value=st.session_state.jd_text_state,
                height=260,
                placeholder="Or paste the target job description here...",
                label_visibility="collapsed",
                key="jd_text_area_single"
            )
            st.session_state.jd_text_state = jd_input

    st.markdown("<div style='max-width: 260px; margin: 1.75rem auto 0.5rem auto;'>", unsafe_allow_html=True)
    analyze_clicked = st.button("Review Alignment", key="analyze_btn_single")
    st.markdown("</div>", unsafe_allow_html=True)


    if analyze_clicked:
        if not resume_input.strip() or not jd_input.strip():
            st.warning("Both exhibits are required before a review can be filed. Paste your resume and the job description above.")
        else:
            with st.spinner("Filing exhibits and cross-referencing keyword density…"):
                try:
                    analysis = analyze_match(resume_input, jd_input)
                    score = int(analysis.get("match_score", 0))
                    
                    st.session_state.history.append({
                        "version": f"v{len(st.session_state.history) + 1}",
                        "score": score,
                        "gaps": len(analysis.get("missing_keywords", [])),
                        "bullets": len(analysis.get("rewritten_bullets", []))
                    })
                    
                    missing_keywords = analysis.get("missing_keywords", [])
                    rewritten_bullets = analysis.get("rewritten_bullets", [])
                    skill_roadmaps = analysis.get("skill_roadmaps", [])

                    if score >= 80:
                        stamp_color, verdict = "#1F4D3A", "Strong Match"
                    elif score >= 50:
                        stamp_color, verdict = "#9C6B14", "Partial Match"
                    else:
                        stamp_color, verdict = "#A13327", "Needs Revision"

                    st.markdown("""
                    <div class="report-heading">
                        <div class="report-kicker">Findings</div>
                        <div class="report-title">Alignment Report</div>
                    </div>
                    """, unsafe_allow_html=True)

                    res_col1, res_col2 = st.columns([1, 2])

                    with res_col1:
                        with st.container(border=True):
                            st.markdown('<div class="section-number">01 — Alignment Score</div>', unsafe_allow_html=True)
                            st.markdown(f"""
                            <div class="stamp-wrap">
                                <div class="stamp" style="--stamp-color: {stamp_color};">
                                    <div class="stamp-score">{score}%</div>
                                    <div class="stamp-verdict">{verdict}</div>
                                </div>
                            </div>
                            """, unsafe_allow_html=True)

                    with res_col2:
                        with st.container(border=True):
                            st.markdown('<div class="section-number">02 — Flagged Terms</div>', unsafe_allow_html=True)
                            
                            kw_tech = analysis.get("missing_keywords_technical", [])
                            kw_tools = analysis.get("missing_keywords_tools", [])
                            kw_soft = analysis.get("missing_keywords_soft", [])
                            
                            has_any = kw_tech or kw_tools or kw_soft
                            
                            if has_any:
                                if kw_tech:
                                    st.markdown("<p style='font-size: 0.8rem; font-weight: 600; color: var(--accent); margin: 0.5rem 0 0.25rem 0;'>Technical Skills:</p>", unsafe_allow_html=True)
                                    pills = "".join([f'<span class="flag-term flag-term-technical">{kw}</span>' for kw in kw_tech])
                                    st.markdown(f'<div class="flag-list">{pills}</div>', unsafe_allow_html=True)
                                if kw_tools:
                                    st.markdown("<p style='font-size: 0.8rem; font-weight: 600; color: var(--amber); margin: 0.5rem 0 0.25rem 0;'>Tools & Infrastructure:</p>", unsafe_allow_html=True)
                                    pills = "".join([f'<span class="flag-term flag-term-tools">{kw}</span>' for kw in kw_tools])
                                    st.markdown(f'<div class="flag-list">{pills}</div>', unsafe_allow_html=True)
                                if kw_soft:
                                    st.markdown("<p style='font-size: 0.8rem; font-weight: 600; color: var(--flag); margin: 0.5rem 0 0.25rem 0;'>Soft Skills & Methodologies:</p>", unsafe_allow_html=True)
                                    pills = "".join([f'<span class="flag-term flag-term-soft">{kw}</span>' for kw in kw_soft])
                                    st.markdown(f'<div class="flag-list">{pills}</div>', unsafe_allow_html=True)
                            else:
                                st.markdown(
                                    "<p style='font-size: 0.85rem; color: var(--accent); font-weight: 500;'>No material gaps found against the target role's requirements.</p>",
                                    unsafe_allow_html=True
                                )

                    # ---------------- Skill Roadmap Generator ----------------
                    if skill_roadmaps:
                        st.markdown("<div style='margin-top: 1.5rem;'></div>", unsafe_allow_html=True)
                        with st.container(border=True):
                            st.markdown('<div class="section-number">02.3 — Skill Gaps Roadmap</div>', unsafe_allow_html=True)
                            st.markdown("<p style='font-size: 0.85rem; color: var(--ink-muted); margin-bottom: 1.25rem;'>Actionable learning plans and projects to bridge your core skill gaps:</p>", unsafe_allow_html=True)
                            
                            for road in skill_roadmaps:
                                skill_name = road.get("skill", "")
                                steps = road.get("steps", [])
                                if skill_name and steps:
                                    steps_html = "".join([f'<li style="font-size: 0.82rem; margin-bottom: 0.4rem; color: var(--ink);"><b>Step {i+1}:</b> {step}</li>' for i, step in enumerate(steps)])
                                    st.markdown(f"""
                                    <div style="border: 1px solid var(--rule); border-radius: 4px; padding: 0.85rem; margin-bottom: 0.75rem; background-color: var(--surface);">
                                        <div style="font-family: 'IBM Plex Mono', monospace; font-size: 0.85rem; font-weight: 700; color: var(--accent); text-transform: uppercase; margin-bottom: 0.5rem; border-bottom: 1px dashed var(--rule); padding-bottom: 0.25rem;">
                                            {skill_name} Gap Closure Plan
                                        </div>
                                        <ul style="padding-left: 1.2rem; margin: 0;">
                                            {steps_html}
                                        </ul>
                                    </div>
                                    """, unsafe_allow_html=True)

                    # ---------------- Custom Interview Prep ----------------
                    st.markdown("<div style='margin-top: 1.5rem;'></div>", unsafe_allow_html=True)
                    with st.container(border=True):
                        st.markdown('<div class="section-number">02.7 — Custom Interview Prep</div>', unsafe_allow_html=True)
                        st.markdown("<p style='font-size: 0.85rem; color: var(--ink-muted); margin-bottom: 1.25rem;'>Targeted questions covering your identified keyword gaps:</p>", unsafe_allow_html=True)
                        
                        gap_sample = missing_keywords[:3] if missing_keywords else ["Technical Skills"]
                        for idx, gap in enumerate(gap_sample):
                            st.markdown(f"""
                            <div style="border-left: 2px solid var(--amber); padding-left: 10px; margin-bottom: 1rem;">
                                <span style="font-family: 'IBM Plex Mono', monospace; font-size: 0.72rem; font-weight: 700; color: var(--amber); text-transform: uppercase;">Question {idx+1}:</span>
                                <p style="font-size: 0.85rem; color: var(--ink); margin: 2px 0 0 0; font-weight: 500;">"Can you provide an example of a project where you utilized {gap} to solve a complex engineering constraint?"</p>
                                <p style="font-size: 0.78rem; color: var(--ink-muted); margin-top: 2px;"><b>Suggested Strategy:</b> Frame your response using the STAR method. Describe the situation, highlight why {gap} was critical, and mention positive results.</p>
                            </div>
                            """, unsafe_allow_html=True)

                    st.markdown("<div style='margin-top: 1.5rem;'></div>", unsafe_allow_html=True)
                    with st.container(border=True):
                        st.markdown('<div class="section-number">03 — Recommended Revisions</div>', unsafe_allow_html=True)
                        st.markdown(
                            "<p style='font-size: 0.85rem; color: var(--ink-muted); margin-bottom: 1.25rem;'>Tracked changes, original struck through and replaced:</p>",
                            unsafe_allow_html=True
                        )
                        for bullet in rewritten_bullets:
                            orig = bullet.get("original", "")
                            rewritten = bullet.get("rewritten", "")
                            impact = bullet.get("impact", "")
                            st.markdown(f"""
                            <div class="diff-block">
                                <div class="diff-line diff-remove">− {orig}</div>
                                <div class="diff-line diff-add">+ {rewritten}</div>
                                <div class="diff-impact"><b>Why:</b> {impact}</div>
                            </div>
                            """, unsafe_allow_html=True)

                    report_content = "RESUME & JOB DESCRIPTION MATCH REPORT\n"
                    report_content += f"ATS Score: {score}% ({verdict})\n\n"
                    report_content += "MISSING KEYWORDS:\n"
                    report_content += ", ".join(missing_keywords) + "\n\n"
                    report_content += "REWRITTEN BULLETS:\n"
                    for idx, bullet in enumerate(rewritten_bullets):
                        report_content += f"{idx+1}. Original: {bullet.get('original')}\n"
                        report_content += f"   Upgraded: {bullet.get('rewritten')}\n"
                        report_content += f"   Impact: {bullet.get('impact')}\n\n"

                    st.markdown("<div style='margin-top: 1.25rem;'></div>", unsafe_allow_html=True)
                    dl_col1, dl_col2 = st.columns(2)
                    with dl_col1:
                        st.download_button(
                            label="Download Report (.txt)",
                            data=report_content,
                            file_name="job_alignment_report.txt",
                            mime="text/plain",
                            key="dl_report_txt_single"
                        )
                    with dl_col2:
                        json_content = json.dumps(analysis, indent=2)
                        st.download_button(
                            label="Download Report (.json)",
                            data=json_content,
                            file_name="job_alignment_report.json",
                            mime="application/json",
                            key="dl_report_json_single"
                        )

                except Exception as ex:
                    st.error(f"Review could not be filed. Error details: {ex}")

    # Version History Comparison Panel
    if st.session_state.history:
        st.markdown("<div style='margin-top: 2rem;'></div>", unsafe_allow_html=True)
        with st.container(border=True):
            st.markdown('<div class="section-number">04 — Version Analysis Log</div>', unsafe_allow_html=True)
            st.markdown("<p style='font-size: 0.85rem; color: var(--ink-muted); margin-bottom: 1rem;'>Compare alignment metrics across consecutive runs to track ATS score improvements:</p>", unsafe_allow_html=True)
            
            cols = st.columns(len(st.session_state.history))
            for idx, run in enumerate(st.session_state.history):
                with cols[idx]:
                    st.markdown(f"""
                    <div style="border: 1px solid var(--rule); border-radius: 4px; padding: 0.75rem; text-align: center; background-color: var(--paper);">
                        <div style="font-family: 'IBM Plex Mono', monospace; font-size: 0.75rem; font-weight: 700; color: var(--ink-muted);">{run['version']}</div>
                        <div style="font-family: 'Fraunces', serif; font-size: 1.8rem; font-weight: 600; color: var(--accent); margin: 0.25rem 0;">{run['score']}%</div>
                        <div style="font-size: 0.75rem; color: var(--ink-muted);">Gaps: {run['gaps']} | Bullet Revisions: {run['bullets']}</div>
                    </div>
                    """, unsafe_allow_html=True)
            
            st.markdown("<div style='margin-top: 1rem;'></div>", unsafe_allow_html=True)
            if st.button("Clear Version Log", key="clear_log_btn_single"):
                st.session_state.history = []
                st.rerun()

# ---------------------------------------------------------------------------
# Tab 2: Multi-Resume Comparison
# ---------------------------------------------------------------------------
with tab_multi:
    st.markdown('<div class="section-number">Multi-Resume Comparison</div>', unsafe_allow_html=True)
    st.markdown("<p style='font-size: 0.9rem; color: var(--ink-muted); margin-bottom: 1.5rem;'>Upload 2 to 3 different versions of your resume to compare their ATS match scores and keyword density against the job description.</p>", unsafe_allow_html=True)
    
    # Check if target job description is loaded
    if not st.session_state.jd_text_state.strip():
        st.warning("Please upload/paste a Job Description in the 'Single Resume Review' tab or below.")
        compare_jd_input = st.text_area(
            "Target Job Description",
            value=st.session_state.jd_text_state,
            height=150,
            placeholder="Paste the target job description here...",
            key="compare_jd_text_area"
        )
        st.session_state.jd_text_state = compare_jd_input
    else:
        st.info("Using the target job description loaded from your session state.")
        
    uploaded_resumes = st.file_uploader(
        "Upload 2-3 Resume Versions",
        type=["pdf", "txt"],
        accept_multiple_files=True,
        key="multi_resumes_uploader"
    )
    
    if uploaded_resumes:
        if len(uploaded_resumes) < 2:
            st.warning("Please upload at least 2 resumes to compare.")
        elif len(uploaded_resumes) > 5:
            st.error("You can upload a maximum of 5 resumes for comparison.")
        else:
            st.markdown("<div style='max-width: 260px; margin: 1rem 0;'>", unsafe_allow_html=True)
            run_comparison = st.button("Compare Resume Versions", key="run_multi_comparison")
            st.markdown("</div>", unsafe_allow_html=True)
            
            if run_comparison:
                with st.spinner("Analyzing all uploaded resumes side-by-side..."):
                    results = []
                    for idx, resume_file in enumerate(uploaded_resumes):
                        try:
                            file_bytes = resume_file.read()
                            if resume_file.name.endswith(".pdf"):
                                text = extract_text_from_pdf(file_bytes)
                            else:
                                text = file_bytes.decode("utf-8", errors="ignore")
                                
                            analysis = analyze_match(text, st.session_state.jd_text_state)
                            results.append({
                                "name": resume_file.name,
                                "score": int(analysis.get("match_score", 0)),
                                "tech_gaps": analysis.get("missing_keywords_technical", []),
                                "tools_gaps": analysis.get("missing_keywords_tools", []),
                                "soft_gaps": analysis.get("missing_keywords_soft", []),
                                "bullets_count": len(analysis.get("rewritten_bullets", [])),
                                "analysis": analysis
                            })
                        except Exception as ex:
                            st.error(f"Failed to analyze {resume_file.name}: {ex}")
                    
                    if results:
                        st.markdown("<div style='margin-top: 2rem;'></div>", unsafe_allow_html=True)
                        st.markdown("<h3 style='font-family: Fraunces, serif; text-align: center; margin-bottom: 2rem;'>Side-by-Side Comparison Matrix</h3>", unsafe_allow_html=True)
                        
                        cols = st.columns(len(results))
                        for i, res in enumerate(results):
                            with cols[i]:
                                if res["score"] >= 80:
                                    sc_color, verdict = "#1F4D3A", "Strong"
                                elif res["score"] >= 50:
                                    sc_color, verdict = "#9C6B14", "Partial"
                                else:
                                    sc_color, verdict = "#A13327", "Needs Revision"
                                    
                                st.markdown(f"""
                                <div style="border: 2px solid var(--rule); padding: 1.25rem; border-radius: 4px; background-color: var(--surface); height: 100%;">
                                    <div style="font-family: 'IBM Plex Mono', monospace; font-size: 0.72rem; font-weight: 700; color: var(--ink-muted); text-transform: uppercase; border-bottom: 1px solid var(--rule); padding-bottom: 0.5rem; margin-bottom: 1rem; text-overflow: ellipsis; overflow: hidden; white-space: nowrap;">
                                        {res['name']}
                                    </div>
                                    <div class="stamp-wrap" style="padding: 0.5rem 0;">
                                        <div class="stamp" style="--stamp-color: {sc_color}; width: 120px; height: 120px;">
                                            <div class="stamp-score" style="font-size: 1.8rem;">{res['score']}%</div>
                                            <div class="stamp-verdict" style="font-size: 0.55rem;">{verdict}</div>
                                        </div>
                                    </div>
                                    <div style="margin-top: 1rem;">
                                        <p style="font-size: 0.8rem; margin: 0.25rem 0;"><b>Technical Gaps:</b> {len(res['tech_gaps'])}</p>
                                        <p style="font-size: 0.8rem; margin: 0.25rem 0;"><b>Tools Gaps:</b> {len(res['tools_gaps'])}</p>
                                        <p style="font-size: 0.8rem; margin: 0.25rem 0;"><b>Bullet Improvements:</b> {res['bullets_count']}</p>
                                    </div>
                                    <div style="margin-top: 1rem; border-top: 1px dashed var(--rule); padding-top: 0.5rem;">
                                        <p style="font-size: 0.75rem; font-weight: 600; margin-bottom: 0.25rem; color: var(--ink-muted);">Key Missing Skills:</p>
                                        <div style="font-family: monospace; font-size: 0.75rem; color: var(--flag);">
                                            {", ".join(res['tech_gaps'][:4]) if res['tech_gaps'] else "None"}
                                        </div>
                                    </div>
                                </div>
                                """, unsafe_allow_html=True)

# ---------------------------------------------------------------------------
# Tab 3: Cover Letter Workspace
# ---------------------------------------------------------------------------
with tab_cover:
    st.markdown('<div class="section-number">Cover Letter Generator</div>', unsafe_allow_html=True)
    st.markdown("<p style='font-size: 0.9rem; color: var(--ink-muted); margin-bottom: 1.5rem;'>Generate a professionally written, tailored cover letter aligning your resume and job description inputs using Gemini.</p>", unsafe_allow_html=True)
    
    if not st.session_state.resume_text_state.strip() or not st.session_state.jd_text_state.strip():
        st.warning("Please upload/paste both your Resume and Job Description in the 'Single Resume Review' tab to generate a cover letter.")
    else:
        st.markdown("<div style='max-width: 260px; margin: 1rem 0;'>", unsafe_allow_html=True)
        run_cover_letter_gen = st.button("Generate Cover Letter", key="run_cover_letter_gen")
        st.markdown("</div>", unsafe_allow_html=True)
        
        if run_cover_letter_gen:
            with st.spinner("Analyzing inputs and drafting a customized cover letter..."):
                try:
                    cl_text = generate_cover_letter(st.session_state.resume_text_state, st.session_state.jd_text_state)
                    st.session_state.cover_letter = cl_text
                    st.success("Cover letter drafted successfully!")
                except Exception as e:
                    st.error(f"Failed to generate cover letter: {e}")
                    
        if st.session_state.cover_letter:
            st.markdown("<div style='margin-top: 1.5rem;'></div>", unsafe_allow_html=True)
            
            # Text area allowing edits
            edited_cl = st.text_area(
                "Customize Cover Letter Draft",
                value=st.session_state.cover_letter,
                height=450,
                key="cl_text_area"
            )
            st.session_state.cover_letter = edited_cl
            
            col_dl, col_spacer = st.columns([1, 3])
            with col_dl:
                st.download_button(
                    label="Download Draft (.txt)",
                    data=st.session_state.cover_letter,
                    file_name="tailored_cover_letter.txt",
                    mime="text/plain",
                    key="dl_cover_letter_txt"
                )
            
            st.markdown("<p style='font-size: 0.8rem; font-weight: 600; color: var(--ink-muted); margin-top: 1.5rem; margin-bottom: 0.5rem;'>Raw Copy Preview:</p>", unsafe_allow_html=True)
            st.code(st.session_state.cover_letter, language="text")