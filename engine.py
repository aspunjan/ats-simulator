import re
from models import Evidence, SimulationResult
from taxonomy import SEMANTIC
from platforms import PLATFORMS

WEIGHTS={"Hard Requirements":.30,"Required Qualifications":.25,"Skills Match":.20,"Experience Match":.15,"Education Match":.05,"ATS Readability":.05}

def _contains(text, phrase): return phrase.lower() in text.lower()
def _tokens(s): return set(re.findall(r'[a-z0-9+#.]+', s.lower()))
def _overlap(a,b):
    aa=_tokens(a); bb=_tokens(b)
    return len(aa&bb)/max(1,len(bb))

def evaluate(resume, job, answers, platform="Unknown / Generic ATS"):
    rtext=resume.raw_text.lower(); requirements=[]; knockout=[]
    # Explicit application answers take precedence for common true knockout questions.
    auth=answers.get("work_authorization", "Not specified")
    sponsor=answers.get("sponsorship", "Not specified")
    if any("authoriz" in h.lower() for h in job.hard_requirements):
        st="Match" if auth=="Yes" else ("Missing" if auth=="No" else "Partial Match")
        requirements.append(Evidence("Work authorization", auth, st, "critical", "explicit", "Based on an explicit job/application eligibility requirement."))
        if auth=="No": knockout.append("Work authorization answer conflicts with an explicit authorization requirement.")
    if any("sponsor" in h.lower() for h in job.hard_requirements):
        no_sponsor=any(x in job.raw_text.lower() for x in ["will not sponsor", "no sponsorship", "unable to sponsor", "without sponsorship"])
        st="Missing" if no_sponsor and sponsor=="Yes" else ("Match" if sponsor in ["No","Not specified"] else "Partial Match")
        requirements.append(Evidence("Sponsorship", sponsor, st, "critical", "explicit", "Compared with sponsorship language detected in the posting."))
        if no_sponsor and sponsor=="Yes": knockout.append("Candidate indicates sponsorship is required while the posting says sponsorship is unavailable.")
    # GPA rule
    gpa_req=re.search(r'(?:minimum\s+gpa|gpa(?:\s+of)?)[^0-9]{0,10}([0-4](?:\.\d{1,2})?)', job.raw_text, re.I)
    if gpa_req:
        req=float(gpa_req.group(1)); cand=answers.get("gpa") or resume.gpa
        st="Match" if cand is not None and float(cand)>=req else ("Missing" if cand is not None else "Partial Match")
        requirements.append(Evidence(f"Minimum GPA {req:g}", str(cand or "Not found"), st, "high", "explicit", "Numeric comparison to posting requirement."))
        if cand is not None and float(cand)<req: knockout.append(f"GPA {cand} is below the explicit minimum GPA {req:g}.")
    # Required qualification evidence by text overlap.
    req_matches=[]
    for q in job.required_qualifications:
        ov=_overlap(rtext,q)
        st="Match" if ov>=.45 else ("Partial Match" if ov>=.18 else "Missing")
        ev="Resume text shares relevant terms" if ov>=.18 else "No clear supporting evidence found"
        requirements.append(Evidence(q[:140],ev,st,"high","explicit",f"Deterministic token-overlap evidence score: {ov:.2f}."))
        req_matches.append(100 if st=="Match" else 55 if st=="Partial Match" else 0)
    req_score=round(sum(req_matches)/len(req_matches)) if req_matches else 85
    # Skills: exact + bounded semantic relationships; repeated mentions do not increase score.
    exact=[]; semantic=[]; weak=[]; missing=[]
    for skill in job.skills:
        if skill in resume.skills: exact.append(skill)
        elif any(rel in resume.skills for rel in SEMANTIC.get(skill,[])): semantic.append(skill)
        elif any(_contains(rtext, term) for term in skill.split()): weak.append(skill)
        else: missing.append(skill)
    denom=max(1,len(job.skills)); skill_score=round((100*len(exact)+70*len(semantic)+35*len(weak))/denom) if job.skills else 80
    # Experience and education use evidence presence + job vocabulary relevance.
    exp_text=" ".join(resume.experience+resume.projects+resume.leadership+resume.coursework)
    relevance=max([_overlap(exp_text,q) for q in job.required_qualifications] or [0])
    entry_level=any(x in job.raw_text.lower() for x in ["intern", "entry level", "student", "new grad", "university"])
    evidence_blocks=sum(bool(x) for x in [resume.experience,resume.projects,resume.leadership,resume.coursework])
    exp_score=min(100, round(45 + relevance*45 + evidence_blocks*6 + (8 if entry_level and (resume.coursework or resume.projects) else 0)))
    edu_score=90 if resume.education else 45
    if any(x in job.raw_text.lower() for x in ["bachelor", "degree", "major", "university"]): edu_score=95 if resume.education else 25
    parse_score=max(0,min(100,resume.parsing_confidence+PLATFORMS[platform]["parse_modifier"]))
    hard_score=100
    critical=[r for r in requirements if r.importance=="critical"]
    if critical: hard_score=round(sum(100 if r.status=="Match" else 50 if r.status=="Partial Match" else 0 for r in critical)/len(critical))
    if knockout: hard_score=min(hard_score,20)
    cats={"Hard Requirements":hard_score,"Required Qualifications":req_score,"Skills Match":skill_score,"Experience Match":exp_score,"Education Match":edu_score,"ATS Readability":parse_score}
    overall=round(sum(cats[k]*WEIGHTS[k] for k in WEIGHTS))
    knockout_status="LIKELY AUTO-REJECT" if knockout else ("POSSIBLE AUTO-REJECT" if any(r.status=="Missing" and r.importance=="critical" for r in requirements) else "PASS")
    outcome="Likely Auto-Reject" if knockout else "At Risk" if overall<65 else "Likely Pass Initial Screening" if overall<82 else "Strong Match"
    confidence="High" if (job.required_qualifications or job.hard_requirements) and parse_score>=80 else "Medium" if parse_score>=60 else "Low"
    major=[r.label for r in requirements if r.status=="Missing" and r.importance in ["critical","high"]]
    minor=[r.label for r in requirements if r.status=="Partial Match"]
    rejection={"LIKELY KNOCKOUT ISSUE":knockout,"MAJOR WEAKNESSES":major,"MINOR WEAKNESSES":minor,"MISSING QUALIFICATIONS":major,"MISSING/UNDERREPRESENTED KEYWORDS":missing,"PARSING PROBLEMS":resume.parsing_issues}
    strengths=(exact+semantic)[:5]
    interview="High" if overall>=82 and not knockout else "Medium" if overall>=65 and not knockout else "Low"
    recruiter={"Education":"; ".join(resume.education[:3]) or "No clearly parsed education section.","Relevant experience":("; ".join(resume.experience[:4]) or "Limited clearly parsed work-experience evidence."),"Strongest skills":", ".join(strengths) or "No strong job-specific skill matches detected.","Major strengths":", ".join(exact[:5]) or "General transferable evidence.","Major weaknesses":", ".join((missing+major)[:5]) or "No major weakness detected by the simulation.","Potential concerns":"; ".join(knockout+resume.parsing_issues[:2]) or "No major eligibility/parsing concern detected.","Overall fit":outcome,"Interview likelihood":interview}
    recs=[]
    for s in missing[:5]: recs.append({"change":f"If truthful, make existing {s} evidence explicit.","why":"The posting references this skill but the parser found no supported evidence.","where":"Most relevant experience/project/coursework bullet","wording":f"Use the exact term '{s}' only where it accurately describes work you already performed.","estimated_effect":"+1 to +4 points if supported by genuine evidence"})
    for issue in resume.parsing_issues[:3]: recs.append({"change":"Simplify the affected resume formatting/content.","why":issue,"where":"Resume structure/contact/date formatting","wording":"Prefer conventional headings, plain text dates, and single-column content where practical.","estimated_effect":"+1 to +3 readability points"})
    estimated_gain=min(12, len(missing[:5])*2 + len(resume.parsing_issues[:3]))
    optimized=min(100, overall+estimated_gain)
    explanation=[f"{k}: {v}/100 × {int(WEIGHTS[k]*100)}%" for k,v in cats.items()]
    explanation.append(PLATFORMS[platform]["note"])
    return SimulationResult(overall,outcome,confidence,knockout_status,cats,requirements,exact,semantic,weak,missing,rejection,recruiter,recs,optimized,explanation)
