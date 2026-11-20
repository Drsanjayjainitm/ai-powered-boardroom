import unittest
from unittest.mock import patch
from simulation.multiround import run_round
from agents.ceo_mentor import verified_facts, mentor_feedback

class MentorV3Tests(unittest.TestCase):
    def setUp(self):
        self.history = []
        for amounts in [(8,10,4),(4,5,3),(2,3,2)]:
            record = run_round(self.history, dict(zip(('marketing_lakh','technology_lakh','training_lakh'),amounts)),
                'Maintain current prices','Improve process efficiency',
                'I balance customer outcomes with investments.',
                'I learned that revenue can rise while profits fall because the initial recovery investment creates short term pressure.')
            self.history.append(record)

    def test_verified_numbers(self):
        f = verified_facts(self.history)
        self.assertEqual(f['final_revenue_lakh'],268.02)
        self.assertEqual(f['revenue_vs_baseline_lakh'],18.02)
        self.assertEqual(f['final_profit_lakh'],23.54)
        self.assertEqual(f['profit_vs_baseline_lakh'],-16.46)
        self.assertEqual(f['investment_lakh'],41)
        self.assertEqual(f['remaining_budget_lakh'],9)
        self.assertEqual(f['final_risk'],'Moderate')

    @patch('agents.ceo_mentor._call_ollama')
    def test_llm_wrong_numeric_claim_removed(self, mock):
        mock.return_value = ('### Strategic Strengths\nThe CEO links technology to customer experience.\n'
            'Revenue declined by ₹18 lakh.\n### Financial and Risk Trade-offs\n'
            'The higher investment creates an immediate profit trade-off, requiring careful evaluation.\n'
            '### Reflection and Learning\nThe learner acknowledges the profit trade-off and favors phased decisions.\n'
            '### Two Feasible Next Actions and One CEO Question\n'
            'Compare a lower-spend option under the same assumptions.\n'
            'Track customer satisfaction and payback before scaling.\n'
            'What evidence would justify the next investment?')
        output = mentor_feedback(self.history,'Ollama (local, free)',model='llama3.2:1b')
        self.assertIn('₹268.02',output)
        self.assertIn('+18.02',output)
        self.assertNotIn('Revenue declined by ₹18',output)
        mock.assert_called_once()

    @patch('agents.ceo_mentor._call_ollama', return_value='Revenue fell by ₹20 lakh.')
    def test_short_bad_output_falls_back(self, mock):
        output = mentor_feedback(self.history,'Ollama (local, free)',model='llama3.2:1b')
        self.assertIn('rule-based fallback',output)
        self.assertNotIn('Revenue fell by ₹20',output)

    def test_demo_mode(self):
        output = mentor_feedback(self.history)
        self.assertIn('₹9.00 lakh',output)
        self.assertIn('rule-based Demo mode',output)

if __name__=='__main__': unittest.main()
