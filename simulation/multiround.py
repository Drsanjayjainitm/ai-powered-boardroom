"""Three-stage strategy revision exercise (not a time-series forecast).

Each round commits additional investment; cumulative category caps and the ₹50 lakh
ceiling apply across the whole exercise. The teaching engine re-evaluates the
cumulative strategy using the latest pricing/operations choice. Each row is a
revision of the SAME year-one forecast, not a new financial year.
"""
from simulation.decision_engine import evaluate_retail_decision
from assessment.evaluation import assess_decision

CAPS = {'marketing_lakh': 25, 'technology_lakh': 25, 'training_lakh': 15}
BUDGET = 50
MAX_ROUNDS = 3


def validate_round(history, increments):
    if len(history) >= MAX_ROUNDS:
        raise ValueError('The three decision rounds are complete.')
    for key, cap in CAPS.items():
        value = increments[key]
        if not isinstance(value, (int, float)) or value < 0 or value > cap:
            raise ValueError(f'Invalid incremental amount for {key}.')
    cumulative = {key: sum(row['increment'][key] for row in history) + increments[key]
                  for key in CAPS}
    for key, cap in CAPS.items():
        if cumulative[key] > cap:
            raise ValueError(f'Cumulative {key} allocation exceeds ₹{cap} lakh.')
    if sum(cumulative.values()) > BUDGET:
        raise ValueError('Cumulative investment exceeds ₹50 lakh.')
    return cumulative


def run_round(history, increments, pricing, operations, rationale, reflection):
    cumulative = validate_round(history, increments)
    if len(reflection.strip().split()) < 12:
        raise ValueError('Reflection is required: write at least 12 words explaining your learning, assumptions, or next step.')
    if not rationale.strip():
        raise ValueError('Provide a CEO rationale before submitting the round.')
    decision = {**cumulative, 'pricing': pricing, 'operations': operations,
                'rationale': rationale.strip()}
    result = evaluate_retail_decision(decision)
    if not isinstance(result, dict):
        raise RuntimeError('Decision engine did not return a valid result.')
    assessment = assess_decision(decision, result)
    record = {'round': len(history) + 1,
              'increment': {key: increments[key] for key in CAPS},
              'decision': decision, 'result': result, 'assessment': assessment,
              'reflection': reflection.strip()}
    return record


def learning_rows(history):
    rows = []
    for record in history:
        d, r, a = record['decision'], record['result'], record['assessment']
        row = {'Round': record['round'], 'Total investment (₹ lakh)': r['investment_lakh'],
               'Revenue (₹ lakh)': round(r['revenue_crore'] * 100, 2),
               'Year-one profit after investment (₹ lakh)': round(r['profit_lakh'], 2),
               'Satisfaction': round(r['customer_satisfaction'], 1),
               'Market share (%)': round(r['market_share'], 2),
               'Risk': r['risk_level'], 'Rubric score (/100)': a['total'],
               'Pricing': d['pricing'], 'Operations': d['operations'],
               'Marketing committed (₹ lakh)': d['marketing_lakh'],
               'Technology committed (₹ lakh)': d['technology_lakh'],
               'Training committed (₹ lakh)': d['training_lakh'],
               'CEO rationale': d['rationale'], 'Reflection': record['reflection']}
        row.update({f'Rubric: {k}': v for k, v in a['dimensions'].items()})
        rows.append(row)
    return rows


def downside_sensitivity(record, revenue_shortfall_pct=10):
    """Simple sensitivity: lower revenue with operating costs and spend unchanged."""
    r = record['result']
    lower_revenue_lakh = r['revenue_crore'] * 100 * (1 - revenue_shortfall_pct / 100)
    return {'revenue_lakh': round(lower_revenue_lakh, 2),
            'profit_lakh': round(lower_revenue_lakh - r['operating_cost_lakh'] - r['investment_lakh'], 2)}
