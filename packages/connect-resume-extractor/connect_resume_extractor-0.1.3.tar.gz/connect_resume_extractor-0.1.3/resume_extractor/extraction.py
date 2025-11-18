import re
import fitz
from datetime import datetime
from .db import load_colleges_df, load_branches_df

df_colleges = load_colleges_df()
df_branches = load_branches_df()

# ------------------ BASIC UTILITIES ------------------

def extract_text(file_path: str):
    doc = fitz.open(file_path)
    text = ""
    for page in doc:
        text += page.get_text("text") + "\n"
    return text

def extract_mobile_no_from_text(pdf_text: str):
    pattern = re.compile(r'(?:\+?91[\s\-]*)?0?([6-9]\d{9})')
    m = pattern.findall(pdf_text)
    return m[0] if m else None

def extracting_urls_from_pdf(path: str):
    urls = set()
    doc = fitz.open(path)
    for page in doc:
        for link in page.get_links():
            if "uri" in link:
                urls.add(link["uri"])
        text = page.get_text("text")
        urls.update(re.findall(r'https?://[^\s)]+', text))
    return list(urls)

_SECTION_BOUNDARIES = [
    r'\bprojects\b', r'\bresearch\b', r'\bexperience\b',
    r'\bintern(ship)?\b', r'\bskills\b', r'\bcertificat',
    r'\bachievement', r'\brelevant coursework\b',
]

def extract_education_section(full_text: str) -> str:
    text = full_text.replace("\r", "\n")
    m = re.search(r'(?im)^\s*(education|academic background)\s*[:\-]?\s*$', text)
    if m:
        start = m.end()
        end_positions = []
        for boundary in _SECTION_BOUNDARIES:
            mm = re.search(boundary, text[start:], re.I)
            if mm:
                end_positions.append(start + mm.start())
        end = min(end_positions) if end_positions else start + 600
        snippet = text[start:end]
        return "\n".join([ln.strip() for ln in snippet.splitlines() if ln.strip()])

    lines = text.splitlines()
    for i, ln in enumerate(lines):
        if re.search(r'\bbachelor|b\.tech|btech|m\.tech|mtech|engineering\b', ln, re.I):
            start = max(0, i - 3)
            end = min(len(lines), i + 6)
            return "\n".join(lines[start:end])

    return "\n".join(lines[:20])

def extract_passout_year(text: str):
    years = re.findall(r'\b(?:19|20)\d{2}\b', text)
    years = [int(y) for y in years]
    if "present" in text.lower():
        return min(years) + 4 if years else datetime.now().year + 2
    return max(years) if years else None

def extract_college_name(edu_text: str):
    lines = [ln.strip() for ln in edu_text.splitlines() if ln.strip()]
    first = lines[0] if lines else ""
    if re.search(r'(institute|iit|iiit|nit|university|technology|college)', first, re.I):
        return first
    for ln in lines:
        if re.search(r'(institute|iit|iiit|nit|university|technology|college)', ln, re.I):
            return ln
    for ln in lines:
        if ln.isupper() and len(ln) > 20:
            return ln
    return max(lines, key=len) if lines else None

def extract_branch_name(edu_text: str):
    text = edu_text
    text = re.sub(r"(CGPA|GPA|CPI|SGPA|Score)\s*[:\-]?\s*\d+(\.\d+)?", "", text, flags=re.I)
    text = re.sub(r"\b(B\.?\s*Tech|BTech|Bachelor of Technology|B\.?\s*E|BE|Bachelor of Engineering)\b", "", text, flags=re.I)

    m = re.search(r"\bin\s+([A-Za-z &/\-]{3,80})", text, flags=re.I)
    if m:
        branch_raw = m.group(1).strip(" .,-")
    else:
        return None

    branch_raw = re.sub(r"[\(\)\[\]\d]", "", branch_raw).strip()
    return branch_raw

def extract_degree(edu_text: str):
    t = edu_text.lower()
    if "b.tech" in t or "bachelor of technology" in t or "btech" in t:
        return "B.Tech"
    if "b.e" in t or "bachelor of engineering" in t:
        return "B.E"
    if "m.tech" in t:
        return "M.Tech"
    return None

def extract_linkedin_url(urls):
    for u in urls:
        if "linkedin.com" in u.lower():
            return u
    return None

def clean_text(college: str):
    text = college.lower()
    text = re.sub(r'\([^)]*\)', ' ', text)
    text = re.sub(r'[.,()\-\/&]', ' ', text)
    return re.sub(r'\s+', ' ', text).strip()

def extracting_college_from_db(college: str):
    if not college:
        return None
    cleaned = clean_text(college)
    matches = df_colleges[df_colleges["normalized"].apply(lambda x: cleaned in x)]
    return matches.iloc[0]["original"] if len(matches) else None

def extracting_branch_from_db(branch: str):
    if not branch:
        return None
    cleaned = clean_text(branch)
    matches = df_branches[df_branches["normalized"].apply(lambda x: cleaned in x)]
    return matches.iloc[0]["original"] if len(matches) else None

# ------------------ ONE-LINE MAIN FUNCTION ------------------

def extract_resume(file_path: str):
    full_text = extract_text(file_path)
    edu = extract_education_section(full_text)
    urls = extracting_urls_from_pdf(file_path)

    data = {
        "mobile": extract_mobile_no_from_text(full_text),
        "passout_year": extract_passout_year(edu),
        "degree": extract_degree(edu),
        "branch": extracting_branch_from_db(extract_branch_name(edu)),
        "college": extracting_college_from_db(extract_college_name(edu)),
        "linkedin": extract_linkedin_url(urls),
    }

    return data
