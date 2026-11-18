from scenarios.retail import RETAIL_SCENARIO

def baseline_metrics():
    return RETAIL_SCENARIO["baseline"].copy()

def evaluate_retail_decision(decision):
    """Transparent illustrative model. Coefficients are teaching assumptions, not empirical forecasts."""
    m = float(decision["marketing_lakh"])
    t = float(decision["technology_lakh"])
    h = float(decision["training_lakh"])
    pricing = decision["pricing"]
    operations = decision["operations"]

    # Marketing supports demand; returns diminish as spend increases.
    marketing_lift = 0.55 * m - 0.012 * (m ** 2)
    tech_lift = 0.42 * t - 0.008 * (t ** 2)
    training_lift = 0.30 * h
    price_effect = {"Maintain current prices": 0.0,
                    "Reduce prices by 5%": 5.0,
                    "Increase prices by 5%": -4.0}[pricing]
    ops_effect = {"Maintain current operations": 0.0,
                  "Improve process efficiency": 5.0,
                  "Expand store capacity": 3.0}[operations]

    revenue_change_lakh = marketing_lift + tech_lift + training_lift + price_effect + ops_effect
    revenue_lakh = 250.0 + revenue_change_lakh
    investment_lakh = m + t + h

    # Expense savings are modelled separately and bounded for stability.
    efficiency_saving = 0.0
    if operations == "Improve process efficiency":
        efficiency_saving += 4.0 + 0.10 * t
    elif operations == "Expand store capacity":
        efficiency_saving -= 2.0
    efficiency_saving += 0.08 * h

    operating_cost = 210.0 - efficiency_saving
    operating_profit = revenue_lakh - operating_cost - investment_lakh
    revenue_crore = revenue_lakh / 100.0
    revenue_change_pct = (revenue_lakh - 250.0) / 250.0 * 100.0

    satisfaction = 70.0 + 0.55*m + 0.45*t + 0.65*h
    if pricing == "Reduce prices by 5%":
        satisfaction += 3
    elif pricing == "Increase prices by 5%":
        satisfaction -= 4
    if operations == "Improve process efficiency":
        satisfaction += 2
    satisfaction = max(0, min(100, satisfaction))

    market_share = 20.0 + 0.035*m + 0.025*t + 0.012*h
    if pricing == "Reduce prices by 5%":
        market_share += 1.2
    elif pricing == "Increase prices by 5%":
        market_share -= 0.8
    market_share = max(0, min(100, market_share))

    risk_points = 0
    if investment_lakh > 40:
        risk_points += 2
    if m > 18:
        risk_points += 1
    if t > 18:
        risk_points += 1
    if pricing == "Increase prices by 5%":
        risk_points += 1
    if operations == "Expand store capacity":
        risk_points += 1
    risk_level = "High" if risk_points >= 4 else ("Moderate" if risk_points >= 2 else "Low")

    explanations = [
        f"Total investment is ₹{investment_lakh:.1f} lakh against the ₹50 lakh ceiling.",
        f"Marketing, technology and training contribute a modelled revenue change of ₹{revenue_change_lakh:.1f} lakh before baseline revenue.",
        f"Operational cost savings are modelled at ₹{efficiency_saving:.1f} lakh.",
        "The model assumes diminishing returns from marketing and technology spending; actual outcomes would depend on execution and market conditions."
    ]
    return {
        "revenue_crore": revenue_crore,
        "revenue_change_pct": revenue_change_pct,
        "profit_lakh": operating_profit,
        "profit_change_lakh": operating_profit - 40.0,
        "customer_satisfaction": satisfaction,
        "customer_change": satisfaction - 70.0,
        "market_share": market_share,
        "market_share_change": market_share - 20.0,
        "investment_lakh": investment_lakh,
        "operating_cost_lakh": operating_cost,
        "risk_level": risk_level,
        "explanations": explanations
    }
