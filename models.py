from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional

@dataclass
class Evidence:
    label: str
    evidence: str
    status: str
    importance: str = "medium"
    source: str = "explicit"
    reason: str = ""

@dataclass
class ResumeProfile:
    raw_text: str
    name: str = ""
    email: str = ""
    phone: str = ""
    education: List[str] = field(default_factory=list)
    experience: List[str] = field(default_factory=list)
    skills: List[str] = field(default_factory=list)
    certifications: List[str] = field(default_factory=list)
    projects: List[str] = field(default_factory=list)
    leadership: List[str] = field(default_factory=list)
    coursework: List[str] = field(default_factory=list)
    gpa: Optional[float] = None
    graduation: str = ""
    parsing_issues: List[str] = field(default_factory=list)
    parsing_confidence: int = 100

@dataclass
class JobProfile:
    raw_text: str
    title: str = ""
    company: str = ""
    hard_requirements: List[str] = field(default_factory=list)
    required_qualifications: List[str] = field(default_factory=list)
    preferred_qualifications: List[str] = field(default_factory=list)
    skills: List[str] = field(default_factory=list)

@dataclass
class SimulationResult:
    overall_score: int
    outcome: str
    confidence: str
    knockout_status: str
    category_scores: Dict[str, int]
    requirements: List[Evidence]
    exact_skills: List[str]
    semantic_skills: List[str]
    weak_skills: List[str]
    missing_skills: List[str]
    rejection_analysis: Dict[str, List[str]]
    recruiter_view: Dict[str, str]
    recommendations: List[Dict[str, str]]
    optimized_score: int
    explanation: List[str]

    def to_dict(self):
        return asdict(self)
