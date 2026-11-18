"""Compare independent strategy decisions using the same deterministic teaching model."""
from simulation.decision_engine import evaluate_retail_decision

def compare_strategies(named_decisions):
    records = []
    for name, decision in named_decisions:
        allocated = sum(float(decision[k]) for k in ("marketing_lakh", "technology_lakh", "training_lakh"))
        if allocated > 50 or min(float(decision[k]) for k in ("marketing_lakh", "technology_lakh", "training_lakh")) < 0:
            raise ValueError(f"{name}: investment must be between ₹0 and ₹50 lakh")
        result = evaluate_retail_decision(decision)
        if not isinstance(result, dict):
            raise ValueError(f"{name}: simulation did not return valid results")
        # Profit is already after the one-time investment. This proxy is NOT cash-flow ROI.
        incremental_preinvestment_profit = result["profit_lakh"] + allocated - 40.0
        roi_proxy = (incremental_preinvestment_profit - allocated) / allocated * 100 if allocated else None
        records.append({
            "Strategy": name,
            "Investment (₹ lakh)": round(allocated, 2),
            "Revenue (₹ lakh)": round(result["revenue_crore"] * 100, 2),
            "Year-one profit (₹ lakh)": round(result["profit_lakh"], 2),
            "Satisfaction (/100)": round(result["customer_satisfaction"], 1),
            "Market share (%)": round(result["market_share"], 2),
            "Risk": result["risk_level"],
            "First-year investment return proxy (%)": round(roi_proxy, 1) if roi_proxy is not None else None,
        })
    return records
