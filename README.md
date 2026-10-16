# Transparent ATS Simulator MVP

A local-first Applicant Tracking System **simulation** for comparing a resume with a job posting. It does **not** claim to reproduce any proprietary ATS/vendor ranking algorithm.

## What it does
- Upload PDF or DOCX resumes and inspect exactly what was extracted.
- Parse common resume sections, contact info, GPA, graduation date, skills, and formatting warnings.
- Analyze job descriptions for hard requirements, required/preferred qualifications, and skills.
- Evaluate application completeness/eligibility, qualifications, skills, experience, education, and ATS readability.
- Use deterministic weighted scoring: eligibility 30%, required qualifications 25%, skills 20%, experience 15%, education 5%, readability 5%.
- Keep genuine knockout conflicts separate from the numeric score.
- Show recruiter view, rejection analysis, explainability, optimization suggestions, and before/after scenario score.
- Compare multiple jobs in the current Streamlit session.
- Includes modes for Workday, Greenhouse, Lever, iCIMS, Oracle/Taleo, SAP SuccessFactors, SmartRecruiters, Ashby, ADP, UKG, Dayforce, Avature, and Generic ATS. Modes do **not** invent proprietary formulas.

## Architecture
- `ats_simulator/resume_parser.py` — PDF/DOCX text extraction + structured resume parsing
- `ats_simulator/job_parser.py` — requirement and skill extraction
- `ats_simulator/taxonomy.py` — transparent skill vocabulary and semantic relationships
- `ats_simulator/engine.py` — deterministic eligibility, matching, scoring, recruiter view, recommendations
- `ats_simulator/platforms.py` — conservative platform-mode profiles/disclosures
- `ats_simulator/models.py` — data models/evidence records
- `ats_simulator/ui.py` — reusable dashboard UI
- `app.py` — Streamlit application
- `tests/test_engine.py` — seven requested behavioral tests

## Run locally
Requires Python 3.10+.

### Windows PowerShell
```powershell
cd ats-simulator
py -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

### macOS / Linux
```bash
cd ats-simulator
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Open the local URL Streamlit prints (normally `http://localhost:8501`).

## Run tests
```bash
pytest -q
```

## Privacy
This MVP makes no external AI/API calls. Resume bytes are processed in the Streamlit process and the application code does not intentionally save uploads to disk/database. If deployed remotely, uploaded data necessarily reaches that server. Add authentication, encryption, retention controls, and a privacy review before production use.

## Important limitations
- Real employers configure ATS products differently, and human recruiters can make decisions outside the simulated rules.
- Job requirement extraction is rule-based and intentionally conservative; ambiguous prose can require manual interpretation.
- PDF extraction quality depends on the source PDF. Scanned/image-only resumes may need OCR in a future version.
- Platform modes represent defensible workflow/parsing assumptions, not vendor-secret scoring behavior.
- Optimization recommendations never authorize fabrication: only add a skill/term when the resume owner genuinely has supporting experience.

## Sensible next production upgrades
1. Add a validated structured LLM extraction adapter (Pydantic schema) for ambiguous job descriptions while retaining deterministic scoring.
2. Add manual editing/confirmation of extracted requirements before scoring.
3. Add richer DOCX/PDF layout diagnostics (columns, headers/footers, text boxes).
4. Add local SQLite only if persistent job comparison is desired, with explicit retention/deletion controls.
5. Add authentication and encrypted object storage before any multi-user deployment.
