"""
PhantomTrain - OSINT Profiler
Scrapes publicly available information about a target company and employee.
"""

import requests
from bs4 import BeautifulSoup
import re
from dataclasses import dataclass, field
from typing import Optional
import time


@dataclass
class CompanyProfile:
    domain: str
    name: str = ""
    description: str = ""
    industry: str = ""
    recent_news: list = field(default_factory=list)
    products: list = field(default_factory=list)
    locations: list = field(default_factory=list)
    technologies: list = field(default_factory=list)
    raw_text: str = ""


@dataclass
class EmployeeProfile:
    name: str
    role: str
    department: str
    company: str
    email: str = ""
    linkedin_url: str = ""
    extra_context: str = ""


@dataclass
class TargetProfile:
    employee: EmployeeProfile
    company: CompanyProfile
    attack_surface: list = field(default_factory=list)


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept-Language": "en-US,en;q=0.9",
}

SCRAPE_TIMEOUT = 10

# Keywords to look for when extracting useful company info
TECH_KEYWORDS = [
    "AWS", "Azure", "Google Cloud", "Salesforce", "SAP", "Slack", "Jira",
    "GitHub", "GitLab", "Zoom", "Microsoft 365", "ServiceNow", "Oracle",
    "Kubernetes", "Docker", "Python", "Java", "React", "Node.js"
]

INDUSTRY_KEYWORDS = {
    "finance": ["bank", "financial", "investment", "insurance", "fintech", "payment"],
    "healthcare": ["hospital", "clinic", "medical", "health", "pharma", "biotech"],
    "technology": ["software", "tech", "digital", "AI", "cloud", "SaaS", "platform"],
    "retail": ["retail", "e-commerce", "store", "shop", "consumer", "brand"],
    "manufacturing": ["manufacturing", "industrial", "factory", "production", "supply chain"],
    "education": ["university", "school", "learning", "education", "academy", "training"],
}


def scrape_company_website(domain: str, progress_callback=None) -> CompanyProfile:
    """Scrape key pages from a company's public website."""
    
    # Normalize domain
    if not domain.startswith("http"):
        base_url = f"https://{domain}"
    else:
        base_url = domain
        domain = domain.replace("https://", "").replace("http://", "").split("/")[0]

    profile = CompanyProfile(domain=domain)
    pages_to_scrape = [
        ("", "homepage"),
        ("/about", "about"),
        ("/about-us", "about"),
        ("/company", "company"),
        ("/news", "news"),
        ("/blog", "blog"),
        ("/press", "press"),
        ("/products", "products"),
        ("/services", "services"),
        ("/contact", "contact"),
    ]
    
    all_text = []
    scraped_count = 0

    for path, page_type in pages_to_scrape:
        url = base_url + path
        try:
            if progress_callback:
                progress_callback(f"🔍 Scraping {url}...")
            
            resp = requests.get(url, headers=HEADERS, timeout=SCRAPE_TIMEOUT, allow_redirects=True)
            if resp.status_code != 200:
                continue
            
            soup = BeautifulSoup(resp.text, "html.parser")
            
            # Remove boilerplate tags
            for tag in soup(["script", "style", "nav", "footer", "header", "iframe"]):
                tag.decompose()
            
            text = soup.get_text(separator=" ", strip=True)
            text = re.sub(r'\s+', ' ', text)[:3000]  # Limit per page
            
            all_text.append(f"[{page_type.upper()}] {text}")
            scraped_count += 1
            
            # Extract structured info based on page type
            if page_type == "homepage" or page_type == "about":
                _extract_company_info(soup, text, profile)
            
            if page_type in ("news", "blog", "press"):
                _extract_news(soup, profile)

            time.sleep(0.3)  # Polite delay
            
            if scraped_count >= 4:  # Don't hammer the server
                break
                
        except Exception:
            continue

    profile.raw_text = "\n\n".join(all_text)[:8000]
    
    # Detect technologies
    combined = profile.raw_text.lower()
    profile.technologies = [t for t in TECH_KEYWORDS if t.lower() in combined]
    
    # Detect industry if not set
    if not profile.industry:
        for industry, keywords in INDUSTRY_KEYWORDS.items():
            if any(kw in combined for kw in keywords):
                profile.industry = industry
                break
    
    return profile


def _extract_company_info(soup: BeautifulSoup, text: str, profile: CompanyProfile):
    """Extract company name, description, locations from page soup."""
    
    # Try to get company name from title or og:site_name
    if not profile.name:
        og_site = soup.find("meta", property="og:site_name")
        if og_site:
            profile.name = og_site.get("content", "")
        if not profile.name:
            title = soup.find("title")
            if title:
                profile.name = title.text.split("|")[0].split("-")[0].strip()[:60]

    # Try og:description
    if not profile.description:
        og_desc = soup.find("meta", property="og:description")
        if og_desc:
            profile.description = og_desc.get("content", "")[:300]
        if not profile.description:
            meta_desc = soup.find("meta", attrs={"name": "description"})
            if meta_desc:
                profile.description = meta_desc.get("content", "")[:300]

    # Extract locations via simple pattern matching
    location_pattern = re.compile(
        r'\b(?:headquartered|based|offices?|locations?)\s+in\s+([A-Z][a-zA-Z\s,]+?)(?:\.|,|\band\b)',
        re.IGNORECASE
    )
    matches = location_pattern.findall(text)
    profile.locations.extend([m.strip() for m in matches[:3]])


def _extract_news(soup: BeautifulSoup, profile: CompanyProfile):
    """Extract recent headlines from news/blog pages."""
    headlines = []
    
    for tag in soup.find_all(["h1", "h2", "h3", "h4"]):
        text = tag.get_text(strip=True)
        if 10 < len(text) < 150:
            headlines.append(text)
    
    profile.recent_news.extend(headlines[:5])


def build_attack_surface(profile: TargetProfile) -> list:
    """Identify potential attack vectors based on profile data."""
    vectors = []
    emp = profile.employee
    comp = profile.company

    # Role-based attack vectors
    role_lower = emp.role.lower()
    dept_lower = emp.department.lower()

    if any(k in role_lower for k in ["ceo", "cto", "cfo", "director", "vp", "head", "chief"]):
        vectors.append("executive_impersonation")  # Pretend to be a vendor/partner
        vectors.append("urgent_business_deal")

    if any(k in dept_lower for k in ["finance", "accounting", "payroll"]):
        vectors.append("invoice_fraud")
        vectors.append("wire_transfer_request")

    if any(k in dept_lower for k in ["hr", "human resources", "people", "talent"]):
        vectors.append("employee_data_request")
        vectors.append("fake_job_applicant")

    if any(k in dept_lower for k in ["it", "engineering", "developer", "tech", "devops"]):
        vectors.append("credential_phishing")
        vectors.append("fake_security_alert")
        vectors.append("github_notification")

    if any(k in dept_lower for k in ["sales", "business development", "marketing"]):
        vectors.append("fake_client_inquiry")
        vectors.append("partnership_opportunity")

    # Technology-based vectors
    for tech in comp.technologies:
        if tech in ["Salesforce", "SAP"]:
            vectors.append(f"fake_{tech.lower()}_notification")
        if tech in ["GitHub", "GitLab"]:
            vectors.append("repository_access_alert")
        if tech in ["Slack", "Microsoft 365"]:
            vectors.append("collaboration_tool_phishing")

    # Generic fallbacks
    if not vectors:
        vectors = ["generic_phishing", "account_verification", "security_alert"]

    return vectors[:4]


def create_target_profile(
    employee_name: str,
    role: str,
    department: str,
    company_domain: str,
    employee_email: str = "",
    extra_context: str = "",
    progress_callback=None,
) -> TargetProfile:
    """Full pipeline: scrape company + build employee profile."""

    if progress_callback:
        progress_callback("🕵️ Starting OSINT collection...")

    company = scrape_company_website(company_domain, progress_callback)

    employee = EmployeeProfile(
        name=employee_name,
        role=role,
        department=department,
        company=company.name or company_domain,
        email=employee_email,
        extra_context=extra_context,
    )

    target = TargetProfile(employee=employee, company=company)
    target.attack_surface = build_attack_surface(target)

    if progress_callback:
        progress_callback(f"Profile built. Attack vectors identified: {len(target.attack_surface)}")

    return target
