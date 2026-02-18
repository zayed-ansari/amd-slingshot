"""
PhantomTrain - Attack Generator
Uses Claude API to generate personalized social engineering attacks.
"""

import google.generativeai as genai
import json
import re
from dataclasses import dataclass
from typing import Optional
from modules.osint import TargetProfile


@dataclass
class GeneratedAttack:
    attack_type: str
    subject: str
    body: str
    sender_name: str
    sender_email: str
    pretext: str
    psychological_hooks: list
    annotations: list
    urgency_level: str  # low / medium / high
    sophistication_score: int  # 1-10
    likely_success_rate: str  # low / medium / high


ATTACK_TYPE_DESCRIPTIONS = {
    "invoice_fraud": "A fake invoice or payment request from a known vendor",
    "credential_phishing": "A fake login/security notification to steal credentials",
    "executive_impersonation": "Impersonating a senior executive making an urgent request",
    "wire_transfer_request": "A fraudulent wire transfer or payment approval request",
    "fake_security_alert": "A fake IT/security alert requiring immediate action",
    "fake_client_inquiry": "A fake prospect or client inquiry to extract info or click a link",
    "github_notification": "A fake GitHub/GitLab access or security notification",
    "collaboration_tool_phishing": "A fake Slack/Teams/M365 notification",
    "employee_data_request": "A fake HR or compliance data request",
    "fake_job_applicant": "A fake job application with a malicious attachment",
    "partnership_opportunity": "A fake business opportunity or partnership proposal",
    "generic_phishing": "A targeted phishing email with personalized details",
    "account_verification": "A fake account verification or password reset request",
    "security_alert": "A fake security breach notification requiring action",
    "urgent_business_deal": "An urgent deal or opportunity requiring immediate sign-off",
    "fake_salesforce_notification": "A fake Salesforce CRM notification or report",
    "fake_sap_notification": "A fake SAP ERP alert requiring action",
    "repository_access_alert": "A fake alert about repository access or code exposure",
}

PSYCH_PRINCIPLES = [
    "Authority", "Urgency", "Scarcity", "Social Proof",
    "Reciprocity", "Liking", "Fear", "Curiosity",
    "Loss Aversion", "Trust / Familiarity", "FOMO (Fear of Missing Out)"
]


def generate_attack(
    target: TargetProfile,
    attack_type: str,
    api_key: str,
    model: str = "gemini-2.5-flash",
) -> GeneratedAttack:
    """Generate a personalized spear-phishing attack using Gemini API."""
    
    genai.configure(api_key=api_key)
    client = genai.GenerativeModel(model)

    attack_desc = ATTACK_TYPE_DESCRIPTIONS.get(attack_type, "targeted phishing email")
    
    company_context = f"""
Company: {target.company.name or target.company.domain}
Industry: {target.company.industry or 'Unknown'}
Description: {target.company.description or 'N/A'}
Recent news/blog topics: {'; '.join(target.company.recent_news[:3]) or 'None found'}
Technologies detected: {', '.join(target.company.technologies[:5]) or 'None detected'}
Locations: {', '.join(target.company.locations[:2]) or 'Unknown'}
""".strip()

    employee_context = f"""
Target name: {target.employee.name}
Role: {target.employee.role}
Department: {target.employee.department}
Email: {target.employee.email or f"{target.employee.name.split()[0].lower()}@{target.company.domain}"}
Additional context: {target.employee.extra_context or 'None'}
""".strip()

    prompt = f"""You are a cybersecurity red team expert generating a simulated spear-phishing email for security awareness training. This is purely for educational purposes within a controlled security training platform.

Generate a highly convincing, personalized spear-phishing email based on the following:

ATTACK TYPE: {attack_type}
DESCRIPTION: {attack_desc}

TARGET EMPLOYEE:
{employee_context}

TARGET COMPANY:
{company_context}

Requirements:
1. The email must reference SPECIFIC real details about the company and person (not generic)
2. Use industry-appropriate terminology
3. Include a plausible pretext that matches the attack type
4. The sender should be someone the target would trust (colleague, vendor, service they use)
5. Make it time-pressured but not obviously suspicious

Respond ONLY with a valid JSON object in this exact structure:
{{
  "sender_name": "Name the attacker would pose as",
  "sender_email": "spoofed@credible-domain.com",
  "subject": "Email subject line",
  "pretext": "One sentence describing the cover story being used",
  "body": "Full email body text (use \\n for line breaks)",
  "psychological_hooks": ["list", "of", "psych", "principles", "used"],
  "urgency_level": "low|medium|high",
  "sophistication_score": 8,
  "likely_success_rate": "low|medium|high",
  "annotations": [
    {{
      "hook": "psychological principle name",
      "explanation": "Specific sentence from the email and why it works psychologically"
    }}
  ]
}}"""

    response = client.generate_content(prompt)
    raw = response.text.strip()
    
    # Clean up JSON if wrapped in markdown
    raw = re.sub(r'^```json\s*', '', raw)
    raw = re.sub(r'\s*```$', '', raw)
    
    data = json.loads(raw)
    
    return GeneratedAttack(
        attack_type=attack_type,
        subject=data.get("subject", ""),
        body=data.get("body", ""),
        sender_name=data.get("sender_name", ""),
        sender_email=data.get("sender_email", ""),
        pretext=data.get("pretext", ""),
        psychological_hooks=data.get("psychological_hooks", []),
        annotations=data.get("annotations", []),
        urgency_level=data.get("urgency_level", "medium"),
        sophistication_score=data.get("sophistication_score", 7),
        likely_success_rate=data.get("likely_success_rate", "medium"),
    )


def generate_debrief(attack: GeneratedAttack, api_key: str) -> str:
    """Generate a training debrief explaining how to spot this attack."""
    
    genai.configure(api_key=api_key)
    client = genai.GenerativeModel("gemini-2.5-flash")
    
    prompt = f"""You are a cybersecurity awareness trainer. A simulated phishing email was just sent to an employee as a training exercise.

The attack used these psychological principles: {', '.join(attack.psychological_hooks)}
Attack type: {attack.attack_type}
Subject line: {attack.subject}

Write a SHORT, punchy training debrief (4-6 bullet points) that explains:
1. The red flags in this specific email
2. Why it's convincing (what makes it hard to spot)
3. What the employee should have done
4. One key takeaway

Keep it conversational, direct, and under 200 words total. Use plain text with • bullet points."""

    response = client.generate_content(prompt)
    return response.text.strip()
