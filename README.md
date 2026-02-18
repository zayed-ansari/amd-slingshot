# 🎯 PhantomTrain

> AI-powered social engineering simulation platform for security awareness training.  
> Built for **AMD Slingshot 2026** | Challenge: AI + Cybersecurity & Privacy

---

## What it does

PhantomTrain simulates the exact process real attackers use — scraping public data about your company and employees, then generating hyper-personalized phishing emails — so your organization can train against *realistic* attacks, not generic templates.

---

## Quickstart

### 1. Clone & setup

```bash
cd phantomtrain
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure API key

```bash
cp .env.example .env
# Edit .env and add your Google Gemini API key
```

Or just paste it directly in the sidebar when the app loads.

### 3. Run

```bash
streamlit run app.py
```

App will open at `http://localhost:8501`

---

## How to use

1. **New Simulation** → Enter a company domain + employee details + attack type → click Run
2. View the generated phishing email with psychological annotations
3. Check the risk score and training recommendations
4. **Campaign Dashboard** → Run multiple simulations to see org-wide risk heatmap

---

## Project structure

```
phantomtrain/
├── app.py                  ← Streamlit UI (main entry point)
├── modules/
│   ├── osint.py            ← Web scraper & profile builder
│   ├── generator.py        ← Gemini API attack generator
│   └── scorer.py           ← Risk scoring engine
├── requirements.txt
├── .env.example
└── README.md
```

---

## Tech stack

| Component | Technology |
|-----------|-----------|
| UI | Streamlit |
| AI Generation | Google Gemini API |
| OSINT Scraping | BeautifulSoup + Requests |
| Risk Scoring | Custom Python engine |
| AMD Production Story | ROCm + local LLM (Mistral 7B via Ollama) |

---

## ⚠️ Ethical use

For authorized security training only. Never run against targets without explicit consent.

---

*AMD Slingshot 2026*
