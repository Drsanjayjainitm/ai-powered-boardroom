"""PromptEd Milestone 3: a 3-round cumulative investment teaching exercise."""
from utils.cloud_ai import gemini_sidebar
from utils.board_dashboard import render_board
import json
import pandas as pd
import plotly.express as px
import streamlit as st
from decimal import Decimal, ROUND_HALF_UP

from utils.ui import apply_theme, hero
from utils.charts import polish_chart
from simulation.multiround import (CAPS, BUDGET, MAX_ROUNDS, run_round,
                                   learning_rows, downside_sensitivity)
from agents.dialogue import ask_advisor
from agents.ceo_mentor import mentor_feedback
from assessment.explainability import explain_rubric
from agents.advisors import get_advisor_recommendations

st.set_page_config(page_title='CEO Decision Lab | AI-Powered Boardroom', page_icon='📈', layout='wide')
apply_theme()
hero('AI-POWERED BOARDROOM · INTERACTIVE MANAGEMENT SIMULATOR',
     'CEO Decision Lab',
     'Three decisions. One recovery strategy. Use evidence, debate trade-offs, and reflect like a CEO.')
st.markdown('<span class="pill">3-round learning journey · Aarohan Retail Pvt. Ltd.</span>', unsafe_allow_html=True)
st.info('Each round revises the **same year-one scenario**, not a different financial year. '
        'The ₹50 lakh ceiling and category caps apply cumulatively. Figures are illustrative teaching assumptions.')

if 'm3_history' not in st.session_state:
    st.session_state.m3_history = []
if 'm3_dialogues' not in st.session_state:
    st.session_state.m3_dialogues = {}

history = st.session_state.m3_history
n = len(history)
with st.sidebar:
    st.page_link('app.py', label='AI-Powered Boardroom', icon='🏢')
    st.page_link('pages/2_CEO_Decision_Lab.py', label='CEO Decision Lab', icon='📈')
    st.divider()
    st.header('CEO Lab controls')
    provider = st.selectbox('Advisor mode', ['Demo mode (no API key)', 'Ollama (local, free)', 'OpenAI', 'Google Gemini'], key='m3_provider')
    api_key = ''
    model = ''
    if provider == 'Ollama (local, free)':
        model = st.text_input('Local Ollama model', value='llama3.2:1b', key='m3_ollama_model')
        st.caption('No API key needed. Run Ollama on this computer at localhost:11434.')
    elif provider == 'OpenAI':
        api_key = st.text_input('OpenAI API key', type='password', key='m3_openai_key')
        model = st.text_input('Model', value='gpt-4o-mini', key='m3_openai_model')
    elif provider == 'Google Gemini':
        api_key, model = gemini_sidebar()
    st.caption('Demo responses are deterministic rules, not generative AI.')
    if st.button('Reset all three rounds', key='m3_reset'):
        st.session_state.m3_history = []
        st.session_state.m3_dialogues = {}
        st.session_state.pop('m3_board_all', None)
        st.session_state.pop('m31_mentor', None)
        st.rerun()

st.progress(n / MAX_ROUNDS, text=f'{n} of {MAX_ROUNDS} rounds completed')
committed = {key: sum(item['increment'][key] for item in history) for key in CAPS}
remaining = BUDGET - sum(committed.values())
a, b, c = st.columns(3)
a.metric('Cumulative investment', f'₹{BUDGET - remaining} lakh')
b.metric('Remaining total budget', f'₹{remaining} lakh')
c.metric('Current round', 'Complete' if n == MAX_ROUNDS else f'{n+1} / {MAX_ROUNDS}')

if n < MAX_ROUNDS:
    round_guidance = [
        'Round 1 · Stabilise the business: choose your initial investments.',
        'Round 2 · Respond to feedback: add targeted investments and revise priorities.',
        'Round 3 · Final board review: optimise the remaining budget and explain trade-offs.'
    ]
    st.subheader(round_guidance[n])
    if n:
        prev = history[-1]['result']
        st.write(f"Previous modelled profit: **₹{prev['profit_lakh']:.1f} lakh**; "
                 f"satisfaction: **{prev['customer_satisfaction']:.0f}/100**; "
                 f"risk: **{prev['risk_level']}**.")
    with st.form('m3_round_form', clear_on_submit=False):
        st.markdown('**Additional investments this round (₹ lakh)**')
        cols = st.columns(3)
        increments = {}
        labels = {'marketing_lakh':'Marketing', 'technology_lakh':'Technology', 'training_lakh':'Employee training'}
        for col, (key, cap) in zip(cols, CAPS.items()):
            maximum = int(min(cap - committed[key], remaining))
            increments[key] = col.slider(f'{labels[key]} (remaining category cap: ₹{cap - committed[key]}L)',
                                         0, maximum, 0, 1, key=f'm3_{n}_{key}')
        spend = sum(increments.values())
        st.caption(f'This round: ₹{spend} lakh; cumulative after submission: ₹{BUDGET - remaining + spend} lakh')
        pricing = st.selectbox('Pricing choice for the revised strategy',
            ['Maintain current prices','Reduce prices by 5%','Increase prices by 5%'], key=f'm3_price_{n}')
        operations = st.selectbox('Operations choice for the revised strategy',
            ['Maintain current operations','Improve process efficiency','Expand store capacity'], key=f'm3_ops_{n}')
        rationale = st.text_area('CEO rationale (required)', key=f'm3_rationale_{n}',
                                 placeholder='Why this allocation, and what trade-off are you accepting?')
        reflection = st.text_area('Reflection (required: at least 12 words)', key=f'm3_reflection_{n}',
                                  placeholder='Round 1: explain your assumptions. Later rounds: what did you learn and why revise?')
        submit = st.form_submit_button('Submit CEO decision round', type='primary')
    if submit:
        try:
            record = run_round(history, increments, pricing, operations, rationale, reflection)
            history.append(record)
            st.session_state.m3_dialogues = {}
            st.session_state.pop('m3_board_all', None)
            st.session_state.pop('m31_mentor', None)
            st.rerun()
        except (ValueError, RuntimeError) as exc:
            st.error(str(exc))
else:
    st.success('All three rounds completed. Review the learning analytics and export the results.')

if history:
    latest = history[-1]
    r = latest['result']
    st.subheader('Latest CEO dashboard')
    cols = st.columns(3)
    cols[0].metric('Revenue', f"₹{r['revenue_crore']:.2f} Cr", f"{r['revenue_change_pct']:+.1f}%")
    cols[1].metric('Year-one profit', f"₹{r['profit_lakh']:.1f} L", f"{r['profit_change_lakh']:+.1f} L")
    cols[2].metric('Satisfaction', f"{r['customer_satisfaction']:.0f}/100")
    cols = st.columns(2)
    cols[0].metric('Market share', f"{r['market_share']:.1f}%")
    cols[1].metric('Learning score', f"{latest['assessment']['total']}/100")
    st.caption(f"Modelled risk: {r['risk_level']}. Year-one profit deducts cumulative one-time investment. "
               'These are revised scenario estimates, not realised business results.')

    st.subheader('Advisor challenge')
    render_board(latest['decision'], r, provider, api_key, model, 'm3_board_all')
    st.markdown('#### Ask an individual advisor')
    role = st.selectbox('Consult an advisor on your latest decision',
                        ['CFO','CMO','CHRO','COO','Risk Officer'], key='m3_role')
    with st.expander(f'{role} initial recommendation', expanded=True):
        st.write(get_advisor_recommendations(role, latest['decision'], r, provider, api_key, model))
    dialogue = st.session_state.m3_dialogues.setdefault(role, [])
    for turn in dialogue:
        with st.chat_message('user' if turn['speaker'] == 'CEO' else 'assistant'):
            st.markdown(turn['text'])
    with st.form('m3_ask', clear_on_submit=True):
        question = st.text_input('Question to advisor', max_chars=1200, key='m3_question')
        ask = st.form_submit_button('Ask advisor')
    if ask:
        if not question.strip():
            st.warning('Enter a question first.')
        else:
            answer = ask_advisor(role, question, latest['decision'], r, provider, api_key, model, dialogue)
            dialogue.extend([{'speaker':'CEO','text':question}, {'speaker':role,'text':answer}])
            st.rerun()

    st.subheader('Learning analytics: decisions across rounds')
    rows = learning_rows(history)
    frame = pd.DataFrame(rows)
    st.dataframe(frame, use_container_width=True, hide_index=True)
    fig = px.line(frame, x='Round', y='Year-one profit after investment (₹ lakh)', markers=True,
                  title='How revised strategies change the year-one profit estimate')
    fig.update_xaxes(dtick=1)
    st.plotly_chart(polish_chart(fig, legend=False), use_container_width=True)
    rubric = pd.DataFrame([{'Round': item['round'], **item['assessment']['dimensions']} for item in history])
    long_rubric = rubric.melt(id_vars='Round', var_name='Learning dimension', value_name='Score')
    st.plotly_chart(polish_chart(px.bar(long_rubric, x='Round', y='Score', color='Learning dimension',
                           barmode='group', range_y=[0,20], title='Rubric by round (0–20 per dimension)'), bottom=95),
                    use_container_width=True)
    st.caption('Rubric scores are rule-based formative indicators, not validated measures of managerial competence.')

    st.subheader('Explainable assessment')
    selected_round = st.selectbox('Explain score for round', list(range(1, len(history)+1)), index=len(history)-1)
    selected = history[selected_round-1]
    breakdown = explain_rubric(selected['decision'], selected['result'], selected['assessment'])
    for dimension, detail in breakdown.items():
        with st.expander(f"{dimension}: {detail['score']}/20"):
            for reason in detail['reasons']:
                st.write('• ' + reason)
            st.caption(detail['note'])
    st.caption('The reflection is required for learning evidence but is not automatically graded by the current numerical rubric.')

    st.subheader('CEO Mentor — whole-portfolio feedback')
    st.caption('Verified financial evidence is calculated by Python; Ollama/OpenAI/Gemini generate qualitative feedback only. Demo mode is rule-based.')
    if st.button('Generate CEO Mentor feedback'):
        st.session_state['m31_mentor'] = mentor_feedback(history, provider, api_key, model)
    if st.session_state.get('m31_mentor'):
        st.markdown(st.session_state['m31_mentor'])


    st.subheader('Downside sensitivity')
    shortfall = st.slider('Illustrative revenue shortfall (%)', 0, 30, 10, 5)
    downside = downside_sensitivity(latest, shortfall)
    x, y = st.columns(2)
    x.metric('Revenue under downside', f"₹{downside['revenue_lakh']:.1f} L")
    y.metric('Profit under downside', f"₹{downside['profit_lakh']:.1f} L")
    st.caption('Sensitivity holds modelled operating costs and cumulative investment fixed; '
               'it is not a probability-weighted forecast or cash-flow analysis.')

    st.subheader('Feedback and export')
    for item in latest['assessment']['feedback']:
        st.write('• ' + item)
    st.download_button('Download learning analytics (CSV)', frame.to_csv(index=False).encode('utf-8-sig'),
                       file_name='ceo_learning_analytics.csv', mime='text/csv')
    payload = {'scenario':'Aarohan Retail Pvt. Ltd. — fictional teaching case',
               'model_note':'Each round is a cumulative revision of the same year-one estimate.',
               'history':history}
    from io import StringIO
    summary = [
        '# CEO Learning Summary — Milestone 4.1.6.1',
        'Fictional teaching simulation; not a financial forecast.',
        f'Rounds completed: {len(history)}',
        f"Cumulative investment: ₹{r['investment_lakh']:.1f} lakh; remaining: ₹{BUDGET-r['investment_lakh']:.1f} lakh",
        f"Final revenue: ₹{r['revenue_crore']:.2f} crore; year-one profit: ₹{r['profit_lakh']:.1f} lakh",
        f"Final satisfaction: {Decimal(str(round(r['customer_satisfaction'], 2))).quantize(Decimal('0.1'), rounding=ROUND_HALF_UP)}/100; risk: {r['risk_level']}",
        f"Final formative score: {latest['assessment']['total']}/100",
        '', 'Round reflections:',
    ]
    for record in history:
        d = record['decision']
        summary.extend([f"Round {record['round']}: {record['reflection']}",
                        f"Pricing: {d['pricing']}; Operations: {d['operations']}",
                        f"CEO rationale: {d['rationale']}"])
    summary.extend(['', 'CEO Mentor:', st.session_state.get('m31_mentor', 'Not generated yet.'),
                    '', 'Scores are rule-based formative indicators, not validated competence measures.'])
    st.download_button('Download final CEO learning summary (TXT)', '\n'.join(summary),
                       file_name='ceo_learning_summary.txt', mime='text/plain')
    st.download_button('Download full decision portfolio (JSON)', 
                       json.dumps(payload, ensure_ascii=False, indent=2).encode('utf-8'),
                       file_name='ceo_decision_portfolio.json', mime='application/json')

st.divider()
st.caption('Interactive educational prototype · Data stored in current Streamlit session only. '
           'Avoid entering personal or confidential business information.')


st.caption("Developed by Dr. Sanjay Jain · Professor, Department of Computer Science & Applications · ITM University Gwalior, India. Educational simulation; fictional data and illustrative outcomes.")
