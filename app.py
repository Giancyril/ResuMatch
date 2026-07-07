import streamlit as st
import json
from gemini_service import analyze_match

# Page Configuration
st.set_page_config(
    page_title="ResuMatch — Resume Review Report",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initialize Session State Version Comparison History
if "history" not in st.session_state:
    st.session_state.history = []

# ---------------------------------------------------------------------------
# Design system: "Document Review Report"
# A resume and job description are treated as exhibits in a formal review.
# Missing keywords are flagged like proofreader's marks; rewritten bullets
# are shown as track-changes diffs; the match score is an ink stamp verdict.
# ---------------------------------------------------------------------------
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Fraunces:ital,wght@0,500;0,600;1,500&family=IBM+Plex+Sans:wght@400;500;600&family=IBM+Plex+Mono:wght@400;500;600&display=swap');

    :root {
        --paper: #F7F4EE;
        --surface: #FFFFFF;
        --ink: #201E1B;
        --ink-muted: #6B6459;
        --rule: #DED7C9;
        --accent: #1F4D3A;
        --accent-soft: rgba(31, 77, 58, 0.08);
        --flag: #A13327;
        --flag-soft: rgba(161, 51, 39, 0.07);
        --amber: #9C6B14;
        --amber-soft: rgba(156, 107, 20, 0.08);
        
        /* Global Streamlit Focus Custom Property Overrides */
        --primary-color: #1F4D3A !important;
        --st-color-primary: #1F4D3A !important;
        --st-color-border-focus: #1F4D3A !important;
    }

    header {visibility: hidden;}
    footer {visibility: hidden;}
    #MainMenu {visibility: hidden;}

    .stApp {
        background-color: var(--paper) !important;
        color: var(--ink);
        font-family: 'IBM Plex Sans', -apple-system, sans-serif;
    }

    ::-webkit-scrollbar { width: 8px; }
    ::-webkit-scrollbar-track { background: var(--paper); }
    ::-webkit-scrollbar-thumb { background: var(--rule); border-radius: 4px; }
    ::-webkit-scrollbar-thumb:hover { background: var(--ink-muted); }

    /* ---------------- Letterhead ---------------- */
    .letterhead {
        text-align: center;
        padding: 2.75rem 0 1.5rem 0;
        border-bottom: 1px solid var(--rule);
        margin-bottom: 2.5rem;
    }
    .eyebrow {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.7rem;
        font-weight: 500;
        letter-spacing: 0.28em;
        text-transform: uppercase;
        color: var(--ink-muted);
        margin-bottom: 0.9rem;
    }
    .masthead {
        font-family: 'Fraunces', serif;
        font-size: 3.1rem;
        font-weight: 600;
        color: var(--ink);
        letter-spacing: -0.02em;
        margin-bottom: 0.6rem;
    }
    .masthead em {
        color: var(--accent);
        font-style: italic;
        font-weight: 500;
    }
    .deck {
        font-family: 'Fraunces', serif;
        font-style: italic;
        font-size: 1.05rem;
        color: var(--ink-muted);
        max-width: 560px;
        margin: 0 auto;
        line-height: 1.65;
        font-weight: 500;
    }

    /* ---------------- Exhibit cards (inputs) ---------------- */
    .exhibit-label {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.7rem;
        font-weight: 600;
        letter-spacing: 0.18em;
        text-transform: uppercase;
        color: var(--ink-muted);
        margin-bottom: 0.6rem;
        display: block;
    }

    /* Change the red container border to none */
    div[data-testid="stVerticalBlockBorderWrapper"],
    div[data-testid="stVerticalBlockBorderWrapper"] > div {
        border: none !important;
        background-color: var(--surface) !important;
        border-radius: 2px !important;
        box-shadow: 0 1px 0 var(--rule), 0 8px 24px -18px rgba(32, 30, 27, 0.35) !important;
    }

    /* Style the Text Area Wrapper and Inner Input */
    div[data-baseweb="textarea"] {
        border: none !important;
        background: transparent !important;
    }
    div[data-baseweb="textarea"] > div {
        background-color: var(--surface) !important;
        border: 1px solid var(--rule) !important;
        border-radius: 4px !important;
        transition: all 0.15s ease-in-out !important;
    }
    div[data-baseweb="textarea"]:focus-within > div,
    div[data-baseweb="textarea"] > div:focus-within,
    div[data-baseweb="textarea"] div:focus-within,
    div[data-baseweb="textarea"] *:focus,
    div[data-baseweb="textarea"] *:focus-within,
    textarea:focus {
        border-color: var(--accent) !important;
        box-shadow: 0 0 0 1px var(--accent) !important;
        outline: none !important;
    }
    textarea {
        background-color: var(--surface) !important;
        color: #000000 !important;
        font-family: 'IBM Plex Mono', monospace !important;
        font-size: 0.85rem !important;
        line-height: 1.6 !important;
    }
    textarea::placeholder { color: #B7AF9F !important; }

    /* ---------------- Button ---------------- */
    div.stButton > button {
        background: var(--accent) !important;
        color: var(--paper) !important;
        border: none !important;
        border-radius: 2px !important;
        padding: 0.8rem 2rem !important;
        font-family: 'IBM Plex Mono', monospace !important;
        font-weight: 600 !important;
        font-size: 0.78rem !important;
        letter-spacing: 0.14em;
        text-transform: uppercase;
        transition: background 0.15s ease-in-out !important;
        width: 100%;
    }
    div.stButton > button:hover {
        background: #163A2B !important;
    }

    /* ---------------- Report section headers ---------------- */
    .report-heading {
        text-align: center;
        margin: 1rem 0 2rem 0;
    }
    .report-kicker {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.7rem;
        letter-spacing: 0.28em;
        text-transform: uppercase;
        color: var(--ink-muted);
    }
    .report-title {
        font-family: 'Fraunces', serif;
        font-size: 1.9rem;
        font-weight: 600;
        color: var(--ink);
        margin-top: 0.4rem;
    }
    .section-number {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.72rem;
        font-weight: 600;
        letter-spacing: 0.16em;
        color: var(--accent);
        text-transform: uppercase;
        margin-bottom: 0.5rem;
    }

    /* ---------------- Ink stamp (score) ---------------- */
    .stamp-wrap {
        display: flex;
        align-items: center;
        justify-content: center;
        height: 100%;
        padding: 1rem 0;
    }
    .stamp {
        width: 168px;
        height: 168px;
        border-radius: 50%;
        border: 3px double var(--stamp-color, var(--accent));
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        transform: rotate(-7deg);
        color: var(--stamp-color, var(--accent));
        font-family: 'IBM Plex Mono', monospace;
    }
    .stamp-score {
        font-size: 2.6rem;
        font-weight: 600;
        line-height: 1;
    }
    .stamp-verdict {
        font-size: 0.62rem;
        font-weight: 600;
        letter-spacing: 0.14em;
        text-transform: uppercase;
        margin-top: 0.35rem;
        text-align: center;
        padding: 0 0.5rem;
    }

    /* ---------------- Flagged terms ---------------- */
    .flag-list {
        display: flex;
        flex-wrap: wrap;
        gap: 0.5rem 1.1rem;
        margin-top: 0.5rem;
    }
    .flag-term {
        font-family: 'IBM Plex Mono', monospace;
        font-size: 0.82rem;
        font-weight: 500;
        color: var(--flag);
        border-bottom: 1px dashed var(--flag);
        padding-bottom: 1px;
    }
    .flag-term::before { content: "▸ "; }
    .flag-term-technical { color: var(--accent) !important; border-color: var(--accent) !important; }
    .flag-term-technical::before { content: "▪ " !important; }
    .flag-term-tools { color: var(--amber) !important; border-color: var(--amber) !important; }
    .flag-term-tools::before { content: "▪ " !important; }
    .flag-term-soft { color: var(--flag) !important; border-color: var(--flag) !important; }
    .flag-term-soft::before { content: "▪ " !important; }

    /* ---------------- Diff rows (bullet revisions) ---------------- */
    .diff-block {
        border: 1px solid var(--rule);
        border-radius: 2px;
        margin-bottom: 1rem;
        overflow: hidden;
        font-family: 'IBM Plex Mono', monospace;
    }
    .diff-line {
        padding: 0.7rem 1rem;
        font-size: 0.82rem;
        line-height: 1.55;
        border-left: 3px solid transparent;
    }
    .diff-remove {
        background: var(--flag-soft);
        border-left-color: var(--flag);
        color: #7A241B;
        text-decoration: line-through;
        text-decoration-color: rgba(161, 51, 39, 0.45);
    }
    .diff-add {
        background: var(--accent-soft);
        border-left-color: var(--accent);
        color: var(--accent);
        font-weight: 500;
    }
    .diff-impact {
        padding: 0.55rem 1rem;
        font-size: 0.72rem;
        color: var(--ink-muted);
        background: var(--surface);
        border-top: 1px dashed var(--rule);
        font-family: 'IBM Plex Sans', sans-serif;
    }
    .diff-impact b { color: var(--ink); font-weight: 600; }

    div[data-testid="stDownloadButton"] > button {
        background: var(--surface) !important;
        color: var(--accent) !important;
        border: 1px solid var(--accent) !important;
        border-radius: 2px !important;
        font-family: 'IBM Plex Mono', monospace !important;
        font-size: 0.75rem !important;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        font-weight: 600 !important;
    }
</style>
""", unsafe_allow_html=True)

# ---------------- Letterhead ----------------
st.markdown("""
<div class="letterhead">
    <div class="eyebrow">Document Review Report</div>
    <div class="masthead">Resu<em>Match</em></div>
    <div class="deck">Submit your resume and a target role as exhibits. Gemini reviews the pairing and returns a scored alignment report with flagged gaps and recommended revisions.</div>
</div>
""", unsafe_allow_html=True)

# ---------------- Exhibits (inputs) ----------------
col1, col2 = st.columns(2)

with col1:
    with st.container(border=True):
        st.markdown('<span class="exhibit-label">Exhibit A — Resume</span>', unsafe_allow_html=True)
        
        # File uploader option for resume
        uploaded_resume = st.file_uploader(
            "Upload Resume (PDF or TXT)",
            type=["pdf", "txt"],
            key="resume_uploader",
            label_visibility="visible"
        )
        
        resume_default = ""
        if uploaded_resume is not None:
            try:
                file_bytes = uploaded_resume.read()
                if uploaded_resume.name.endswith(".pdf"):
                    from utils import extract_text_from_pdf
                    resume_default = extract_text_from_pdf(file_bytes)
                else:
                    resume_default = file_bytes.decode("utf-8", errors="ignore")
                st.markdown(f'<p style="font-size: 0.72rem; color: var(--accent); font-family: monospace; margin: -5px 0 10px 0;">✔ Loaded {len(resume_default)} chars. You can edit below.</p>', unsafe_allow_html=True)
            except Exception as ex:
                st.error(f"Error loading resume file: {ex}")
        
        resume_input = st.text_area(
            "Resume Plain Text",
            value=resume_default,
            height=260,
            placeholder="Or paste your resume text here...",
            label_visibility="collapsed"
        )

with col2:
    with st.container(border=True):
        st.markdown('<span class="exhibit-label">Exhibit B — Target Role</span>', unsafe_allow_html=True)
        
        # File uploader option for job description
        uploaded_jd = st.file_uploader(
            "Upload Job Description (PDF or TXT)",
            type=["pdf", "txt"],
            key="jd_uploader",
            label_visibility="visible"
        )
        
        jd_default = ""
        if uploaded_jd is not None:
            try:
                file_bytes = uploaded_jd.read()
                if uploaded_jd.name.endswith(".pdf"):
                    from utils import extract_text_from_pdf
                    jd_default = extract_text_from_pdf(file_bytes)
                else:
                    jd_default = file_bytes.decode("utf-8", errors="ignore")
                st.markdown(f'<p style="font-size: 0.72rem; color: var(--accent); font-family: monospace; margin: -5px 0 10px 0;">✔ Loaded {len(jd_default)} chars. You can edit below.</p>', unsafe_allow_html=True)
            except Exception as ex:
                st.error(f"Error loading job description file: {ex}")
        
        jd_input = st.text_area(
            "Job Description Plain Text",
            value=jd_default,
            height=260,
            placeholder="Or paste the target job description here...",
            label_visibility="collapsed"
        )

st.markdown("<div style='max-width: 260px; margin: 1.75rem auto 0.5rem auto;'>", unsafe_allow_html=True)
analyze_clicked = st.button("Review Alignment")
st.markdown("</div>", unsafe_allow_html=True)

# ---------------- Analysis ----------------
if analyze_clicked:
    if not resume_input.strip() or not jd_input.strip():
        st.warning("Both exhibits are required before a review can be filed. Paste your resume and the job description above.")
    else:
        with st.spinner("Filing exhibits and cross-referencing keyword density…"):
            try:
                analysis = analyze_match(resume_input, jd_input)
                score = int(analysis.get("match_score", 0))
                
                # Append analysis results to history logs for comparison
                st.session_state.history.append({
                    "version": f"v{len(st.session_state.history) + 1}",
                    "score": score,
                    "gaps": len(analysis.get("missing_keywords", [])),
                    "bullets": len(analysis.get("rewritten_bullets", []))
                })
                missing_keywords = analysis.get("missing_keywords", [])
                rewritten_bullets = analysis.get("rewritten_bullets", [])

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
                        mime="text/plain"
                    )
                with dl_col2:
                    json_content = json.dumps(analysis, indent=2)
                    st.download_button(
                        label="Download Report (.json)",
                        data=json_content,
                        file_name="job_alignment_report.json",
                        mime="application/json"
                    )

            except Exception as ex:
                st.error(f"Review could not be filed. Error details: {ex}")

# ----------------- Version History Comparison Panel -----------------
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
        if st.button("Clear Version Log", key="clear_log_btn"):
            st.session_state.history = []
            st.rerun()