"""On-demand, session-persistent five-advisor board review."""
import hashlib
import json
import streamlit as st
from agents.advisors import get_advisor_recommendations
from agents.grounding import verified_advisor_markdown

ROLES = ('CFO', 'CMO', 'CHRO', 'COO', 'Risk Officer')

def render_board(decision, result, provider, api_key, model, state_key):
    """Keep five advisor outputs visible without repeating calls on reruns."""
    signature_data = {'decision': decision, 'result': result, 'provider': provider, 'model': model,
                      'credential_configured': bool(api_key)}
    signature = hashlib.sha256(json.dumps(signature_data, sort_keys=True, default=str).encode()).hexdigest()
    saved = st.session_state.get(state_key)
    if saved and saved.get('signature') != signature:
        st.session_state.pop(state_key, None)
        saved = None
    st.markdown('#### AI Board of Directors — all five perspectives')
    st.caption('Generate all five recommendations for the latest decision, then compare them side by side. '
               'Outputs stay on screen during this browser session. Refreshing other controls does not repeat API calls.')
    if st.button('Generate / refresh all five advisor recommendations', key=state_key + '_generate'):
        # One click may trigger five provider requests. Never auto-call on rerender.
        responses = {}
        with st.spinner('Consulting the five advisors…'):
            for role in ROLES:
                responses[role] = get_advisor_recommendations(role, decision, result, provider, api_key, model)
        st.session_state[state_key] = {'signature': signature, 'responses': responses}
        saved = st.session_state[state_key]
    if not saved:
        st.info('Click the button to display all five advisor outcomes. In Gemini mode, this uses up to five API requests.')
        return
    st.markdown('##### Shared verified financial evidence')
    st.markdown(verified_advisor_markdown(decision, result))
    st.markdown('##### Advisor-specific perspectives')
    for start in (0, 2, 4):
        pair = ROLES[start:start+2]
        cols = st.columns(len(pair))
        for col, role in zip(cols, pair):
            with col:
                with st.container(border=True):
                    st.markdown(f'**{role}**')
                    response = saved['responses'][role]
                    # The financial facts are already shown once above. Keep
                    # each advisor's qualitative feedback and its source label.
                    evidence = verified_advisor_markdown(decision, result)
                    if response.startswith(evidence):
                        response = response[len(evidence):].strip()
                    st.markdown(response)
    st.caption('Python computes the verified financial evidence. AI commentary is screened; fallback text is labelled.')
