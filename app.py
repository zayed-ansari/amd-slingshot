"""
PhantomTrain — AI-Powered Social Engineering Simulation Platform
AMD Slingshot Hackathon | AI + Cybersecurity & Privacy Track
"""

import streamlit as st
import json
import time
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

# ── Page config ─────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="PhantomTrain",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
  /* Dark header */
  [data-testid="stAppViewContainer"] { background: #0f1117; }
  [data-testid="stSidebar"] { background: #1a1d2e; }

  .phantom-logo {
    font-size: 2rem; font-weight: 900; letter-spacing: -1px;
    color: #ffffff;
  }
  .phantom-logo span { color: #ff4b4b; }

  .risk-badge {
    display: inline-block; padding: 4px 14px; border-radius: 20px;
    font-weight: 700; font-size: 0.85rem; letter-spacing: 0.5px;
  }
  .badge-critical { background: #ff2e2e22; color: #ff2e2e; border: 1px solid #ff2e2e; }
  .badge-high { background: #ff6b3522; color: #ff6b35; border: 1px solid #ff6b35; }
  .badge-medium { background: #ffb34722; color: #ffb347; border: 1px solid #ffb347; }
  .badge-low { background: #4caf5022; color: #4caf50; border: 1px solid #4caf50; }

  .email-container {
    background: #1e2130; border: 1px solid #2d3252; border-radius: 12px;
    padding: 24px; font-family: 'Courier New', monospace; font-size: 0.88rem;
    line-height: 1.7; color: #c9d1d9;
  }
  .email-header { color: #8b949e; font-size: 0.8rem; margin-bottom: 16px; }
  .email-subject { color: #f0f6fc; font-size: 1rem; font-weight: 700; margin-bottom: 12px; }
  .email-body { white-space: pre-wrap; }

  .annotation-card {
    background: #161b2e; border-left: 3px solid #ff4b4b;
    border-radius: 0 8px 8px 0; padding: 12px 16px; margin: 8px 0;
  }
  .hook-label {
    color: #ff4b4b; font-weight: 700; font-size: 0.8rem;
    text-transform: uppercase; letter-spacing: 1px;
  }

  .score-ring {
    text-align: center; padding: 20px;
    background: #1a1d2e; border-radius: 16px;
  }
  .score-number { font-size: 3.5rem; font-weight: 900; line-height: 1; }

  .stat-card {
    background: #1a1d2e; border: 1px solid #2d3252;
    border-radius: 12px; padding: 16px; text-align: center;
  }
  .stat-number { font-size: 2rem; font-weight: 900; color: #ff4b4b; }
  .stat-label { font-size: 0.8rem; color: #8b949e; text-transform: uppercase; letter-spacing: 1px; }

  .target-row {
    background: #1a1d2e; border: 1px solid #2d3252; border-radius: 10px;
    padding: 14px 18px; margin: 8px 0;
    display: flex; align-items: center; gap: 16px;
  }

  /* Override Streamlit metric */
  [data-testid="stMetricValue"] { font-size: 2rem !important; color: #ff4b4b !important; }

  /* Button styling */
  .stButton button {
    background: #ff4b4b !important; color: white !important;
    border: none !important; font-weight: 700 !important;
    border-radius: 8px !important;
  }

  div[data-testid="stExpander"] {
    background: #1a1d2e; border: 1px solid #2d3252 !important; border-radius: 10px;
  }
</style>
""", unsafe_allow_html=True)


# ── Session state ────────────────────────────────────────────────────────────
if "campaign_results" not in st.session_state:
    st.session_state.campaign_results = []
if "current_attack" not in st.session_state:
    st.session_state.current_attack = None
if "current_target" not in st.session_state:
    st.session_state.current_target = None
if "current_score" not in st.session_state:
    st.session_state.current_score = None
if "api_key" not in st.session_state:
    st.session_state.api_key = os.getenv("GEMINI_API_KEY", "")


# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="phantom-logo">Phantom<span>Train</span></div>', unsafe_allow_html=True)
    st.caption("AI-Powered Security Simulation Platform")
    st.divider()

    page = st.radio(
        "Navigation",
        ["🎯 New Simulation", "📊 Campaign Dashboard", "ℹ️ About"],
        label_visibility="collapsed"
    )

    st.divider()
    st.markdown("**🔑 API Configuration**")
    api_key_input = st.text_input(
        "Gemini API Key",
        value=st.session_state.api_key,
        type="password",
        placeholder="AIza...",
        help="Your Google Gemini API key. Never stored — stays in session only."
    )
    if api_key_input:
        st.session_state.api_key = api_key_input

    if st.session_state.api_key:
        st.success("API key loaded ✓")
    else:
        st.warning("Add API key to run simulations")

    st.divider()
    st.caption("⚠️ For authorized security training only. All simulations are for educational purposes.")


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: New Simulation
# ══════════════════════════════════════════════════════════════════════════════
if "New Simulation" in page:

    st.markdown("## New Phishing Simulation")
    st.caption("Generate a personalized spear-phishing simulation from publicly available information")

    col1, col2 = st.columns([1, 1], gap="large")

    with col1:
        st.markdown("### 🏢 Company Target")
        company_domain = st.text_input(
            "Company Domain",
            placeholder="example.com",
            help="Public website of the target company. Will be scraped for OSINT."
        )
        st.markdown("### 👤 Employee Target")
        emp_name = st.text_input("Full Name", placeholder="Alex Johnson")
        
        col_a, col_b = st.columns(2)
        with col_a:
            emp_role = st.text_input("Job Title", placeholder="Senior Accountant")
        with col_b:
            emp_dept = st.text_input("Department", placeholder="Finance")
        
        emp_email = st.text_input(
            "Work Email (optional)",
            placeholder="alex@example.com",
            help="If left blank, will be inferred from name + domain"
        )
        emp_context = st.text_area(
            "Additional Context (optional)",
            placeholder="Recently promoted, just announced a new product launch, attending a conference next week...",
            height=80,
            help="Any extra public info that could make the attack more personalized"
        )

    with col2:
        st.markdown("### ⚙️ Attack Configuration")
        attack_options = {
            "🎣 Credential Phishing": "credential_phishing",
            "💸 Invoice Fraud": "invoice_fraud",
            "👔 Executive Impersonation": "executive_impersonation",
            "🚨 Fake Security Alert": "fake_security_alert",
            "🤝 Partnership Opportunity": "partnership_opportunity",
            "💼 Fake Client Inquiry": "fake_client_inquiry",
            "🏦 Wire Transfer Request": "wire_transfer_request",
            "🐙 GitHub/Repository Alert": "repository_access_alert",
            "💬 Collaboration Tool Phishing": "collaboration_tool_phishing",
            "📋 Employee Data Request": "employee_data_request",
        }
        selected_label = st.selectbox(
            "Attack Type",
            list(attack_options.keys()),
            help="The type of social engineering attack to simulate"
        )
        attack_type = attack_options[selected_label]

        st.markdown("### AI Model")
        model_choice = st.selectbox(
            "Generation Model",
            ["gemini-2.5-flash"],
            help="Pro = highest quality, Flash = faster & cheaper"
        )

        st.markdown("---")
        st.markdown("**What happens when you run:**")
        st.markdown("""
        1. 🔍 OSINT scraping of company website
        2. 🧩 Employee profile construction  
        3. 🤖 AI generates personalized attack
        4. 🧠 Psychological annotation
        5. 📊 Risk score calculation
        """)

    # ── Run Button ────────────────────────────────────────────────────────────
    st.markdown("---")
    run_col, _ = st.columns([1, 3])
    with run_col:
        run_btn = st.button("Run Simulation", use_container_width=True)

    if run_btn:
        # Validation
        errors = []
        if not company_domain:
            errors.append("Company domain is required")
        if not emp_name:
            errors.append("Employee name is required")
        if not emp_role:
            errors.append("Job title is required")
        if not emp_dept:
            errors.append("Department is required")
        if not st.session_state.api_key:
            errors.append("API key is required (see sidebar)")

        if errors:
            for e in errors:
                st.error(f"❌ {e}")
        else:
            # Run the simulation
            from modules.osint import create_target_profile
            from modules.generator import generate_attack, generate_debrief
            from modules.scorer import score_target, CampaignResult

            progress_placeholder = st.empty()
            status_log = []

            def update_progress(msg):
                status_log.append(msg)
                progress_placeholder.info("\n".join(status_log[-3:]))

            try:
                with st.spinner("Running simulation..."):
                    # Step 1: OSINT
                    update_progress("Starting OSINT collection...")
                    target = create_target_profile(
                        employee_name=emp_name,
                        role=emp_role,
                        department=emp_dept,
                        company_domain=company_domain,
                        employee_email=emp_email,
                        extra_context=emp_context,
                        progress_callback=update_progress,
                    )

                    # Step 2: Generate attack
                    update_progress("Generating personalized attack via AI...")
                    attack = generate_attack(
                        target=target,
                        attack_type=attack_type,
                        api_key=st.session_state.api_key,
                        model=model_choice,
                    )

                    # Step 3: Score
                    update_progress("Calculating risk score...")
                    score = score_target(target, attack)

                    # Step 4: Store in campaign
                    result = CampaignResult(
                        target_name=emp_name,
                        role=emp_role,
                        department=emp_dept,
                        attack_type=attack_type,
                        risk_score=score,
                        attack=attack,
                        status="sent",
                    )
                    st.session_state.campaign_results.append(result)
                    st.session_state.current_attack = attack
                    st.session_state.current_target = target
                    st.session_state.current_score = score

                    progress_placeholder.empty()

            except Exception as e:
                progress_placeholder.empty()
                st.error(f"❌ Simulation failed: {str(e)}")
                st.stop()

    # ── Results ───────────────────────────────────────────────────────────────
    if st.session_state.current_attack:
        attack = st.session_state.current_attack
        target = st.session_state.current_target
        score = st.session_state.current_score

        st.success("Simulation complete!")
        st.markdown("---")
        st.markdown("## Generated Attack")

        # Top row: score + meta
        score_col, meta_col = st.columns([1, 3])
        
        with score_col:
            color = score.color
            st.markdown(f"""
            <div class="score-ring">
                <div class="score-number" style="color:{color}">{score.overall}</div>
                <div style="color:#8b949e; font-size:0.8rem; margin-top:4px;">RISK SCORE</div>
                <div class="risk-badge badge-{score.label.lower()}" style="margin-top:8px">{score.label.upper()}</div>
            </div>
            """, unsafe_allow_html=True)

        with meta_col:
            st.markdown(f"""
            **Target:** {target.employee.name} — {target.employee.role}, {target.employee.department}  
            **Company:** {target.company.name or target.company.domain}  
            **Attack type:** `{attack.attack_type}`  
            **Sender posing as:** {attack.sender_name} `<{attack.sender_email}>`  
            **Pretext:** {attack.pretext}  
            **Urgency:** `{attack.urgency_level.upper()}`  &nbsp; **Sophistication:** {attack.sophistication_score}/10  
            **Likely success rate:** `{attack.likely_success_rate.upper()}`
            """)

            if target.company.technologies:
                st.markdown(f"**Technologies detected:** {', '.join(target.company.technologies[:5])}")

        st.markdown("---")

        # Email preview
        st.markdown("### ✉️ Phishing Email")
        st.markdown(f"""
        <div class="email-container">
            <div class="email-header">
                <strong>From:</strong> {attack.sender_name} &lt;{attack.sender_email}&gt;<br>
                <strong>To:</strong> {target.employee.email or f"{target.employee.name.split()[0].lower()}@{target.company.domain}"}<br>
                <strong>Date:</strong> {datetime.now().strftime("%a, %d %b %Y %H:%M")}
            </div>
            <div class="email-subject">📧 {attack.subject}</div>
            <div class="email-body">{attack.body.replace(chr(10), "<br>")}</div>
        </div>
        """, unsafe_allow_html=True)

        # Psychological annotations
        st.markdown("### 🧠 Psychological Annotations")
        st.caption("This section reveals the manipulation techniques embedded in the email")
        
        hooks_col, annotations_col = st.columns([1, 2])
        
        with hooks_col:
            st.markdown("**Hooks used:**")
            for hook in attack.psychological_hooks:
                st.markdown(f"🔴 **{hook}**")

        with annotations_col:
            for ann in attack.annotations:
                st.markdown(f"""
                <div class="annotation-card">
                    <div class="hook-label">⚠️ {ann.get('hook', '')}</div>
                    <div style="color:#c9d1d9; margin-top:6px; font-size:0.9rem">{ann.get('explanation', '')}</div>
                </div>
                """, unsafe_allow_html=True)

        # Risk breakdown
        st.markdown("### 📊 Risk Score Breakdown")
        breakdown_cols = st.columns(len(score.breakdown))
        labels = {
            "attack_sophistication": "Attack Sophistication",
            "psychological_hooks": "Psych. Hook Power",
            "department_sensitivity": "Dept. Sensitivity",
            "urgency": "Urgency Level",
            "company_exposure": "Company Data Exposure",
        }
        for i, (key, val) in enumerate(score.breakdown.items()):
            with breakdown_cols[i]:
                st.metric(labels.get(key, key), f"{val}")

        # Recommendations
        st.markdown("### Training Recommendations")
        for rec in score.recommendations:
            st.markdown(f"{rec}")

        # Debrief
        st.markdown("### 🎓 Post-Simulation Debrief")
        with st.expander("Generate Employee Debrief (click to expand)", expanded=False):
            if st.button("Generate Debrief Now"):
                with st.spinner("Generating training debrief..."):
                    from modules.generator import generate_debrief
                    debrief = generate_debrief(attack, st.session_state.api_key)
                    st.markdown(debrief)


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: Campaign Dashboard
# ══════════════════════════════════════════════════════════════════════════════
elif "Campaign Dashboard" in page:
    st.markdown("## 📊 Campaign Dashboard")

    results = st.session_state.campaign_results

    if not results:
        st.info("Run a simulation first to see your campaign dashboard here.")
    else:
        from modules.scorer import org_risk_summary

        summary = org_risk_summary(results)

        # Top stats
        st.markdown("### Org-Wide Risk Summary")
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-number">{summary['total_targets']}</div>
                <div class="stat-label">Targets Simulated</div>
            </div>""", unsafe_allow_html=True)
        with c2:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-number">{summary['avg_risk']}</div>
                <div class="stat-label">Avg Risk Score</div>
            </div>""", unsafe_allow_html=True)
        with c3:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-number">{summary['critical_count']}</div>
                <div class="stat-label">Critical Risk Targets</div>
            </div>""", unsafe_allow_html=True)
        with c4:
            st.markdown(f"""
            <div class="stat-card">
                <div class="stat-number">{summary['highest_risk_dept']}</div>
                <div class="stat-label">Highest Risk Dept</div>
            </div>""", unsafe_allow_html=True)

        st.markdown("---")

        # Department risk chart
        if summary.get("department_risks"):
            st.markdown("### Department Risk Heatmap")
            dept_data = summary["department_risks"]
            
            import json
            dept_json = json.dumps(dept_data)
            
            # Simple bar visualization using st.progress
            for dept, risk in sorted(dept_data.items(), key=lambda x: -x[1]):
                col_label, col_bar, col_score = st.columns([2, 6, 1])
                with col_label:
                    st.write(dept)
                with col_bar:
                    color = "#ff2e2e" if risk >= 80 else "#ff6b35" if risk >= 60 else "#ffb347" if risk >= 40 else "#4caf50"
                    st.markdown(f"""
                    <div style="background:{color}22; border-radius:4px; height:24px; width:{risk}%; 
                    border-left:3px solid {color}; margin-top:6px;"></div>
                    """, unsafe_allow_html=True)
                with col_score:
                    st.write(f"**{risk}**")

        st.markdown("---")

        # Target list
        st.markdown("### Target Details")
        for r in reversed(results):
            badge_class = f"badge-{r.risk_score.label.lower()}"
            with st.expander(
                f"{'🔴' if r.risk_score.label == 'Critical' else '🟠' if r.risk_score.label == 'High' else '🟡' if r.risk_score.label == 'Medium' else '🟢'} "
                f"{r.target_name} — {r.role} ({r.department}) | Risk: {r.risk_score.overall}/100",
                expanded=False
            ):
                col_a, col_b = st.columns([1, 2])
                with col_a:
                    st.markdown(f"**Attack type:** `{r.attack_type}`")
                    st.markdown(f"**Risk label:** `{r.risk_score.label}`")
                    st.markdown(f"**Urgency:** `{r.attack.urgency_level}`")
                    st.markdown(f"**Success rate:** `{r.attack.likely_success_rate}`")
                with col_b:
                    st.markdown(f"**Psychological hooks:** {', '.join(r.attack.psychological_hooks)}")
                    st.markdown("**Training recommendations:**")
                    for rec in r.risk_score.recommendations:
                        st.markdown(f"  • {rec}")
                
                st.markdown("**Email Subject:**")
                st.code(r.attack.subject)

        # Export
        st.markdown("---")
        if st.button("📥 Export Campaign Report (JSON)"):
            export_data = []
            for r in results:
                export_data.append({
                    "target": r.target_name,
                    "role": r.role,
                    "department": r.department,
                    "attack_type": r.attack_type,
                    "risk_score": r.risk_score.overall,
                    "risk_label": r.risk_score.label,
                    "psychological_hooks": r.attack.psychological_hooks,
                    "email_subject": r.attack.subject,
                    "recommendations": r.risk_score.recommendations,
                })
            st.download_button(
                "⬇️ Download JSON",
                data=json.dumps(export_data, indent=2),
                file_name=f"phantomtrain_campaign_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
                mime="application/json",
            )


# ══════════════════════════════════════════════════════════════════════════════
# PAGE: About
# ══════════════════════════════════════════════════════════════════════════════
elif "About" in page:
    st.markdown("## About PhantomTrain")
    
    st.markdown("""
    **PhantomTrain** is an AI-powered offensive security training platform built for AMD Slingshot 2025.

    ### What it does
    PhantomTrain simulates the exact reconnaissance and attack generation process that real threat actors use — 
    but in a safe, controlled, educational environment. By showing organizations exactly how vulnerable they are 
    to personalized social engineering, it drives real behavioral change.

    ### How it works
    1. **OSINT Collection** — Scrapes the target company's public website for context (news, products, technology stack, locations)
    2. **Profile Building** — Constructs a threat profile combining company and employee data
    3. **AI Attack Generation** — Uses Claude AI to generate a hyper-personalized spear-phishing email or script
    4. **Psychological Annotation** — Tags every manipulation technique used (Authority, Urgency, Fear, etc.)
    5. **Risk Scoring** — Quantifies how vulnerable the target is based on role, department, and attack sophistication
    6. **Training Debrief** — Generates targeted training content explaining exactly how to spot the attack

    ### Tech Stack
    - **Frontend:** Streamlit
    - **AI Generation:** Google Gemini API (gemini-2.5-flash)
    - **OSINT:** Scrapy / BeautifulSoup / Requests
    - **Backend:** Python 3.11 + FastAPI (production)
    - **AMD Story:** Designed for local deployment on AMD Instinct MI-series via ROCm — zero cloud dependency for enterprise use

    ### Ethical Use
    PhantomTrain is built exclusively for:
    - Authorized security awareness training
    - Red team exercises with explicit organizational consent
    - Educational demonstrations of social engineering techniques
    
    All simulations are for training purposes only. Never use against unauthorized targets.
    
    ---
    *Built for AMD Slingshot 2025 | Challenge: AI + Cybersecurity & Privacy*
    """)
