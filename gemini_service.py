import os
import json
import warnings
# Suppress the generativeai deprecation warning to keep clean console logs
warnings.filterwarnings("ignore", category=FutureWarning, module="google.generativeai")
import google.generativeai as genai
from dotenv import load_dotenv

# Load API key
load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

if api_key:
    genai.configure(api_key=api_key)

def analyze_match(resume_text, job_desc):
    """
    Compare resume and job description using Gemini.
    Returns parsed JSON dictionary with match details.
    """
    if not api_key:
        raise ValueError("GEMINI_API_KEY is not set. Please check your .env file.")

    if not resume_text.strip() or not job_desc.strip():
        raise ValueError("Resume and Job Description text fields must not be empty.")

    prompt = f"""You are a professional hiring manager and ATS optimization expert.
Analyze the following resume and job description. Evaluate their alignment and return a structured analysis.

Return ONLY valid JSON matching this schema:
{{
  "match_score": int (a percentage score between 0 and 100),
  "missing_keywords_technical": [list of core programming languages, frameworks, libraries, or key technical skills in the job description but not in the resume],
  "missing_keywords_tools": [list of platforms, databases, cloud providers, developer tools, or infrastructure tools in the job description but not in the resume],
  "missing_keywords_soft": [list of soft skills, team collaboration keywords, or methodologies like Agile/Scrum in the job description but not in the resume],
  "rewritten_bullets": [
    {{
      "original": "A representative weak/generic bullet point from the resume",
      "rewritten": "The rewritten bullet point incorporating keywords and strong action verbs tailored to the job description",
      "impact": "Explanation of why this rewrite makes the resume stronger for this job"
    }}
  ] (provide 3 to 5 key bullet points),
  "skill_roadmaps": [
    {{
      "skill": "Name of the missing technical/tool skill",
      "steps": ["Step 1 to close this gap (e.g., specific online course topic, certification)", "Step 2 (e.g., specific project idea to add to the resume)", "Step 3 (e.g., specific tool usage in portfolio)"]
    }}
  ] (provide roadmaps for the top 3 to 5 missing skills from missing_keywords_technical and missing_keywords_tools)
}}

Resume:
{resume_text}

Job Description:
{job_desc}
"""

    try:
        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content(
            prompt,
            generation_config={"response_mime_type": "application/json"}
        )
        
        # Parse the JSON response
        result_text = response.text.strip()
        data = json.loads(result_text)
        
        # Populate backward compatibility keys
        if "missing_keywords" not in data:
            data["missing_keywords"] = (
                data.get("missing_keywords_technical", []) +
                data.get("missing_keywords_tools", []) +
                data.get("missing_keywords_soft", [])
            )
            
        return data
    except Exception as e:
        print(f"Error during Gemini match analysis: {e}")
        raise e

def generate_cover_letter(resume_text, job_desc):
    """
    Generate a tailored cover letter using the resume and job description.
    """
    if not api_key:
        raise ValueError("GEMINI_API_KEY is not set. Please check your .env file.")

    if not resume_text.strip() or not job_desc.strip():
        raise ValueError("Resume and Job Description text fields must not be empty.")

    prompt = f"""You are a professional career coach and resume writer.
Write a highly tailored, compelling, and professional cover letter based on the following resume and job description.
The cover letter should match the tone and keywords of the job description, highlight relevant experiences from the resume that align with the requirements, and be structured with:
1. Contact Information placeholder / Date
2. Formal Salutation
3. Engaging Opening Paragraph
4. 2-3 body paragraphs demonstrating strong alignment, including metrics and impact where possible
5. A polite and proactive closing call to action
6. Professional Sign-off

Return ONLY the plain text of the cover letter. Do not include markdown formatting or tags like ``` or ```markdown at the beginning or end of your response.

Resume:
{resume_text}

Job Description:
{job_desc}
"""
    try:
        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Error during Gemini cover letter generation: {e}")
        raise e

def optimize_linkedin_profile(resume_text, job_desc, rewritten_bullets_list):
    """
    Optimize LinkedIn profile sections based on resume, job description, and tailored bullets.
    Returns a dict with 'about' and 'experience' sections formatted for LinkedIn.
    """
    if not api_key:
        raise ValueError("GEMINI_API_KEY is not set. Please check your .env file.")

    bullets_json = json.dumps(rewritten_bullets_list, indent=2)

    prompt = f"""You are a professional LinkedIn branding expert.
Optimize the following user's LinkedIn profile sections based on their Resume, target Job Description, and their upgraded resume bullet points.

Create two distinct sections tailored for LinkedIn's unique format, character limits, and conventions:
1. LinkedIn "About" (Summary) Section: A compelling, story-driven, first-person summary. Integrate key skills, achievements, and target keywords. Keep it under 2,000 characters.
2. LinkedIn "Experience" Section: Take the upgraded bullet points and reformat them into high-impact LinkedIn experience descriptions (using first-person or action-oriented phrases, clean formatting, and clear metric/impact callouts suitable for a professional online profile).

Return ONLY valid JSON matching this schema:
{{
  "about": "Compelling LinkedIn About section draft...",
  "experience": "Upgraded LinkedIn Experience section bullets/text..."
}}

Resume:
{resume_text}

Job Description:
{job_desc}

Upgraded Bullets:
{bullets_json}
"""
    try:
        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content(
            prompt,
            generation_config={"response_mime_type": "application/json"}
        )
        return json.loads(response.text.strip())
    except Exception as e:
        print(f"Error during LinkedIn profile optimization: {e}")
        raise e

def estimate_salary(job_title, skills_list, job_desc):
    """
    Estimate compensation range for a role based on job title, extracted skills, and JD context.
    Returns a dict with salary range, currency, and context notes.
    """
    if not api_key:
        raise ValueError("GEMINI_API_KEY is not set. Please check your .env file.")

    skills_str = ", ".join(skills_list) if skills_list else "general skills"

    prompt = f"""You are a compensation and labor market analyst with access to salary benchmarking data from sources like Levels.fyi, Glassdoor, LinkedIn Salary, and the US Bureau of Labor Statistics.

Estimate a realistic salary compensation range for the following role based on the job title, required skills, and job description context.

Provide breakdowns by:
- Entry-level / Junior (0-2 years)
- Mid-level (3-5 years)
- Senior-level (5+ years)

Also include notes on location variance, remote premium, and any skills that significantly impact compensation.

Return ONLY valid JSON matching this schema:
{{
  "currency": "USD",
  "job_title": "Detected or inferred job title",
  "entry_level": {{"min": int, "max": int}},
  "mid_level": {{"min": int, "max": int}},
  "senior_level": {{"min": int, "max": int}},
  "high_value_skills": ["skill1", "skill2"],
  "location_note": "Brief note on how location affects salary (e.g. SF/NYC premium)",
  "source_note": "Brief note on data basis (e.g. based on market benchmarks from Levels.fyi, Glassdoor, BLS)"
}}

Job Title: {job_title}
Key Skills: {skills_str}

Job Description:
{job_desc}
"""
    try:
        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content(
            prompt,
            generation_config={"response_mime_type": "application/json"}
        )
        return json.loads(response.text.strip())
    except Exception as e:
        print(f"Error during salary estimation: {e}")
        raise e

def generate_cold_email(resume_text, job_desc, user_name=""):
    """
    Generate a personalized cold email to a recruiter based on resume and JD.
    Returns the cold email as plain text.
    """
    if not api_key:
        raise ValueError("GEMINI_API_KEY is not set. Please check your .env file.")

    name_hint = f"The candidate's name is {user_name}." if user_name else "Use [Your Name] as a placeholder for the sender's name."

    prompt = f"""You are an expert career coach who specializes in recruiter outreach.
Write a short, punchy, and highly personalized cold email to a recruiter or hiring manager for the role described in the job description below.

Guidelines:
- Keep it to 3-4 short paragraphs, under 200 words total
- Open with a specific, non-generic hook referencing the role/company
- In 1-2 sentences, reference the candidate's strongest 2-3 skills that match the JD
- Include a clear, low-friction call to action (e.g. "Happy to share my full resume and portfolio — would a 15-minute chat next week work?")
- Keep a confident but approachable tone — not desperate, not generic
- {name_hint}
- Use [Recruiter Name] as a placeholder for the recipient

Return ONLY the plain text of the cold email. Do not use markdown formatting.

Resume:
{resume_text}

Job Description:
{job_desc}
"""
    try:
        model = genai.GenerativeModel("gemini-2.5-flash")
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Error during cold email generation: {e}")
        raise e
