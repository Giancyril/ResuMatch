import streamlit as st
import json
from gemini_service import analyze_match

# Page Configuration
st.set_page_config(
    page_title="AI Resume & Job Match Analyzer",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom Premium Styling
st.markdown("""
<style>
    /* Gradient Background and Theme Override */
    .stApp {
        background: linear-gradient(135deg, #0d0e15 0%, #151624 100%);
        color: #e2e8f0;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }
    
    /* Title Styling */
    .title-container {
        text-align: center;
        padding: 2.5rem 0 1.5rem 0;
    }
    .main-title {
        font-size: 3rem;
        font-weight: 800;
        letter-spacing: -0.05em;
        background: linear-gradient(to right, #6366f1, #a855f7, #ec4899);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    .subtitle {
        font-size: 1.1rem;
        color: #94a3b8;
        font-weight: 400;
        max-width: 600px;
        margin: 0 auto;
        line-height: 1.5;
    }
    
    /* Custom Card Design */
    .premium-card {
        background: rgba(22, 23, 42, 0.6);
        border: 1px solid rgba(255, 255, 255, 0.05);
        border-radius: 18px;
        padding: 1.75rem;
        backdrop-filter: blur(16px);
        box-shadow: 0 10px 30px -15px rgba(0, 0, 0, 0.5);
        margin-bottom: 1.5rem;
    }
    
    /* Missing Skill Pills */
    .skill-badge {
        display: inline-flex;
        align-items: center;
        background: rgba(236, 72, 153, 0.08);
        border: 1px solid rgba(236, 72, 153, 0.25);
        color: #fbcfe8;
        border-radius: 9999px;
        padding: 6px 14px;
        font-size: 0.75rem;
        margin: 4px;
        font-weight: 700;
        letter-spacing: 0.03em;
        transition: all 0.2s ease;
    }
    .skill-badge:hover {
        background: rgba(236, 72, 153, 0.15);
        border-color: rgba(236, 72, 153, 0.4);
    }
    
    /* Score display elements */
    .score-circle {
        font-size: 4rem;
        font-weight: 900;
        background: linear-gradient(135deg, #a855f7 0%, #6366f1 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        line-height: 1;
        margin-top: 0.5rem;
    }
    .score-label {
        font-size: 0.8rem;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.15em;
        font-weight: 700;
        text-align: center;
    }
    
    /* Bullet list tables */
    .bullet-row {
        border-left: 4px solid #6366f1;
        background: rgba(99, 102, 241, 0.03);
        border-radius: 0 16px 16px 0;
        padding: 1.25rem;
        margin-bottom: 1.25rem;
        border-top: 1px solid rgba(255, 255, 255, 0.02);
        border-right: 1px solid rgba(255, 255, 255, 0.02);
        border-bottom: 1px solid rgba(255, 255, 255, 0.02);
    }
    .bullet-header {
        font-size: 0.75rem;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        margin-bottom: 0.5rem;
    }
    .bullet-orig-header { color: #f43f5e; }
    .bullet-new-header { color: #10b981; }
    
    /* Style default Streamlit buttons */
    div.stButton > button {
        background: linear-gradient(135deg, #6366f1 0%, #a855f7 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.6rem 2rem !important;
        font-weight: 700 !important;
        box-shadow: 0 4px 15px rgba(99, 102, 241, 0.3) !important;
        transition: all 0.2s ease-in-out !important;
        width: 100%;
    }
    div.stButton > button:hover {
        transform: translateY(-1px) !important;
        box-shadow: 0 6px 20px rgba(99, 102, 241, 0.45) !important;
    }
</style>
""", unsafe_allow_html=True)

# App Header
st.markdown("""
<div class="title-container">
    <h1 class="main-title">ResuMatch</h1>
    <p class="subtitle">Tailor your resume, identify missing technical keyword gaps, and generate high-impact bullet points utilizing Google Gemini.</p>
</div>
""", unsafe_allow_html=True)

# Input Columns
col1, col2 = st.columns(2)

with col1:
    st.markdown('<div class="premium-card">', unsafe_allow_html=True)
    st.subheader("📝 Paste Your Resume")
    resume_input = st.text_area(
        "Paste the raw text of your current resume here:",
        height=320,
        placeholder="John Doe\nSoftware Engineer...\n- Built API endpoints using Node.js...\n- Developed frontend components...",
        label_visibility="collapsed"
    )
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="premium-card">', unsafe_allow_html=True)
    st.subheader("🎯 Paste Job Description")
    jd_input = st.text_area(
        "Paste the target job description here:",
        height=320,
        placeholder="Requirements:\n- 3+ years experience with React & Python\n- Solid understanding of SQL and CI/CD pipelines\n- Experience building scalable cloud apps...",
        label_visibility="collapsed"
    )
    st.markdown('</div>', unsafe_allow_html=True)

# Action Row
st.markdown("<div style='max-width: 300px; margin: 1rem auto;'>", unsafe_allow_html=True)
analyze_clicked = st.button("🚀 Analyze Alignment")
st.markdown("</div>", unsafe_allow_html=True)

# Processing Analysis
if analyze_clicked:
    if not resume_input.strip() or not jd_input.strip():
        st.warning("⚠️ Please provide both your resume and the job description to run the alignment analysis.")
    else:
        with st.spinner("⚡ Gemini is analyzing keyword densities and crafting custom resume modifications..."):
            try:
                # Call Gemini Service
                analysis = analyze_match(resume_input, jd_input)
                
                # Results Section
                st.markdown("---")
                st.markdown("<h2 style='text-align: center; margin-bottom: 2rem;'>📊 Analysis Alignment Report</h2>", unsafe_allow_html=True)
                
                res_col1, res_col2 = st.columns([1, 2])
                
                with res_col1:
                    st.markdown('<div class="premium-card" style="text-align: center; display: flex; flex-direction: column; justify-content: center; height: 100%;">', unsafe_allow_html=True)
                    st.markdown('<div class="score-label">ATS Compatibility</div>', unsafe_allow_html=True)
                    score = int(analysis.get("match_score", 0))
                    st.markdown(f'<div class="score-circle">{score}%</div>', unsafe_allow_html=True)
                    st.markdown('<div style="margin-top: 1rem;"></div>', unsafe_allow_html=True)
                    st.progress(score / 100.0)
                    st.markdown('</div>', unsafe_allow_html=True)
                    
                with res_col2:
                    st.markdown('<div class="premium-card" style="height: 100%;">', unsafe_allow_html=True)
                    st.subheader("❌ Missing Keywords & Skills")
                    st.markdown("<p style='font-size: 0.85rem; color: #94a3b8; margin-bottom: 1rem;'>Add these skills to your resume to pass automated ATS filters:</p>", unsafe_allow_html=True)
                    
                    missing_keywords = analysis.get("missing_keywords", [])
                    if missing_keywords:
                        pills_html = "".join([f'<span class="skill-badge">{kw}</span>' for kw in missing_keywords])
                        st.markdown(f'<div>{pills_html}</div>', unsafe_allow_html=True)
                    else:
                        st.success("🎉 Amazing! No major missing skills identified against the job description requirements.")
                    st.markdown('</div>', unsafe_allow_html=True)
                
                # Tailored Bullet Points Section
                st.markdown("<div style='margin-top: 2rem;'></div>", unsafe_allow_html=True)
                st.markdown('<div class="premium-card">', unsafe_allow_html=True)
                st.subheader("💡 Tailored Bullet Point Upgrades")
                st.markdown("<p style='font-size: 0.85rem; color: #94a3b8; margin-bottom: 1.5rem;'>Replace generic resume claims with these action-oriented, metrics-driven bullets tailored to this role's keywords:</p>", unsafe_allow_html=True)
                
                rewritten_bullets = analysis.get("rewritten_bullets", [])
                for idx, bullet in enumerate(rewritten_bullets):
                    orig = bullet.get("original", "")
                    rewritten = bullet.get("rewritten", "")
                    impact = bullet.get("impact", "")
                    
                    st.markdown(f"""
                    <div class="bullet-row">
                        <div style="display: grid; grid-template-columns: 1fr; gap: 10px;">
                            <div>
                                <span class="bullet-header bullet-orig-header">🔴 ORIGINAL:</span>
                                <p style="font-size: 0.85rem; color: #cbd5e1; font-style: italic; margin-top: 2px;">"{orig}"</p>
                            </div>
                            <div style="margin-top: 8px;">
                                <span class="bullet-header bullet-new-header">🟢 UPGRADED:</span>
                                <p style="font-size: 0.9rem; color: #ffffff; font-weight: 600; margin-top: 2px;">"{rewritten}"</p>
                            </div>
                            <div style="margin-top: 6px; border-top: 1px dashed rgba(255,255,255,0.05); padding-top: 6px;">
                                <span style="font-size: 0.75rem; font-weight: 700; color: #818cf8; text-transform: uppercase;">ATS Impact:</span>
                                <span style="font-size: 0.8rem; color: #94a3b8;">{impact}</span>
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
                
                # Report Exporter
                st.markdown("<div style='margin-top: 1.5rem;'></div>", unsafe_allow_html=True)
                report_content = f"RESUME & JOB DESCRIPTION MATCH REPORT\n"
                report_content += f"ATS Score: {score}%\n\n"
                report_content += "MISSING KEYWORDS:\n"
                report_content += ", ".join(missing_keywords) + "\n\n"
                report_content += "REWRITTEN BULLETS:\n"
                for idx, bullet in enumerate(rewritten_bullets):
                    report_content += f"{idx+1}. Original: {bullet.get('original')}\n"
                    report_content += f"   Upgraded: {bullet.get('rewritten')}\n"
                    report_content += f"   Impact: {bullet.get('impact')}\n\n"
                    
                st.download_button(
                    label="📥 Download Match Report (.txt)",
                    data=report_content,
                    file_name="job_alignment_report.txt",
                    mime="text/plain"
                )
                
            except Exception as ex:
                st.error(f"❌ Failed to complete match analysis. Error details: {ex}")
