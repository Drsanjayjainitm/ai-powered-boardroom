from unittest.mock import patch
from agents.dialogue import ask_advisor
from agents.ceo_mentor import mentor_feedback, _validated_ai_sections

DECISION = {'pricing':'Maintain current prices','operations':'Improve process efficiency','marketing_lakh':8,'technology_lakh':10,'training_lakh':4,'rationale':'Phased investment'}
RESULT = {'revenue_crore':2.63232,'profit_lakh':36.552,'investment_lakh':22,'customer_satisfaction':83.5,'risk_level':'Low','revenue_change_pct':5.29}
HISTORY = [{'round':1,'decision':DECISION,'result':RESULT,'assessment':{'total':88},'reflection':'I learned to compare tradeoffs.'}]

def test_gemini_followup_accepted():
    answer = 'Test the evidence behind the current approach and compare alternative explanations. Which assumption would you challenge first?'
    with patch('agents.dialogue._call_gemini', return_value=answer):
        result = ask_advisor('CFO','Why is profit falling?',DECISION,RESULT,'Google Gemini','secret','test-model')
    assert 'AI-generated qualitative coaching (screened)' in result
    assert '₹36.55' in result

def test_gemini_followup_numeric_rejected():
    with patch('agents.dialogue._call_gemini', return_value='The profit is ₹99 lakh and the investment is 30 lakh.'):
        result = ask_advisor('CFO','Why is profit falling?',DECISION,RESULT,'Google Gemini','secret','test-model')
    assert 'rule-based fallback' in result
    assert '₹99' not in result

def test_mentor_sections_accepted():
    answer = '''### Strategic Strengths
The rationale shows thoughtful attention to customer experience and the practical sequence of implementation.
### Financial and Risk Trade-offs
The reflection recognizes tension between near-term outcomes and longer-term objectives. Test assumptions before expanding commitments.
### Reflection and Learning
The learner explicitly identifies phased implementation as a way to make decisions more accountable and adaptable.'''
    assert _validated_ai_sections(answer)
    with patch('agents.ceo_mentor._call_gemini', return_value=answer):
        result = mentor_feedback(HISTORY,'Google Gemini','secret','test-model')
    assert 'AI-generated narrative' in result
    assert 'Verified Performance Evidence' in result
    assert 'Two Feasible Next Actions' in result

def test_mentor_rejects_missing_sections():
    assert _validated_ai_sections('### Strategic Strengths\nExcellent decision.') is None

def test_mentor_discards_numeric_lines():
    answer = '''### Strategic Strengths
Thoughtful attention to customer experience.
### Financial and Risk Trade-offs
Profit is ₹999 lakh.
Test assumptions with care.
### Reflection and Learning
The reflection identifies the importance of phased implementation.'''
    safe = _validated_ai_sections(answer)
    assert safe is not None
    assert '₹999' not in safe
