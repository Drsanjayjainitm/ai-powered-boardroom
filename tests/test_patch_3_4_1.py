import unittest
from unittest.mock import patch
from agents.grounding import verified_advisor_facts, verified_advisor_markdown, safe_qualitative
from agents.advisors import get_advisor_recommendations
from agents.dialogue import ask_advisor
from agents.ceo_mentor import _verified_actions

DECISION = {'pricing':'Maintain current prices', 'operations':'Improve process efficiency'}
RESULT = {'revenue_crore':2.68016,'profit_lakh':23.536,'investment_lakh':41,
          'customer_satisfaction':93.65,'risk_level':'Moderate'}
HISTORY = [{'decision':dict(DECISION)}, {'decision':dict(DECISION)}, {'decision':dict(DECISION)}]

class PatchTests(unittest.TestCase):
    def test_advisor_verified_revenue_direction(self):
        f=verified_advisor_facts(DECISION,RESULT)
        self.assertEqual(f['revenue_delta_lakh'],18.02)
        self.assertEqual(f['profit_delta_lakh'],-16.46)
        t=verified_advisor_markdown(DECISION,RESULT)
        self.assertIn('increased by **₹18.02 lakh**',t)
        self.assertIn('decreased by **₹16.46 lakh**',t)
    def test_numeric_hallucination_rejected(self):
        self.assertIsNone(safe_qualitative('The company has a revenue loss of ₹18 lakh.'))
        self.assertIsNone(safe_qualitative('Profit declined because of the reserve.'))
    def test_advisor_fallback_for_wrong_llm(self):
        with patch('agents.advisors._call_ollama',return_value='Revenue fell by ₹18 lakh, which is bad.'):
            answer=get_advisor_recommendations('CFO',DECISION,RESULT,'Ollama (local, free)')
        self.assertIn('increased by **₹18.02 lakh**',answer)
        self.assertIn('rule-based fallback',answer)
        self.assertNotIn('Revenue fell',answer)
    def test_followup_fallback_for_wrong_llm(self):
        with patch('agents.dialogue._call_ollama',return_value='The reserve caused a profit decline of ₹16 lakh.'):
            answer=ask_advisor('CFO','Why did profit fall?',DECISION,RESULT,'Ollama (local, free)')
        self.assertIn('decreased by **₹16.46 lakh**',answer)
        self.assertIn('rule-based fallback',answer)
        self.assertNotIn('reserve caused',answer)
    def test_valid_qualitative_is_labelled(self):
        with patch('agents.advisors._call_ollama',return_value='Ask the learner to compare assumptions with alternative evidence before committing to a plan. What would change your mind?'):
            answer=get_advisor_recommendations('CMO',DECISION,RESULT,'Ollama (local, free)')
        self.assertIn('AI-generated qualitative coaching',answer)
    def test_unchanged_operations_actions(self):
        actions=_verified_actions(HISTORY)
        self.assertIn('Test an alternative operating strategy',actions)
        self.assertNotIn('previous operations choice',actions)
        self.assertEqual(actions.count('\n- '),2)
    def test_changed_operations_actions(self):
        h=[{'decision':dict(DECISION)},{'decision':{**DECISION,'operations':'Maintain current operations'}}]
        self.assertIn('previous choice',_verified_actions(h))

if __name__=='__main__': unittest.main()
