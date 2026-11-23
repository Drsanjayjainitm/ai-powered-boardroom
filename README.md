# AI-Powered Boardroom

**Interactive Management Strategy and Decision-Making Simulator**

Developed by Dr. Sanjay Jain, Professor, Department of Computer Science & Applications, ITM University Gwalior, India.

## What it does

- CEO Strategy Studio: one-decision sandbox, five advisor perspectives, follow-up dialogue, comparisons, formative feedback.
- CEO Decision Lab: three cumulative revisions of the **same year-one scenario**, financial evidence, five advisors, CEO Mentor, learning analytics, and exports.
- Fictional Aarohan Retail scenario. Financial outputs are deterministic teaching assumptions, **not forecasts**.
- AI-generated coaching is screened; rule-based fallback is labeled. A classroom pilot has **not** been conducted.

## Local setup

```bash
python -m pip install -r requirements.txt
streamlit run app.py
```

Python 3.10+ recommended. Select Demo mode for offline, rule-based testing. Gemini requires an API key; an administrator can configure it in Streamlit Community Cloud **Secrets** (never in GitHub).

## Streamlit Secrets (private, do not commit)

```toml
GEMINI_API_KEY = "your-private-key"
GEMINI_MODEL = "gemini-3.1-flash-lite"
```

The app also offers an optional session-only personal Gemini API key. Google provider limits and charges may apply.

## Deploy

1. Upload the contents of this ZIP's `AI_Boardroom_PromptEd` folder to the repository root.
2. Ensure `.streamlit/config.toml` is included; keep `app.py` as the main Streamlit entrypoint.
3. Configure Secrets in Streamlit Cloud, not in GitHub.
4. Verify both navigation pages, the five-advisor dashboard, CEO Mentor, and exports.

## Scope and privacy

Scenario values are illustrative. Learning rubric scores are formative, not validated competence measurements. The application does not intentionally persist student session data to a database. Do not upload personal or confidential information.
