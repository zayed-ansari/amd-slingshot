"""
PhantomTrain - Risk Scoring Engine
Scores targets and campaigns based on attack simulations.
"""

from dataclasses import dataclass, field
from typing import Optional
from modules.generator import GeneratedAttack
from modules.osint import TargetProfile


URGENCY_SCORE = {"low": 1, "medium": 2, "high": 3}
SUCCESS_SCORE = {"low": 1, "medium": 2, "high": 3}

# How many psych hooks = how dangerous
HOOK_WEIGHTS = {
    "Authority": 2.0,
    "Urgency": 1.8,
    "Fear": 1.7,
    "Loss Aversion": 1.6,
    "Trust / Familiarity": 1.5,
    "FOMO (Fear of Missing Out)": 1.4,
    "Scarcity": 1.3,
    "Curiosity": 1.2,
    "Social Proof": 1.1,
    "Reciprocity": 1.0,
    "Liking": 1.0,
}

# High-value departments
DEPARTMENT_RISK = {
    "finance": 9,
    "accounting": 9,
    "payroll": 9,
    "executive": 9,
    "c-suite": 9,
    "ceo": 10,
    "cfo": 10,
    "cto": 9,
    "hr": 8,
    "human resources": 8,
    "it": 7,
    "engineering": 7,
    "devops": 7,
    "security": 6,
    "sales": 6,
    "marketing": 5,
    "operations": 5,
    "legal": 8,
    "compliance": 8,
}


@dataclass
class RiskScore:
    overall: int           # 0-100
    label: str             # Low / Medium / High / Critical
    color: str             # For UI
    breakdown: dict        # Component scores
    recommendations: list  # What training to prioritize


@dataclass 
class CampaignResult:
    target_name: str
    role: str
    department: str
    attack_type: str
    risk_score: RiskScore
    attack: GeneratedAttack
    status: str = "sent"   # sent / clicked / reported / no_response
    debrief: str = ""


def score_target(target: TargetProfile, attack: GeneratedAttack) -> RiskScore:
    """Score the risk of a target based on their profile and the attack generated."""
    
    components = {}

    # 1. Sophistication of the attack (0-30 points)
    components["attack_sophistication"] = min(30, attack.sophistication_score * 3)

    # 2. Psychological hook power (0-25 points)
    hook_power = sum(HOOK_WEIGHTS.get(h, 1.0) for h in attack.psychological_hooks)
    components["psychological_hooks"] = min(25, int(hook_power * 3))

    # 3. Department sensitivity (0-20 points)
    dept_lower = target.employee.department.lower()
    dept_risk = 5  # default
    for key, val in DEPARTMENT_RISK.items():
        if key in dept_lower:
            dept_risk = val
            break
    components["department_sensitivity"] = min(20, int(dept_risk * 2))

    # 4. Urgency level (0-15 points)
    components["urgency"] = URGENCY_SCORE.get(attack.urgency_level, 2) * 5

    # 5. Company data exposure (0-10 points) - more scraped data = more personalized = more dangerous
    company_score = 0
    if target.company.description:
        company_score += 2
    if target.company.recent_news:
        company_score += min(4, len(target.company.recent_news))
    if target.company.technologies:
        company_score += min(4, len(target.company.technologies))
    components["company_exposure"] = company_score

    overall = sum(components.values())
    overall = min(100, overall)

    # Label and color
    if overall >= 80:
        label, color = "Critical", "#FF2E2E"
    elif overall >= 60:
        label, color = "High", "#FF6B35"
    elif overall >= 40:
        label, color = "Medium", "#FFB347"
    else:
        label, color = "Low", "#4CAF50"

    # Recommendations
    recs = []
    if components["psychological_hooks"] >= 15:
        recs.append("Priority: Social engineering awareness training")
    if components["department_sensitivity"] >= 14:
        recs.append("Department-specific BEC (Business Email Compromise) training")
    if components["urgency"] >= 10:
        recs.append("Train employees to pause and verify urgent requests via a second channel")
    if components["attack_sophistication"] >= 20:
        recs.append("Advanced phishing simulation drills recommended quarterly")
    if not recs:
        recs.append("Standard security awareness training sufficient")

    return RiskScore(
        overall=overall,
        label=label,
        color=color,
        breakdown=components,
        recommendations=recs,
    )


def org_risk_summary(results: list) -> dict:
    """Summarize risk across an entire campaign."""
    if not results:
        return {}
    
    scores = [r.risk_score.overall for r in results]
    
    dept_risks = {}
    for r in results:
        dept = r.department
        if dept not in dept_risks:
            dept_risks[dept] = []
        dept_risks[dept].append(r.risk_score.overall)
    
    dept_avg = {dept: int(sum(v)/len(v)) for dept, v in dept_risks.items()}
    
    critical_count = sum(1 for s in scores if s >= 80)
    high_count = sum(1 for s in scores if 60 <= s < 80)
    
    return {
        "total_targets": len(results),
        "avg_risk": int(sum(scores) / len(scores)),
        "max_risk": max(scores),
        "critical_count": critical_count,
        "high_count": high_count,
        "department_risks": dept_avg,
        "highest_risk_dept": max(dept_avg, key=dept_avg.get) if dept_avg else "N/A",
    }
