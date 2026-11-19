from utils.cloud_ai import gemini_sidebar
import streamlit as st
import pandas as pd
import plotly.express as px

from utils.ui import apply_theme, hero
from scenarios.retail import RETAIL_SCENARIO
from simulation.decision_engine import evaluate_retail_decision
from simulation.strategy_comparison import compare_strategies
from agents.advisors import get_advisor_recommendations
from agents.dialogue import ask_advisor
from assessment.evaluation import assess_decision
from assessment.report_generator import make_report

st.set_page_config(page_title="AI-Powered Boardroom | CEO Strategy Studio", page_icon="🏢", layout="wide")
apply_theme()


defaults = {
    "last_result": None, "last_decision": None, "last_assessment": None,
    "saved_strategies": {}, "dialogues": {}
}
for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value.copy() if isinstance(value, dict) else value

ADVISORS = ["CFO", "CMO", "CHRO", "COO", "Risk Officer"]

with st.sidebar:
    st.header("Simulation setup")
    st.success("Scenario 1 · Retail Business Recovery")
    st.write("**Company:** " + RETAIL_SCENARIO["company"])
    st.write("**Industry:** " + RETAIL_SCENARIO["industry"])
    st.write("**Investment ceiling:** ₹50 lakh")
    st.divider()
    provider = st.selectbox("AI provider", ["Demo mode (no API key)", "Ollama (local, free)", "OpenAI", "Google Gemini"])
    api_key, model = "", ""
    if provider == "Ollama (local, free)":
        model = st.text_input("Local Ollama model", value="llama3.2:1b")
        st.caption("No API key needed. Ollama must be running on this computer at localhost:11434.")
    elif provider == "OpenAI":
        api_key = st.text_input("OpenAI API key", type="password")
        model = st.text_input("Model", value="gpt-4o-mini")
    elif provider == "Google Gemini":
        api_key, model = gemini_sidebar()
    st.caption("Demo is rule-based, not generative AI. Gemini is configured through Streamlit Secrets; local Ollama requires a local server.")
    if st.button("Reset current simulation"):
        st.session_state["last_result"] = None
        st.session_state["last_decision"] = None
        st.session_state["last_assessment"] = None
        st.rerun()

hero('PROMPTED 2026 · PROFESSIONAL TRACK · COMPETITION QUALITY PATCH 3.4.1',
     'AI-Powered Boardroom',
     'Lead the recovery of Aarohan Retail. Make strategic decisions, challenge five AI advisors, and defend the trade-offs.')
st.markdown('<span class="pill">CEO Strategy Studio · Single-decision sandbox</span>', unsafe_allow_html=True)
st.caption('For a full three-round learning journey, open **CEO Decision Lab** in the sidebar.')

st.markdown("### 1 · Understand the business challenge")
a,b,c = st.columns(3)
a.metric("Annual revenue", "₹2.50 crore", "-15% trend")
b.metric("Annual operating costs", "₹2.10 crore")
c.metric("Recovery investment ceiling", "₹50 lakh")
with st.expander("Company background and challenge", expanded=False):
    st.write(RETAIL_SCENARIO["description"])
    for item in RETAIL_SCENARIO["challenges"]:
        st.write("• " + item)
    st.info("This is fictional teaching data. Results are illustrative, not forecasts.")

st.markdown("### 2 · Make your CEO decisions")
left, right = st.columns(2)
with left:
    marketing = st.slider("Marketing investment (₹ lakh)", 0, 25, 12, 1)
    technology = st.slider("Technology investment (₹ lakh)", 0, 25, 15, 1)
    training = st.slider("Employee training (₹ lakh)", 0, 15, 5, 1)
with right:
    pricing = st.selectbox("Pricing strategy", ["Maintain current prices", "Reduce prices by 5%", "Increase prices by 5%"])
    operations = st.selectbox("Operational strategy", ["Maintain current operations", "Improve process efficiency", "Expand store capacity"])
    rationale = st.text_area("CEO rationale", height=110, placeholder="Explain the trade-offs and your intended outcomes...")

decision = {
    "marketing_lakh": marketing, "technology_lakh": technology,
    "training_lakh": training, "pricing": pricing,
    "operations": operations, "rationale": rationale
}
total = marketing + technology + training
x,y,z = st.columns(3)
x.metric("Allocated budget", f"₹{total} lakh")
y.metric("Remaining budget", f"₹{50-total} lakh")
z.metric("Budget status", "Within limit" if total <= 50 else "Over budget")
valid = total <= 50
if not valid:
    st.error("Reduce investments to stay within the ₹50 lakh ceiling.")
if st.button("🚀 Run business simulation", type="primary", use_container_width=True, disabled=not valid):
    result = evaluate_retail_decision(decision)
    if not isinstance(result, dict) or not {"revenue_crore","profit_lakh","customer_satisfaction","market_share"}.issubset(result):
        st.error("Simulation did not return a complete result. Check simulation/decision_engine.py.")
    else:
        st.session_state["last_result"] = result
        st.session_state["last_decision"] = decision.copy()
        st.session_state["last_assessment"] = assess_decision(decision, result)
        st.session_state["dialogues"] = {}  # questions belong to the current decision

result = st.session_state.get("last_result")
if not isinstance(result, dict):
    st.info("Run a valid business simulation to unlock the dashboard, advisor dialogue and strategy comparison.")
    st.stop()

current_decision = st.session_state["last_decision"]
st.markdown("### 3 · Business performance dashboard")
st.caption("These values correspond to the last simulated decision, not necessarily the sliders currently displayed.")
m1,m2,m3,m4 = st.columns(4)
m1.metric("Projected revenue", f"₹{result['revenue_crore']:.2f} Cr", f"{result['revenue_change_pct']:+.1f}%")
m2.metric("Year-one profit after investment", f"₹{result['profit_lakh']:.1f} L", f"{result['profit_change_lakh']:+.1f} L")
m3.metric("Customer satisfaction", f"{result['customer_satisfaction']:.0f}/100", f"{result['customer_change']:+.0f} pts")
m4.metric("Market share", f"{result['market_share']:.1f}%", f"{result['market_share_change']:+.1f} pts")
plot = pd.DataFrame({
    "Measure":["Revenue","Year-one profit","Satisfaction","Market share"],
    "Baseline":[250,40,70,20],
    "Projected":[result["revenue_crore"]*100,result["profit_lakh"],result["customer_satisfaction"],result["market_share"]],
    "Units":["₹ lakh","₹ lakh","points","%"]
})
financial = plot.iloc[:2].copy()
nonfinancial = plot.iloc[2:].copy()
fc1, fc2 = st.columns(2)
with fc1:
    st.plotly_chart(px.bar(financial, x="Measure", y=["Baseline","Projected"],
                           barmode="group", title="Financial outcomes (₹ lakh)"), use_container_width=True)
with fc2:
    st.plotly_chart(px.bar(nonfinancial, x="Measure", y=["Baseline","Projected"],
                           barmode="group", title="Satisfaction (points) and market share (%)"),
                    use_container_width=True)
for note in result["explanations"]:
    st.write("• " + note)
st.info(f"Modelled risk: {result['risk_level']}. Profit includes the one-time investment; revenue growth does not imply immediate profit growth.")

st.markdown("### 4 · Interactive AI Boardroom")
st.caption("Choose an advisor, review their position, and ask follow-up questions. Each role has its own dialogue history.")
role = st.selectbox("Advisor to consult", ADVISORS, key="advisor_role")
with st.expander(f"Initial {role} recommendation", expanded=True):
    st.write(get_advisor_recommendations(role, current_decision, result, provider, api_key, model))
dialogues = st.session_state["dialogues"]
history = dialogues.setdefault(role, [])
for turn in history:
    with st.chat_message("user" if turn["speaker"] == "CEO" else "assistant"):
        st.markdown(turn["text"])
with st.form("advisor_question_form", clear_on_submit=True):
    question = st.text_input(f"Ask {role} a question", placeholder="What is the biggest trade-off in my strategy?", max_chars=1200)
    submitted = st.form_submit_button("Ask advisor")
if submitted:
    if not question.strip():
        st.warning("Please enter a question.")
    else:
        answer = ask_advisor(role, question, current_decision, result, provider, api_key, model, history)
        history.extend([{"speaker":"CEO","text":question.strip()}, {"speaker":role,"text":answer}])
        st.rerun()
if st.button(f"Clear {role} dialogue"):
    dialogues[role] = []
    st.rerun()

st.markdown("### 5 · Compare business strategies")
st.write("Save the last simulated decision as a named strategy. Change the sliders, run again, and save an alternative.")
strategy_name = st.text_input("Strategy name", value=f"Strategy {len(st.session_state['saved_strategies'])+1}", max_chars=60)
if st.button("Save last simulated strategy"):
    if not strategy_name.strip():
        st.warning("Enter a strategy name.")
    elif strategy_name.strip() in st.session_state["saved_strategies"]:
        st.warning("That name already exists. Choose another name.")
    else:
        st.session_state["saved_strategies"][strategy_name.strip()] = current_decision.copy()
        st.success(f"Saved {strategy_name.strip()}.")
saved = st.session_state["saved_strategies"]
if saved:
    names = st.multiselect("Strategies to compare (up to 3)", list(saved), default=list(saved)[-3:], max_selections=3)
    if names:
        rows = compare_strategies([(name, saved[name]) for name in names])
        frame = pd.DataFrame(rows)
        st.dataframe(frame, use_container_width=True, hide_index=True)
        st.plotly_chart(px.bar(frame, x="Strategy", y="Year-one profit (₹ lakh)",
                               color="Strategy", title="Year-one profit comparison"), use_container_width=True)
        st.download_button("Download strategy comparison (CSV)", frame.to_csv(index=False).encode("utf-8-sig"),
                           file_name="strategy_comparison.csv", mime="text/csv")
        st.caption("First-year investment return proxy = (projected profit after investment − baseline profit) / investment × 100. "
                   "This is an illustrative single-period measure, NOT an audited ROI, cash-flow return, or payback estimate.")
    if st.button("Clear saved strategies"):
        st.session_state["saved_strategies"] = {}
        st.rerun()
else:
    st.caption("No saved strategies yet. Save this decision, then try a different budget mix.")

st.markdown("### 6 · CEO learning assessment")
assessment = st.session_state.get("last_assessment")
if isinstance(assessment, dict):
    st.metric("Formative decision score", f"{assessment['total']}/100")
    scores = pd.DataFrame({"Dimension":list(assessment["dimensions"]),
                           "Score":list(assessment["dimensions"].values())})
    st.plotly_chart(px.bar(scores, x="Dimension", y="Score", range_y=[0,20],
                           title="Decision rubric (0–20 per dimension)"), use_container_width=True)
    for feedback in assessment["feedback"]:
        st.write("• " + feedback)
    report = make_report(current_decision, result, assessment)
    st.download_button("Download CEO performance report (TXT)", report,
                       file_name="ceo_performance_report.txt", mime="text/plain")

st.divider()
st.caption("Educational prototype · Rule-based demo responses are not generative AI. "
           "The numerical model uses transparent fictional assumptions. "
           "Live AI output must be checked critically. Session data is not persisted after the session ends.")
