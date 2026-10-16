from ats_simulator.models import ResumeProfile
from ats_simulator.job_parser import parse_job
from ats_simulator.engine import evaluate

def run(resume_text, job_text, skills=None, issues=None, answers=None):
    r=ResumeProfile(raw_text=resume_text,education=["BS Finance"] if "degree" in resume_text.lower() else [],experience=[resume_text],skills=skills or [],coursework=["Financial Accounting"] if "coursework" in resume_text.lower() else [],parsing_issues=issues or [],parsing_confidence=100-12*len(issues or []))
    return evaluate(r,parse_job(job_text),answers or {"work_authorization":"Yes","sponsorship":"No"})

def test_excellent_candidate():
    x=run("degree finance excel python data analysis communication leadership project management", "Required: degree and Excel. Required: Python and data analysis. Preferred: leadership.", ["finance","excel","python","data analysis","communication","leadership","project management"])
    assert x.overall_score >= 70 and not x.rejection_analysis["LIKELY KNOCKOUT ISSUE"]

def test_missing_preferred_not_knockout():
    x=run("degree finance excel", "Required: degree and Excel. Preferred: Tableau.", ["finance","excel"])
    assert x.knockout_status == "PASS"

def test_missing_required_skill_reduces_skill_score():
    x=run("degree finance", "Required: Excel and SQL.", ["finance"])
    assert x.category_scores["Skills Match"] < 60

def test_true_knockout():
    x=run("degree finance", "Candidates must be authorized to work in the United States. We will not sponsor visas.", ["finance"], answers={"work_authorization":"No","sponsorship":"Yes"})
    assert x.knockout_status == "LIKELY AUTO-REJECT" and x.outcome == "Likely Auto-Reject"

def test_poor_formatting_lowers_readability():
    x=run("degree finance excel", "Required: Excel.", ["excel"], issues=["table","missing dates","contact missing"])
    assert x.category_scores["ATS Readability"] < 80

def test_entry_level_coursework_gets_credit():
    x=run("degree finance coursework financial accounting excel", "Finance intern. Required: Excel and accounting.", ["finance","accounting","excel"])
    assert x.category_scores["Experience Match"] >= 50

def test_strong_experience_weak_keyword_overlap():
    x=run("degree managed budgets forecasts reporting for three years", "Required: SQL and Python data analysis.", [])
    assert x.category_scores["Experience Match"] >= 45 and x.category_scores["Skills Match"] < 60
