import os
import json
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
  "missing_keywords": [list of skills/tools/technologies in the job description but not in the resume],
  "rewritten_bullets": [
    {{
      "original": "A representative weak/generic bullet point from the resume",
      "rewritten": "The rewritten bullet point incorporating keywords and strong action verbs tailored to the job description",
      "impact": "Explanation of why this rewrite makes the resume stronger for this job"
    }}
  ] (provide 3 to 5 key bullet points)
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
        return data
    except Exception as e:
        print(f"Error during Gemini match analysis: {e}")
        raise e
