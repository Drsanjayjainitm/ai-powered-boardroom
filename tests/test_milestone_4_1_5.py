from unittest.mock import patch
from agents.grounding import safe_qualitative, fallback_coaching
from agents.ceo_mentor import _validated_ai_sections
from agents.dialogue import ask_advisor
from test_gemini_reliability_4_1_3 import DECISION, RESULT


def test_financial_vocabulary_accepted():
    assert safe_qualitative('Discuss why profit and revenue may move differently after investment, and identify what evidence would clarify the trade-off.')


def test_numeric_claims_still_rejected():
    assert safe_qualitative('Your profit is ₹200 lakh; this guarantees a return.') is None


def test_role_specific_fallbacks():
    assert 'conversion' in fallback_coaching('CMO')
    assert 'fulfilment' in fallback_coaching('COO')
    assert fallback_coaching('CMO') != fallback_coaching('CFO')


def test_followup_financial_vocabulary():
    answer = 'Profit may lag revenue because an upfront implementation expense affects the first-year estimate. Which cost assumption would you verify first?'
    with patch('agents.dialogue._call_gemini', return_value=answer):
        result = ask_advisor('CFO', 'Why does profit fall?', DECISION, RESULT, 'Google Gemini', 'secret', 'model')
    assert 'AI-generated qualitative coaching' in result


def test_mentor_bold_headings():
    answer = ('**Strategic Strengths**\nThe rationale connects capability building with a measured rollout.\n'
              '**Financial and Risk Trade-offs**\nThe learner recognizes the tension between short-term performance and longer-term resilience.\n'
              '**Reflection and Learning**\nThe reflection proposes a more phased approach to future decisions.')
    assert _validated_ai_sections(answer)
