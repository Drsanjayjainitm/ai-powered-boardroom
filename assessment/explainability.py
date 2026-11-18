"""Human-readable explanations of the existing transparent rubric."""

def explain_rubric(decision, result, assessment):
    spend = result['investment_lakh']
    explanations = {
        'Strategic thinking': [
            '12 base points',
            '+4 for modelled revenue growth above 3%' if result['revenue_change_pct'] > 3 else '+0: revenue growth is not above 3%',
            '+2 for changing operations' if decision['operations'] != 'Maintain current operations' else '+0: operations maintained',
        ],
        'Financial reasoning': [
            '15 base points for spending up to ₹40 lakh; otherwise 11',
            '+3 if projected year-one profit exceeds ₹40 lakh' if result['profit_lakh'] > 40 else '+0: projected profit does not exceed ₹40 lakh',
            '+2 for staying within the ₹50 lakh ceiling',
        ],
        'Marketing decisions': [
            '12 base points',
            '+5 for marketing allocation ₹5–18 lakh' if 5 <= decision['marketing_lakh'] <= 18 else '+0: marketing allocation outside ₹5–18 lakh',
            '+3 for satisfaction at least 75' if result['customer_satisfaction'] >= 75 else '+0: satisfaction below 75',
        ],
        'Risk management': [
            '15 base points',
            '+3 for Low modelled risk' if result['risk_level'] == 'Low' else ('−5 for High modelled risk' if result['risk_level'] == 'High' else '+0 for Moderate modelled risk'),
        ],
        'Responsible leadership': [
            '12 base points',
            '+5 for employee training ≥ ₹5 lakh' if decision['training_lakh'] >= 5 else '+0: training below ₹5 lakh',
            '+3 for written CEO rationale' if decision['rationale'].strip() else '+0: missing rationale',
        ],
    }
    return {name: {'score': assessment['dimensions'][name], 'reasons': reasons,
                   'note': 'Score capped at 20.'} for name, reasons in explanations.items()}
