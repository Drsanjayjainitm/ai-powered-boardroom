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


DISALLOWED = re.compile(
    r"\b(?:revenue|profit|budget|investment|reserve|cash|pricing|prices|operations|risk|satisfaction|" 
    r"loss|gain|increase|decrease|grew|fell|growth|decline|percent|percentages|roi|payback)\b",
    re.I,
)


def safe_qualitative(text):
    """Accept only nonnumeric, nonfinancial coaching prose; otherwise use a labelled fallback.

    Not a semantic truth verifier. Restrict LLM to generic teaching prompts, while
    deterministic code owns all decision/financial assertions.
    """
    if not isinstance(text, str) or len(text.strip()) < 35:
        return None
    if re.search(r'[0-9₹%$]', text):
        return None
    if DISALLOWED.search(text):
        return None
    if len(text.split()) > 160:
        return None
    return text.strip()


def fallback_coaching(role, question=''):
    prompts = {
        'CFO': 'What evidence would you use to judge whether this strategy offers acceptable value for the company?',
        'CMO': 'Which customer segment and measurable experiment would you prioritize?',
        'CHRO': 'How would you check employee readiness and adoption?',
        'COO': 'Which service-quality indicator would you monitor during implementation?',
        'Risk Officer': 'Which assumption would you challenge before approving the strategy?',
    }
    return ("**Qualitative coaching — rule-based fallback**\n\n"
            "Consider the evidence, alternative explanations, and what you would test next. "
            "Separate model assumptions from observed business evidence.\n\n"
            f"**Challenge for the CEO:** {prompts[role]}")
