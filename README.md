# ResuMatch (AI Resume & Job Match Analyzer)

A production-grade, AI-augmented resume tailoring and applicant tracking system (ATS) optimization engine built on top of Python, Streamlit, and Google Gemini. Features intelligent keyword gap analysis, structural match scoring, and automated resume bullet point transformation.

## Features

- **ATS Alignment Score**: Instantly calculates compatibility percentage (0–100%) against job descriptions.
- **Technical Keyword Extraction**: Performs conceptual gap analysis between resumes and JDs to extract missing tools, frameworks, and methodologies.
- **Tailored Bullet Upgrade Engine**: Generates 3–5 high-impact, results-driven resume bullet points matching the targeted job's syntax and scope.
- **ATS Impact Explanations**: Details the recruitment rationale and keyword integration value behind each recommended rewrite.
- **File Upload Parsing**: Upload `.pdf` or `.txt` resumes and job description files directly.
- **Version Analysis History**: Keep track of ATS compatibility score gains across consecutive runs to benchmark progress.
- **Interview Prep Assistant**: Formulate targeted interview questions focused on resolving identified technical gap areas.
- **JSON Exporter**: Export report diagnostics as both clean raw JSON and readable plain text files.
- **Premium Glassmorphic Interface**: Elegant, premium off-white paper and green-accented design with full contrast controls.
- **Cover Letter Generator**: Generates a tailored cover letter using the same resume + JD inputs with matching tone and keywords. One extra Gemini prompt, zero new dependencies.
- **Multi-Resume Comparison**: Upload 2–3 resume versions and compare their ATS scores against the same JD side by side to help pick the strongest version.
- **Job Description Scraper**: Paste a LinkedIn, Indeed, Lever, Greenhouse, or generic job posting URL to scrape the JD automatically using BeautifulSoup, removing copy-paste friction.
- **Skill Roadmap Generator**: For each identified keyword gap, generate a tailored "how to close this gap" plan outlining recommended courses, certifications, or projects.

---

## Tech Stack

- **Frontend/UI**: Streamlit (Python-native web dashboard framework).
- **LLM/AI Model**: Google Gemini API (`gemini-2.5-flash`) utilizing structured JSON generation.
- **Web Scraping**: BeautifulSoup4 & Requests.
- **Environment**: Python 3.10+ and `python-dotenv`.

---

## Folder Structure

```
ai-resume-job-match-analyzer/
├── app.py                 # Streamlit UI application dashboard
├── gemini_service.py      # Google Gemini client integration service
├── scraper.py             # BeautifulSoup & requests job web scraper
├── utils.py               # PDF and file parsing helpers
├── requirements.txt       # Project python dependencies list
├── .env                   # Environment secrets config (Git ignored)
├── .gitignore             # Git exclusion rules file
└── README.md              # Project setup and user guide documentation
```

---

## System Architecture

```mermaid
graph TD
    subgraph Client ["User Client Browser"]
        Dashboard["Streamlit UI (app.py)"]
        Inputs["Resume & Job Description Textareas"]
    end

    subgraph Service ["AI Matcher Service"]
        GeminiService["Gemini Service module (gemini_service.py)"]
        GenAI["Google GenerativeAI SDK"]
        Scraper["BeautifulSoup Scraper (scraper.py)"]
    end

    subgraph External ["External Resource Core"]
        Gemini[(Google Gemini AI Studio)]
        JobBoard["Job Board Webpage (HTTP requests)"]
    end

    Dashboard --> Inputs
    Inputs --> GeminiService
    Dashboard -- paste URL --> Scraper
    Scraper --> JobBoard
    GeminiService --> GenAI
    GenAI --> Gemini
    Gemini --> GenAI
    GenAI --> Dashboard
```

---

## Setup Instructions

### Prerequisites
Ensure Python 3.10+ is installed on your local computer system.

### Local Installation

1. Navigate to the project directory:
   ```bash
   cd "AI Resume & Job Match Analyzer"
   ```
2. Set up a local Python virtual environment:
   ```bash
   python -m venv venv
   ```
3. Activate the virtual environment:
   * **Windows (PowerShell)**:
     ```powershell
     .\venv\Scripts\Activate.ps1
     ```
   * **Windows (CMD)**:
     ```cmd
     .\venv\Scripts\activate.bat
     ```
   * **macOS/Linux**:
     ```bash
     source venv/bin/activate
     ```
4. Install all python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
5. Configure the environment variables by creating `.env` in the root:
   ```
   GEMINI_API_KEY=your_gemini_api_key_here
   ```
6. Launch the Streamlit application server:
   ```bash
   streamlit run app.py
   ```

The application will launch on your local host at **[http://localhost:8501](http://localhost:8501)**.
