"""Role-specific follow-up questions. Demo is deterministic; live responses require API access."""
import re
from agents.advisors import ADVISOR_BRIEFS, _call_openai, _call_gemini, _call_ollama, _safe_provider_error
from agents.grounding import verified_advisor_markdown, qualitative_context, safe_qualitative, fallback_coaching

def _demo_answer(role, question, decision, result):
    q = question.lower()
    evidence = (
        f"Investment ₹{result['investment_lakh']:.1f} lakh; "
        f"year-one profit ₹{result['profit_lakh']:.1f} lakh; "
        f"revenue change {result['revenue_change_pct']:+.1f}%; "
        f"risk {result['risk_level']}."
    )
    topics = {
        "CFO": ("The model charges the full investment in year one. Compare the profit effect against the ₹40 lakh baseline and keep a liquidity reserve.",
                "What would happen to profit if revenue lift were 25% lower?"),
        "CMO": ("Pilot marketing campaigns with tracked conversion and repeat-purchase measures before increasing spend.",
                "What measurable customer segment and acquisition target will you prioritize?"),
        "CHRO": ("Assign change champions, schedule practical training, and measure adoption alongside service quality.",
                 "How will you know employees can use the new systems confidently?"),
        "COO": ("Phase rollout, check inventory accuracy, and track fulfilment time and operational savings.",
                "What operational bottleneck would you fix first?"),
        "Risk Officer": ("Test a lower-demand scenario, set data-access safeguards, and require human review of major decisions.",
                         "What is your contingency if the expected revenue lift does not materialize?")
    }
    suggestion, challenge = topics[role]
    if any(w in q for w in ("profit", "roi", "payback", "cash")):
        suggestion += " Simple investment recovery proxy: compare modelled profit before the one-time investment with baseline profit; this is not a cash-flow ROI."
    if any(w in q for w in ("risk", "downside", "fail", "uncertain")):
        suggestion += " Treat all outcomes as assumptions, not guaranteed forecasts."
    return f"**{role} response (rule-based demo)**\n\n{evidence}\n\n{suggestion}\n\n**Challenge for the CEO:** {challenge}"

def ask_advisor(role, question, decision, result, provider, api_key="", model="", history=None):
    if role not in ADVISOR_BRIEFS:
        raise ValueError("Unknown advisor role")
    question = question.strip()[:1200]
    if not question:
        raise ValueError("Enter a question for the advisor")
    if provider == "Demo mode (no API key)":
        return _demo_answer(role, question, decision, result)
    evidence = verified_advisor_markdown(decision, result)
    if provider in ("OpenAI", "Google Gemini") and not api_key:
        return evidence + "\n\nAn API key is required for live AI."
    context = (ADVISOR_BRIEFS[role] + "\nAct as a classroom coach, not a financial calculator. "
               "Python separately supplies all verified case facts. Answer with conceptual teaching guidance "
               "only. Do not mention numbers, financial quantities, business results, or decision changes. "
               "Ask a thought-provoking question. Under 100 words.")
    prompt = qualitative_context(decision, result) + "\nLearner question: " + question
    try:
        if provider == "Ollama (local, free)":
            response = _call_ollama(context, prompt, model)
        elif provider == "OpenAI":
            response = _call_openai(context, prompt, api_key, model)
        elif provider == "Google Gemini":
            response = _call_gemini(context, prompt, api_key, model)
        else:
            return evidence + "\n\nUnsupported AI provider."
        safe = safe_qualitative(response)
        return evidence + "\n\n" + ("**AI-generated qualitative coaching (screened)**\n\n" + safe if safe else fallback_coaching(role, question))
    except Exception as exc:
        return evidence + f"\n\n**AI unavailable ({_safe_provider_error(exc)}); rule-based coaching shown.**\n\n" + fallback_coaching(role, question)
