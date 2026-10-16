import re
from models import JobProfile
from taxonomy import SKILLS

HARD_PATTERNS = [
    r'[^.\n]*(?:must be authorized|work authorization|authorized to work)[^.\n]*',
    r'[^.\n]*(?:sponsorship|visa sponsorship)[^.\n]*',
    r'[^.\n]*(?:minimum gpa|gpa of|gpa >=|gpa ≥)[^.\n]*',
    r'[^.\n]*(?:graduat(?:e|ing|ion).{0,40}(?:20\d{2}))[^.\n]*',
    r'[^.\n]*(?:must have|required to have|minimum of)\s+\d+[^.\n]*(?:years?|experience)[^.\n]*',
]

def _sentences(text):
    return [s.strip(' •\t-') for s in re.split(r'[\n\r]+|(?<=[.!?])\s+', text) if len(s.strip()) > 3]

def parse_job(text: str, title="", company="") -> JobProfile:
    low=text.lower(); sentences=_sentences(text)
    hard=[]
    for p in HARD_PATTERNS:
        hard += [m.group(0).strip() for m in re.finditer(p, text, re.I)]
    req=[]; pref=[]
    for s in sentences:
        sl=s.lower()
        if any(x in sl for x in ["required", "must have", "minimum qualification", "basic qualification", "requirements:"]): req.append(s)
        elif any(x in sl for x in ["preferred", "nice to have", "bonus", "desired"]): pref.append(s)
    skills=[]
    for skill, terms in SKILLS.items():
        if any(t in low for t in terms): skills.append(skill)
    return JobProfile(text, title, company, list(dict.fromkeys(hard)), list(dict.fromkeys(req)), list(dict.fromkeys(pref)), skills)
