import requests
from bs4 import BeautifulSoup
import re

def scrape_job_description(url: str) -> str:
    """
    Scrapes job description text from a job posting URL.
    Supports special selectors for Greenhouse, Lever, and general web parsing with BeautifulSoup.
    """
    if not url.strip().startswith(("http://", "https://")):
        raise ValueError("Please provide a valid URL starting with http:// or https://")
        
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            raise Exception(f"Failed to fetch URL. HTTP Status: {response.status_code}")
    except Exception as e:
        raise Exception(f"Failed to access the URL: {str(e)}")
        
    soup = BeautifulSoup(response.text, "html.parser")
    
    # 1. Lever
    if "lever.co" in url:
        posting_heading = soup.find(class_="posting-header")
        description_sections = soup.find_all(class_="section")
        text_parts = []
        if posting_heading:
            text_parts.append(posting_heading.get_text(separator="\n"))
        for section in description_sections:
            text_parts.append(section.get_text(separator="\n"))
        if text_parts:
            return "\n\n".join(text_parts).strip()
            
    # 2. Greenhouse
    if "greenhouse.io" in url:
        content_div = soup.find(id="content")
        if content_div:
            return content_div.get_text(separator="\n").strip()
            
    # 3. LinkedIn (anti-bot fallback check)
    if "linkedin.com" in url:
        main_body = soup.find(class_="show-more-less-html__markup")
        if main_body:
            return main_body.get_text(separator="\n").strip()
        if "security" in response.url or response.status_code == 999 or (soup.title and "sign in" in soup.title.string.lower() if soup.title else False):
            raise Exception("LinkedIn anti-bot protection blocked the request. Please copy-paste the JD text manually.")

    # 4. Indeed
    if "indeed.com" in url:
        desc_div = soup.find(id="jobDescriptionText")
        if desc_div:
            return desc_div.get_text(separator="\n").strip()
        raise Exception("Indeed anti-bot protection blocked the request. Please copy-paste the JD text manually.")

    # 5. General Web Scraping Fallback
    # Remove script, style, header, footer, nav, aside elements to get clean job text
    for element in soup(["script", "style", "header", "footer", "nav", "aside"]):
        element.decompose()
        
    # Look for common job description containers
    selectors = [
        "div[class*='jobDescription']", "div[class*='description']", "div[class*='job-description']",
        "main", "article", "[role='main']"
    ]
    for sel in selectors:
        match = soup.select_one(sel)
        if match:
            text = match.get_text(separator="\n").strip()
            # If we get decent content size, use it
            if len(text) > 300:
                return text
                
    # Ultimate fallback: just return cleaned body text
    body = soup.body
    if body:
        text = body.get_text(separator="\n")
        # Remove consecutive duplicate newlines
        text = re.sub(r'\n+', '\n', text)
        return text.strip()
        
    return soup.get_text(separator="\n").strip()
