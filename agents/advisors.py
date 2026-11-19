import os
from agents.grounding import verified_advisor_markdown, qualitative_context, safe_qualitative, fallback_coaching

ADVISOR_BRIEFS = {
    "CFO": "You are the CFO. Focus on budget discipline, profitability, cash flow, ROI, assumptions and financial downside.",
    "CMO": "You are the CMO. Focus on customer segments, pricing, brand, demand generation, retention and marketing effectiveness.",
    "CHRO": "You are the CHRO. Focus on workforce capability, change management, employee engagement, training and responsible leadership.",
    "COO": "You are the COO. Focus on process efficiency, supply chain, service quality, capacity and implementation feasibility.",
    "Risk Officer": "You are the Chief Risk Officer. Focus on strategic, operational, financial, data, privacy, regulatory and reputational risks."
}

def _demo_response(role, decision, result):
    budget = result["investment_lakh"]
    common = f"Proposed investment: ₹{budget:.1f} lakh. Modelled profit: ₹{result['profit_lakh']:.1f} lakh; customer satisfaction: {result['customer_satisfaction']:.0f}/100."
    advice = {
        "CFO": "Check whether the expected incremental contribution can recover the one-time investment. Protect liquidity and compare at least two budget mixes. The simulation is not a cash-flow forecast.",
        "CMO": "Connect marketing spend to measurable customer acquisition, conversion and repeat-purchase targets. Test campaigns in a limited segment before scaling.",
        "CHRO": "Pair technology and process changes with employee training and clear communication. Monitor workload, adoption and employee feedback.",
        "COO": "Sequence technology changes with store and supply-chain readiness. Define service-level, inventory accuracy and fulfilment measures.",
        "Risk Officer": "Stress-test demand assumptions, protect customer data, review vendor access and maintain human oversight of AI-supported decisions."
    }
    return common + "\n\n" + advice[role]

def _call_openai(system_prompt, user_prompt, api_key, model):
    from openai import OpenAI
    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model=model or "gpt-4o-mini",
        messages=[{"role":"system","content":system_prompt},
                  {"role":"user","content":user_prompt}],
        temperature=0.4
    )
    return response.choices[0].message.content

def _call_gemini(system_prompt, user_prompt, api_key, model):
    from google import genai
    client = genai.Client(api_key=api_key)
    response = client.models.generate_content(
        model=model or "gemini-2.0-flash",
        contents=system_prompt + "\n\n" + user_prompt
    )
    return response.text

def _safe_provider_error(exc):
    """Classify cloud failures without disclosing credentials or raw responses."""
    code = getattr(exc, "status_code", None) or getattr(exc, "code", None)
    if code == 400:
        return "Invalid API request or model configuration (HTTP 400)"
    if code == 401 or code == 403:
        return "API key or project permission rejected (HTTP 401/403)"
    if code == 404:
        return "Model not found or unavailable to this project (HTTP 404)"
    if code == 429:
        return "API rate limit or quota reached (HTTP 429)"
    if isinstance(code, int) and code >= 500:
        return "AI provider temporarily unavailable (HTTP 5xx)"
    return "AI provider request failed (" + type(exc).__name__ + ")"

def _call_ollama(system_prompt, user_prompt, model="llama3.2:1b", base_url="http://localhost:11434"):
    """Use Ollama's local HTTP API. No cloud key or Python Ollama package required."""
    import json
    from urllib.request import Request, urlopen
    from urllib.error import HTTPError, URLError
    endpoint = base_url.rstrip("/") + "/api/chat"
    payload = {
        "model": model or "llama3.2:1b", "stream": False,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "options": {"temperature": 0.3, "num_ctx": 2048, "num_predict": 350},
        "keep_alive": "2m",
    }
    req = Request(endpoint, data=json.dumps(payload).encode("utf-8"),
                  headers={"Content-Type": "application/json"}, method="POST")
    try:
        with urlopen(req, timeout=180) as response:
            data = json.load(response)
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:300]
        raise RuntimeError(f"Ollama HTTP {exc.code}: {detail}") from exc
    except (URLError, TimeoutError) as exc:
        raise RuntimeError("Cannot reach local Ollama. Start Ollama and check http://localhost:11434") from exc
    answer = data.get("message", {}).get("content", "").strip()
    if not answer:
        raise RuntimeError("Ollama returned an empty answer. Try another installed model.")
    return answer

def get_advisor_recommendations(role, decision, result, provider="Demo mode (no API key)", api_key="", model=""):
    if role not in ADVISOR_BRIEFS:
        raise ValueError("Unknown advisor role")
    if provider == "Demo mode (no API key)":
        return _demo_response(role, decision, result)
    evidence = verified_advisor_markdown(decision, result)
    if provider in ("OpenAI", "Google Gemini") and not api_key:
        return evidence + "\n\nEnter a provider API key, or choose Ollama for local inference."
    system_prompt = (
        ADVISOR_BRIEFS[role] + "\nYou are an educational coach. All numerical and decision facts "
        "are displayed separately by Python. Provide ONLY qualitative coaching, "
        "without numerical claims, financial terms, selected decision descriptions, "
        "or causal claims. Ask one probing classroom question. Keep it under 100 words."
    )
    user_prompt = qualitative_context(decision, result) + "\nProvide concise qualitative coaching."
    try:
        if provider == "Ollama (local, free)":
            response = _call_ollama(system_prompt, user_prompt, model)
        elif provider == "OpenAI":
            response = _call_openai(system_prompt, user_prompt, api_key, model)
        elif provider == "Google Gemini":
            response = _call_gemini(system_prompt, user_prompt, api_key, model)
        else:
            return evidence + "\n\nUnsupported provider selection."
        safe = safe_qualitative(response)
        return evidence + "\n\n" + ("**AI-generated qualitative coaching (screened)**\n\n" + safe if safe else fallback_coaching(role))
    except Exception as exc:
        return evidence + f"\n\n**AI unavailable: {_safe_provider_error(exc)}; rule-based coaching shown.**\n\n" + fallback_coaching(role)
