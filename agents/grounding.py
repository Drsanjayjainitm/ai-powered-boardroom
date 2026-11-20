"""Grounded advisory facts and conservative narrative gate for small local models."""
import re

BASE_REVENUE_LAKH = 250.0
BASE_PROFIT_LAKH = 40.0
BUDGET_LAKH = 50.0


def verified_advisor_facts(decision, result):
    revenue = float(result['revenue_crore']) * 100
    profit = float(result['profit_lakh'])
    invested = float(result['investment_lakh'])
    return {
        'revenue_lakh': round(revenue, 2),
        'revenue_delta_lakh': round(revenue - BASE_REVENUE_LAKH, 2),
        'profit_lakh': round(profit, 2),
        'profit_delta_lakh': round(profit - BASE_PROFIT_LAKH, 2),
        'investment_lakh': round(invested, 2),
        'remaining_lakh': round(BUDGET_LAKH - invested, 2),
        'satisfaction': round(float(result['customer_satisfaction']), 2),
        'risk': str(result['risk_level']),
        'pricing': str(decision['pricing']),
        'operations': str(decision['operations']),
    }


def _direction(value):
    return 'increased' if value > 0.005 else 'decreased' if value < -0.005 else 'was unchanged'


def verified_advisor_markdown(decision, result):
    f = verified_advisor_facts(decision, result)
    return ("**Verified scenario evidence (Python-calculated)**\n\n"
            f"- Revenue: **₹{f['revenue_lakh']:.2f} lakh**, {_direction(f['revenue_delta_lakh'])} "
            f"by **₹{abs(f['revenue_delta_lakh']):.2f} lakh** versus baseline.\n"
            f"- Year-one profit after investment: **₹{f['profit_lakh']:.2f} lakh**, "
            f"{_direction(f['profit_delta_lakh'])} by **₹{abs(f['profit_delta_lakh']):.2f} lakh** versus baseline.\n"
            f"- Investment: **₹{f['investment_lakh']:.2f} lakh**; unallocated budget: "
            f"**₹{f['remaining_lakh']:.2f} lakh**. The unallocated budget is not a profit expense.\n"
            f"- Satisfaction: **{f['satisfaction']:.1f}/100**; modelled risk: **{f['risk']}**.\n"
            f"- Pricing: **{f['pricing']}**; operations: **{f['operations']}**.\n\n"
            "*Illustrative model outputs, not real-world forecasts.*")


def qualitative_context(decision, result):
    f = verified_advisor_facts(decision, result)
    return (f"VERIFIED TRENDS: revenue {_direction(f['revenue_delta_lakh'])} versus baseline; "
            f"profit {_direction(f['profit_delta_lakh'])} versus baseline; "
            f"remaining budget is nonnegative; risk category is {f['risk']}. "
            f"Pricing selected: {f['pricing']}. Operations selected: {f['operations']}. "
            "The budget reserve does NOT cause the modelled profit decline. "
            "The one-time investment is deducted from year-one profit. "
            "Do not invent decision changes or causal explanations. Do not compute figures.")


# Financial vocabulary is normal in management coaching. Reject invented figures,
# not words such as "profit" or "risk"; Python alone supplies numeric evidence.
def sanitize_ai_prose(text):
    """Remove model-generated code artifacts, without silently rewriting financial claims.

    Return None if code is interleaved with prose in an unsafe or ambiguous way.
    """
    if not isinstance(text, str):
        return None
    # Remove complete fenced code blocks (including malformed open fences).
    text = re.sub(r'```[^\n]*\n.*?(?:```|\Z)', '', text, flags=re.S)
    text = re.sub(r'~~~[^\n]*\n.*?(?:~~~|\Z)', '', text, flags=re.S)
    lines = []
    in_code = False
    for line in text.splitlines():
        t = line.strip()
        if not t:
            if not in_code:
                lines.append('')
            continue
        # A generated Python/JSON snippet can be unfenced and embedded in Markdown.
        if re.match(r'^(?:#\s*(?:decision|financial|numerical|verified|data|facts|trend)|'
                    r'(?:from|import)\s+\w+|(?:print|json\.dumps)\s*\(|'
                    r'[A-Za-z_][\w]*\s*=\s*(?:\{|\[|[\"\']|\w+\())', t, re.I):
            in_code = True
            continue
        if in_code:
            if (t in ('}', ']', '},', '],') or
                re.match(r'^[\[\]{}(),]*$', t) or
                re.match(r'^[\"\'][^\"\']+[\"\']\s*:', t) or
                re.match(r'^[A-Za-z_][\w]*\s*=', t)):
                continue
            in_code = False
        if (re.match(r'^[\[\]{}(),]*$', t) or
            re.match(r'^[\"\'][^\"\']+[\"\']\s*:', t) or
            re.match(r'^(?:print\(|(?:data|facts|trends|metrics|decisions)\s*=)', t)):
            continue
        lines.append(line)
    cleaned = '\n'.join(lines).strip()
    if re.search(r'(?m)^\s*(?:def |class |for .*:|if .*:|print\(|\w+\s*=\s*\{|[{}])', cleaned):
        return None
    return cleaned or None


def safe_qualitative(text):
    """Screen coaching prose; Python alone owns numerical evidence."""
    cleaned = sanitize_ai_prose(text)
    if not cleaned or len(cleaned) < 35 or len(cleaned.split()) > 180:
        return None
    if re.search(r'[0-9₹%$]', cleaned):
        return None
    if re.search(r'\bprofit (?:declined|fell|decreased) because of (?:the )?reserve\b', cleaned, re.I):
        return None
    if re.search(r'\b(?:you (?:chose|selected|changed|increased|decreased|allocated)|'
                 r'you(?:r company)? (?:earned|spent|invested)|'
                 r'budget (?:was|is) exceeded|guaranteed (?:return|profit))\b', cleaned, re.I):
        return None
    return cleaned


def fallback_coaching(role, question=''):
    prompts = {
        'CFO': 'What evidence would you use to judge whether this strategy offers acceptable value for the company?',
        'CMO': 'Which customer segment and measurable experiment would you prioritize?',
        'CHRO': 'How would you check employee readiness and adoption?',
        'COO': 'Which service-quality indicator would you monitor during implementation?',
        'Risk Officer': 'Which assumption would you challenge before approving the strategy?',
    }
    guidance = {
        'CFO': 'Separate the underlying operating contribution from one-time implementation spending. Examine payback assumptions and whether a phased commitment would protect flexibility.',
        'CMO': 'Choose a customer segment, define a measurable conversion or retention target, and compare a small campaign test against a control group.',
        'CHRO': 'Link training to specific employee capabilities, monitor adoption and workload, and invite frontline feedback before scaling change.',
        'COO': 'Map the process bottleneck, test a limited rollout, and monitor fulfilment accuracy and service quality before expanding.',
        'Risk Officer': 'Challenge the demand assumptions, set a downside trigger, protect customer data and identify a contingency response.'
    }
    return ("**Qualitative coaching — role-specific rule-based fallback**\n\n"
            + guidance[role] + "\n\n"
            + f"**Challenge for the CEO:** {prompts[role]}")
