SKILLS = {
    "finance": ["finance", "financial analysis", "corporate finance"],
    "accounting": ["accounting", "gaap", "financial statements", "journal entries"],
    "excel": ["excel", "microsoft excel", "pivot table", "vlookup", "xlookup"],
    "financial modeling": ["financial modeling", "financial model", "forecasting", "valuation", "dcf"],
    "data analysis": ["data analysis", "analytics", "analyze data", "data-driven"],
    "sql": ["sql", "mysql", "postgresql", "sql server"],
    "python": ["python", "pandas", "numpy"],
    "power bi": ["power bi", "powerbi"],
    "tableau": ["tableau"],
    "communication": ["communication", "communicate", "presentation", "presented", "written and verbal"],
    "leadership": ["leadership", "led ", "managed", "president", "captain"],
    "project management": ["project management", "managed project", "project planning", "cross-functional"],
}

SEMANTIC = {
    "financial modeling": ["finance", "financial analysis", "forecasting", "valuation"],
    "finance": ["financial analysis", "financial modeling", "accounting"],
    "data analysis": ["excel", "sql", "python", "power bi", "tableau"],
    "excel": ["data analysis", "financial modeling"],
    "communication": ["leadership", "presentation"],
    "project management": ["leadership", "cross-functional"],
    "accounting": ["finance", "financial statements"],
}
