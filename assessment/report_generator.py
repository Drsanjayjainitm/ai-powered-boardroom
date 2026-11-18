def make_report(decision, result, assessment):
    lines = [
        "AI-POWERED BOARDROOM | CEO PERFORMANCE REPORT",
        "PromptEd 2026 teaching artefact prototype",
        "",
        "DECISIONS",
        f"Marketing investment: ₹{decision['marketing_lakh']} lakh",
        f"Technology investment: ₹{decision['technology_lakh']} lakh",
        f"Employee training: ₹{decision['training_lakh']} lakh",
        f"Pricing: {decision['pricing']}",
        f"Operations: {decision['operations']}",
        f"CEO rationale: {decision['rationale'] or 'Not provided'}",
        "",
        "MODELLED OUTCOMES (ILLUSTRATIVE)",
        f"Revenue: ₹{result['revenue_crore']:.2f} crore",
        f"Operating profit: ₹{result['profit_lakh']:.1f} lakh",
        f"Customer satisfaction: {result['customer_satisfaction']:.0f}/100",
        f"Market share: {result['market_share']:.1f}%",
        f"Modelled risk: {result['risk_level']}",
        "",
        f"FORMATIVE DECISION SCORE: {assessment['total']}/100",
        "Rubric dimensions:"
    ]
    lines += [f"- {k}: {v}/20" for k, v in assessment["dimensions"].items()]
    lines += ["", "FEEDBACK"] + [f"- {x}" for x in assessment["feedback"]]
    lines += ["", "LIMITATION: This report is based on a simplified fictional teaching model. It is not a forecast or professional advice."]
    return "\n".join(lines)
