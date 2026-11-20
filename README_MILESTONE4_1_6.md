# Milestone 4.1.6 — AI Response Sanitization and CEO Mentor Reliability

This release builds on the complete Milestone 4.1.5 application.

## Improvements
- Strip fenced and common unfenced Python/JSON snippets from advisor narrative before displaying it. Unclear or unsafe responses still fall back to role-specific rule-based coaching.
- Strengthen natural-language-only instructions for all advisors and the CEO Mentor.
- Accept common Gemini variations of the three CEO Mentor section headings, while filtering numeric claims and preserving deterministic financial evidence and action items.
- Clarify that the simulation's one-time investment is deducted from year-one profit; unverified operating-cost explanations must not be stated as facts.
- Add five regression tests for code leakage, numeric safeguards and mentor headings.

## Files changed from 4.1.5
- agents/grounding.py
- agents/advisors.py
- agents/dialogue.py
- agents/ceo_mentor.py
- tests/test_milestone_4_1_6.py (new)
- README_MILESTONE4_1_6.md (new)

## Deployment
Upload the four changed Python files into their matching GitHub folders. The new test and README are optional for deployment. Do not upload a Streamlit Secrets file or API key. Reboot Streamlit if necessary.

## Validation
42 local automated tests pass; Python compileall passes. Live Gemini behavior and CEO Mentor acceptance still require user verification on Streamlit Cloud. This patch does not guarantee every provider response will be accepted; unsafe content intentionally triggers fallback.
