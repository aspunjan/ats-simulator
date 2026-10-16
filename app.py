import streamlit as st
import pandas as pd
from ats_simulator.resume_parser import parse_resume
from ats_simulator.job_parser import parse_job
from ats_simulator.engine import evaluate
from ats_simulator.platforms import PLATFORMS
from ats_simulator.ui import metric_row, score_bars

st.set_page_config(page_title="Transparent ATS Simulator", page_icon="📄", layout="wide")
st.title("Transparent ATS Simulator")
st.info("This app simulates common ATS/recruiting screening practices. It does not reproduce or claim access to proprietary Workday, Greenhouse, Lever, or other vendor algorithms.")

if "comparisons" not in st.session_state: st.session_state.comparisons=[]
left,right=st.columns(2)
with left:
    st.subheader("Resume Upload")
    resume_file=st.file_uploader("PDF or DOCX", type=["pdf","docx"])
with right:
    st.subheader("Job Description")
    job_title=st.text_input("Job title")
    company=st.text_input("Company")
    job_text=st.text_area("Paste the complete job posting", height=300)

platform=st.selectbox("ATS / recruiting platform", list(PLATFORMS))
st.caption(PLATFORMS[platform]["note"])
with st.expander("Application questions / knockout inputs", expanded=True):
    c1,c2,c3=st.columns(3)
    auth=c1.selectbox("Authorized to work for this employer?", ["Not specified","Yes","No"])
    sponsor=c2.selectbox("Will you require sponsorship?", ["Not specified","No","Yes"])
    gpa=c3.number_input("GPA (0 if not supplied)", min_value=0.0,max_value=4.0,value=0.0,step=.01)
    graduation=st.text_input("Graduation date/window")
    degree=st.text_input("Degree / major")
    location=st.text_input("Location / relocation notes")
    years=st.number_input("Years of relevant experience", min_value=0.0,max_value=50.0,value=0.0,step=.5)
    internship=st.selectbox("Internship eligibility", ["Not specified","Yes","No"])
    custom=st.text_area("Other job-specific questions/answers", placeholder="Example: Are you willing to relocate? Yes")

run=st.button("Run ATS Simulation", type="primary", use_container_width=True)
if run:
    if not resume_file or not job_text.strip(): st.error("Upload a resume and paste a job description first.")
    else:
        resume=parse_resume(resume_file); job=parse_job(job_text,job_title,company)
        answers={"work_authorization":auth,"sponsorship":sponsor,"gpa":gpa or None,"graduation":graduation,"degree":degree,"location":location,"years_experience":years,"internship_eligibility":internship,"custom":custom}
        result=evaluate(resume,job,answers,platform)
        st.session_state.last=(resume,job,result,platform)
        st.session_state.comparisons.append({"Job":job_title or "Untitled role","Company":company or "—","ATS":platform,"ATS Score":result.overall_score,"Eligibility":result.knockout_status,"Skill Match":result.category_scores["Skills Match"],"Experience Match":result.category_scores["Experience Match"],"Estimated Screening Result":result.outcome})

if "last" in st.session_state:
    resume,job,result,platform=st.session_state.last
    st.divider(); metric_row(result)
    if result.knockout_status!="PASS": st.error(f"Eligibility check: {result.knockout_status}")
    else: st.success("Eligibility check: PASS — no explicit knockout conflict was detected from the supplied information.")
    score_bars(result.category_scores)
    tabs=st.tabs(["Eligibility & Qualifications","Skills","Experience & Education","Parser Output","Rejection Analysis","Recruiter View","Optimization","Explainability","Comparison Mode"])
    with tabs[0]:
        st.subheader("Requirement-by-requirement evidence")
        if result.requirements: st.dataframe([r.__dict__ for r in result.requirements], use_container_width=True)
        else: st.write("No explicit hard/minimum requirements were confidently extracted. Treat the result with caution.")
        st.write("**Detected hard requirements**", job.hard_requirements or "None confidently detected")
        st.write("**Required qualifications**", job.required_qualifications or "None confidently detected")
        st.write("**Preferred qualifications**", job.preferred_qualifications or "None confidently detected")
    with tabs[1]:
        st.write("**Exact matches:**", result.exact_skills or "None")
        st.write("**Strong semantic matches:**", result.semantic_skills or "None")
        st.write("**Weak/indirect matches:**", result.weak_skills or "None")
        st.write("**Missing skills:**", result.missing_skills or "None")
        st.caption("Repeated keywords do not earn extra credit. Semantic matches use a bounded, inspectable relationship map.")
    with tabs[2]:
        st.write("**Experience evidence extracted:**", resume.experience or "None")
        st.write("**Projects:**", resume.projects or "None")
        st.write("**Leadership:**", resume.leadership or "None")
        st.write("**Relevant coursework:**", resume.coursework or "None")
        st.write("**Education:**", resume.education or "None")
        st.write("**GPA:**", resume.gpa if resume.gpa is not None else "Not parsed")
        st.write("**Graduation:**", resume.graduation or "Not parsed")
    with tabs[3]:
        st.metric("Parsing Confidence", f"{resume.parsing_confidence}/100")
        st.json({"name":resume.name,"email":resume.email,"phone":resume.phone,"education":resume.education,"experience":resume.experience,"skills":resume.skills,"certifications":resume.certifications,"projects":resume.projects,"leadership":resume.leadership,"coursework":resume.coursework,"gpa":resume.gpa,"graduation":resume.graduation,"parsing_issues":resume.parsing_issues})
        with st.expander("Raw extracted resume text"): st.text(resume.raw_text)
    with tabs[4]:
        for k,v in result.rejection_analysis.items():
            st.write(f"**{k}**"); st.write(v or "None detected")
    with tabs[5]:
        st.subheader("Recruiter View")
        for k,v in result.recruiter_view.items(): st.write(f"**{k}:** {v}")
        st.caption("This assumes the application reached human review; it is an estimate, not a prediction of a specific recruiter's decision.")
    with tabs[6]:
        st.subheader("Resume Optimization")
        if result.recommendations:
            for i,r in enumerate(result.recommendations,1):
                with st.expander(f"{i}. {r['change']}"):
                    st.write("**Why:**",r['why']); st.write("**Where:**",r['where']); st.write("**Suggested wording approach:**",r['wording']); st.write("**Estimated effect:**",r['estimated_effect'])
        else: st.write("No high-confidence optimization recommendation was generated.")
        c1,c2=st.columns(2); c1.metric("Original Resume",result.overall_score); c2.metric("Estimated Optimized",result.optimized_score,delta=result.optimized_score-result.overall_score)
        st.caption("The optimized score is only a scenario estimate and assumes suggested terms can be added truthfully from existing experience.")
    with tabs[7]:
        st.write("### Score calculation")
        for x in result.explanation: st.write("-",x)
        st.write("### Explicit vs inferred decisions")
        if result.requirements: st.dataframe([{"requirement":r.label,"evidence":r.evidence,"decision":r.status,"source":r.source,"reason":r.reason} for r in result.requirements],use_container_width=True)
    with tabs[8]:
        st.subheader("Job Comparison")
        df=pd.DataFrame(st.session_state.comparisons).drop_duplicates(subset=["Job","Company","ATS"],keep="last").sort_values("ATS Score",ascending=False)
        st.dataframe(df,use_container_width=True,hide_index=True)
        if st.button("Clear comparison history"): st.session_state.comparisons=[]; st.rerun()

st.divider()
st.caption("Privacy: files are processed in the running Streamlit process for this MVP and are not intentionally persisted by the app. If you deploy it to a server, that server receives uploaded resume data. No external AI/API call is used in this version.")
