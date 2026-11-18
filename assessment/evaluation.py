def assess_decision(decision, result):
    dims = {
        "Strategic thinking": 0,
        "Financial reasoning": 0,
        "Marketing decisions": 0,
        "Risk management": 0,
        "Responsible leadership": 0
    }
    feedback = []
    spend = result["investment_lakh"]

    # Transparent formative rubric: each dimension is scored from 0 to 20.
    dims["Strategic thinking"] = 12
    if result["revenue_change_pct"] > 3:
        dims["Strategic thinking"] += 4
    if decision["operations"] != "Maintain current operations":
        dims["Strategic thinking"] += 2

    dims["Financial reasoning"] = 15 if spend <= 40 else 11
    if result["profit_lakh"] > 40:
        dims["Financial reasoning"] += 3
    if spend <= 50:
        dims["Financial reasoning"] += 2

    dims["Marketing decisions"] = 12
    if 5 <= decision["marketing_lakh"] <= 18:
        dims["Marketing decisions"] += 5
    if result["customer_satisfaction"] >= 75:
        dims["Marketing decisions"] += 3

    dims["Risk management"] = 15
    if result["risk_level"] == "High":
        dims["Risk management"] -= 5
    elif result["risk_level"] == "Low":
        dims["Risk management"] += 3

    dims["Responsible leadership"] = 12
    if decision["training_lakh"] >= 5:
        dims["Responsible leadership"] += 5
    if decision["rationale"].strip():
        dims["Responsible leadership"] += 3

    dims = {k: min(20, max(0, int(v))) for k, v in dims.items()}
    total = sum(dims.values())

    if decision["rationale"].strip():
        feedback.append("You articulated a CEO rationale; compare it with the modelled outcomes and advisor perspectives.")
    else:
        feedback.append("Add a written rationale so that your decision process can be evaluated, not just the numerical outcome.")
    if spend > 40:
        feedback.append("A large share of the authorised budget is committed. Consider a phased investment and retain a contingency reserve.")
    else:
        feedback.append("You retained some budget flexibility. Explain how the unallocated funds could be used if assumptions change.")
    if result["risk_level"] == "High":
        feedback.append("The selected combination has elevated modelled risk. Stress-test demand and implementation assumptions.")
    else:
        feedback.append("Review whether the risk level remains acceptable under a downside demand scenario.")
    if decision["training_lakh"] < 5:
        feedback.append("Consider whether employees have the skills and support needed to adopt the proposed changes.")
    feedback.append("The score is a formative rubric-based indicator, not an objective measure of managerial ability.")
    return {"total": total, "dimensions": dims, "feedback": feedback}
