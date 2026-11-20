"""Numerically grounded mentor: deterministic facts + qualitative LLM commentary."""
import re
from agents.grounding import sanitize_ai_prose
from agents.advisors import _call_openai, _call_gemini, _call_ollama, _safe_provider_error

BUDGET_LAKH = 50.0
BASE_REVENUE_LAKH = 250.0
BASE_PROFIT_LAKH = 40.0

MENTOR_SYSTEM_PROMPT = """You are a constructive management educator reviewing a fictional CEO simulation.
You are responsible ONLY for qualitative teaching feedback. A separate Python component
provides all financial figures and comparisons. NEVER output numbers, percentages,
currency amounts, equations, financial calculations, or headings about financial evidence.
Never claim the budget is exceeded or that unspent budget must be invested.
The rounds are cumulative revisions of ONE year-one estimate, not separate years.
The rubric is formative, not a validated competence measure.
Use only supplied decision choices, student reflections and verified trend statements.
Avoid invented business facts, unsupported causal certainty and generic praise.
Use EXACTLY these three headings, each on its own line:
### Strategic Strengths
### Financial and Risk Trade-offs
### Reflection and Learning
Provide two or three complete sentences under each heading, grounded in the supplied student rationale and reflections.
Do NOT generate action lists or CEO questions; Python provides those separately.
Keep it between 80 and 160 words. Never repeat the numeric case evidence.
Pricing and operations choices must be described exactly as supplied. Never claim a change
unless VERIFIED DECISION CHANGES explicitly confirms it. Never introduce hypothetical
risks as if they occurred. Python supplies two actions and a CEO question after your commentary. Do not add them.
Avoid numbers in the generated response. Output prose only, never code, JSON, dictionaries, or programming examples. The one-time investment is deducted from year-one profit; do not attribute the profit decline to unverified cost increases.
"""


def verified_facts(history):
    """Compute canonical numerical evidence independently of any LLM."""
    if not history:
        raise ValueError('No completed rounds')
    first, last = history[0], history[-1]
    a, b = first['result'], last['result']
    investment = float(b['investment_lakh'])
    first_rev = float(a['revenue_crore']) * 100
    final_rev = float(b['revenue_crore']) * 100
    first_profit = float(a['profit_lakh'])
    final_profit = float(b['profit_lakh'])
    return {
        'rounds': len(history),
        'first_revenue_lakh': round(first_rev, 2),
        'final_revenue_lakh': round(final_rev, 2),
        'revenue_vs_baseline_lakh': round(final_rev - BASE_REVENUE_LAKH, 2),
        'revenue_vs_baseline_pct': round((final_rev / BASE_REVENUE_LAKH - 1) * 100, 2),
        'revenue_first_to_final_lakh': round(final_rev - first_rev, 2),
        'first_profit_lakh': round(first_profit, 2),
        'final_profit_lakh': round(final_profit, 2),
        'profit_vs_baseline_lakh': round(final_profit - BASE_PROFIT_LAKH, 2),
        'profit_first_to_final_lakh': round(final_profit - first_profit, 2),
        'investment_lakh': round(investment, 2),
        'remaining_budget_lakh': round(BUDGET_LAKH - investment, 2),
        'first_satisfaction': round(float(a['customer_satisfaction']), 2),
        'final_satisfaction': round(float(b['customer_satisfaction']), 2),
        'first_risk': str(a['risk_level']),
        'final_risk': str(b['risk_level']),
        'first_score': int(first['assessment']['total']),
        'final_score': int(last['assessment']['total']),
    }


def _signed(value):
    return ('+' if value > 0 else '') + f'{value:.2f}'


def facts_markdown(f):
    """This section is NEVER written or edited by an LLM."""
    return ("### Verified Performance Evidence (Python-calculated)\n"
            f"- Completed rounds: **{f['rounds']}** (cumulative revisions of one year-one strategy).\n"
            f"- Revenue: Round 1 **₹{f['first_revenue_lakh']:.2f} lakh** → final **₹{f['final_revenue_lakh']:.2f} lakh**. "
            f"Versus ₹250 lakh baseline: **{_signed(f['revenue_vs_baseline_lakh'])} lakh** "
            f"(**{_signed(f['revenue_vs_baseline_pct'])}%**).\n"
            f"- Year-one profit after investment: Round 1 **₹{f['first_profit_lakh']:.2f} lakh** → final "
            f"**₹{f['final_profit_lakh']:.2f} lakh**. Versus ₹40 lakh baseline: "
            f"**{_signed(f['profit_vs_baseline_lakh'])} lakh**.\n"
            f"- Cumulative investment **₹{f['investment_lakh']:.2f} lakh** / ₹50 lakh; "
            f"unspent allocation **₹{f['remaining_budget_lakh']:.2f} lakh**.\n"
            f"- Satisfaction: **{f['first_satisfaction']:.1f} → {f['final_satisfaction']:.1f}**; "
            f"risk: **{f['first_risk']} → {f['final_risk']}**; "
            f"formative score: **{f['first_score']} → {f['final_score']}**.\n"
            "- These are illustrative teaching-model results, not real-world financial forecasts.\n")


def decision_change_lines(history):
    """Deterministic descriptions of actual decision choices across revisions."""
    if not history:
        return []
    first = history[0]['decision']
    last = history[-1]['decision']
    lines = []
    for field, label in [('pricing', 'Pricing'), ('operations', 'Operations')]:
        choices = [str(item['decision'][field]) for item in history]
        if len(set(choices)) == 1:
            lines.append(f'{label} remained unchanged in all rounds: {choices[0]}.')
        else:
            detail = '; '.join(f'Round {i+1}: {v}' for i, v in enumerate(choices))
            lines.append(f'{label} changed across revisions: {detail}.')
    for field, label in [('marketing_lakh', 'Marketing'), ('technology_lakh', 'Technology'), ('training_lakh', 'Training')]:
        if last[field] != first[field]:
            lines.append(f'{label} cumulative investment increased across revisions.')
        else:
            lines.append(f'{label} cumulative investment remained unchanged.')
    return lines


def _deterministic_strategy_commentary(history, f):
    """A verified commentary scaffold; never outsourced to the model."""
    ops = [r['decision']['operations'] for r in history]
    if len(set(ops)) > 1:
        ops_line = 'Operations changed across revisions: ' + ' → '.join(ops) + '.'
    else:
        ops_line = 'Operations remained unchanged: ' + ops[0] + '.'
    pricing = [r['decision']['pricing'] for r in history]
    price_line = ('Pricing remained unchanged: ' + pricing[0] + '.' if len(set(pricing)) == 1
                  else 'Pricing changed across revisions: ' + ' → '.join(pricing) + '.')
    return '**Verified decision history (Python-calculated)**\n' + price_line + '\n' + ops_line + '\n'


def _validated_ai_sections(answer):
    """Parse three narrative sections, allowing common Gemini heading variants.

    Never admit AI-authored figures or code; Python supplies verified evidence and actions.
    """
    cleaned = sanitize_ai_prose(answer)
    if not cleaned:
        return None
    titles = ('Strategic Strengths', 'Financial and Risk Trade-offs', 'Reflection and Learning')
    aliases = {
        'strategic strengths': titles[0], 'strengths': titles[0],
        'financial and risk trade-offs': titles[1], 'financial & risk trade-offs': titles[1],
        'financial and risk tradeoffs': titles[1], 'financial and risk trade offs': titles[1],
        'financial trade-offs': titles[1], 'financial and risk considerations': titles[1],
        'reflection and learning': titles[2], 'reflection & learning': titles[2],
        'learning and reflection': titles[2], 'reflection': titles[2], 'learning reflections': titles[2],
        'strategic strengths and opportunities': titles[0],
        'financial and risk tradeoffs': titles[1],
        'financial and risk trade-offs and considerations': titles[1],
    }
    sections = {t: [] for t in titles}
    current = None
    for line in cleaned.splitlines():
        stripped = line.strip()
        heading = re.sub(r'^#{1,6}\s*', '', stripped)
        heading = re.sub(r'^\d+[.)]\s*', '', heading)
        heading = re.sub(r'^\*\*(.*?)\*\*:?$', r'\1', heading).strip().rstrip(':').strip()
        heading = re.sub(r'^[-*]\s+', '', heading).strip()
        if heading.lower() in aliases:
            current = aliases[heading.lower()]
            continue
        if stripped.startswith('#'):
            current = None
            continue
        if not current or not stripped:
            continue
        if re.search(r'[0-9₹%$]', stripped):
            continue
        if re.search(r'\b(?:budget (?:exceeded|violation)|insufficient budget)\b', stripped, re.I):
            continue
        # Do not allow invented claims that decisions changed; actual choices are
        # printed separately from verified history.
        if re.search(r'\b(?:you|the CEO) (?:changed|switched|raised|lowered) (?:pricing|prices|operations)\b', stripped, re.I):
            continue
        sections[current].append(stripped)
    if any(not sections[t] for t in titles):
        # Some providers omit headings despite explicit instructions. Only accept
        # three substantial, clean paragraphs in the expected order; never infer
        # facts or allow a numeric claim through this recovery path.
        if not any(sections[t] for t in titles):
            paragraphs = [x.strip() for x in re.split(r'\n\s*\n', cleaned)
                          if len(x.strip().split()) >= 15]
            if len(paragraphs) == 3 and all(not re.search(r'[0-9₹%$]|[{}]|\bprint\(', x) for x in paragraphs):
                sections = {title: [paragraphs[i]] for i, title in enumerate(titles)}
            else:
                return None
        else:
            return None
    prose = '\n\n'.join('### ' + title + '\n' + ' '.join(sections[title]) for title in titles)
    return prose if len(prose.split()) >= 25 else None


def _verified_actions(history):
    """Decision-sensitive recommendations; never assume a decision changed."""
    ops = [str(item['decision']['operations']) for item in history]
    pricing = [str(item['decision']['pricing']) for item in history]
    if len(set(ops)) > 1:
        action = "Compare the latest operations choice with the previous choice using the same investment allocation."
        question = "Which verified operating outcome supports the change in operations?"
    elif len(set(pricing)) > 1:
        action = "Compare the revised pricing choice with the previous pricing choice while holding other decisions constant."
        question = "What evidence supports the pricing change?"
    else:
        action = "Test an alternative operating strategy while holding the investment allocation and pricing constant."
        question = "What evidence would justify changing the current operating strategy?"
    return ("### Two Feasible Next Actions and One CEO Question\n"
            f"- {action}\n"
            "- Define measurable payback and customer-experience targets before allocating any remaining budget.\n\n"
            f"**CEO question:** {question}")


def _qualitative_input(history, f):
    def trend(x):
        return 'increased' if x > 0.005 else 'decreased' if x < -0.005 else 'remained approximately unchanged'
    parts = [
        'VERIFIED TRENDS (use words only; no numbers in your response):',
        f"Revenue versus baseline {trend(f['revenue_vs_baseline_lakh'])}.",
        f"Profit versus baseline {trend(f['profit_vs_baseline_lakh'])}.",
        f"Profit from first to final revision {trend(f['profit_first_to_final_lakh'])}.",
        f"Satisfaction from first to final revision {trend(f['final_satisfaction']-f['first_satisfaction'])}.",
        f"Final risk category: {f['final_risk']}.",
        'Budget cap is respected.' if f['remaining_budget_lakh'] >= 0 else 'Budget cap exceeded.',
        'VERIFIED DECISION CHANGES:',
        *decision_change_lines(history),
        'STUDENT EVIDENCE:',
    ]
    for item in history:
        d = item['decision']
        parts.append(f"Round {item['round']}: pricing={d['pricing']}; operations={d['operations']}; "
                     f"CEO rationale={d.get('rationale','')}; reflection={item.get('reflection','')}")
    parts.append('Respond ONLY with the requested qualitative headings and content. Do not reproduce any numbers.')
    return '\n'.join(parts)


def _remove_unsafe_numeric_claims(text):
    """Defense in depth: suppress LLM-authored lines with digits/currency symbols.

    All numerical evidence comes from facts_markdown, so removing these lines
    cannot alter the verified figures. This is intentionally conservative.
    """
    cleaned = []
    for line in text.splitlines():
        if re.search(r'[0-9₹%$]', line):
            continue
        if re.search(r'\b(?:budget (?:exceeded|violation)|insufficient budget)\b', line, re.I):
            continue
        cleaned.append(line)
    return '\n'.join(cleaned).strip()


def _fallback_commentary(history, f):
    return ("### Strategic Strengths\n"
            "The CEO explains the role of marketing, technology and employee capability in customer experience. "
            "The strategy also preserves an unspent contingency allocation.\n\n"
            "### Financial and Risk Trade-offs\n"
            "The verified evidence shows revenue above baseline while profit remains below baseline. "
            "Review the latest operations choice and downside sensitivity before committing further funds.\n\n"
            "### Reflection and Learning\n"
            "The reflections acknowledge that revenue growth does not guarantee immediate profit growth "
            "and identify phased investment as a possible response.\n\n"
            + _verified_actions(history))


def mentor_feedback(history, provider='Demo mode (no API key)', api_key='', model=''):
    if not history:
        return 'Complete at least one decision round first.'
    f = verified_facts(history)
    facts = facts_markdown(f) + '\n' + _deterministic_strategy_commentary(history, f)
    if provider == 'Demo mode (no API key)':
        return facts + '\n**Qualitative mentor feedback — rule-based Demo mode**\n\n' + _fallback_commentary(history, f)
    if provider in ('OpenAI', 'Google Gemini') and not api_key:
        return 'Enter a valid provider API key to use the generative CEO Mentor.'
    try:
        prompt = _qualitative_input(history, f)
        if provider == 'Ollama (local, free)':
            answer = _call_ollama(MENTOR_SYSTEM_PROMPT, prompt, model)
        elif provider == 'OpenAI':
            answer = _call_openai(MENTOR_SYSTEM_PROMPT, prompt, api_key, model)
        elif provider == 'Google Gemini':
            answer = _call_gemini(MENTOR_SYSTEM_PROMPT, prompt, api_key, model)
        else:
            return 'Unsupported provider.'
        safe = _validated_ai_sections(answer)
        if not safe or len(safe.split()) < 25:
            safe = _fallback_commentary(history, f)
            label = '**Qualitative mentor feedback — rule-based fallback (AI response did not pass validation)**'
        else:
            safe += '\n\n' + _verified_actions(history)
            label = '**Qualitative mentor feedback — AI-generated narrative, verified actions and numerical evidence**'
        return facts + '\n' + label + '\n\n' + safe
    except Exception as exc:
        return (facts + '\n**AI mentor unavailable** (' + _safe_provider_error(exc) + '). '
                'Check the selected provider and model; the verified numerical evidence above remains valid.')
