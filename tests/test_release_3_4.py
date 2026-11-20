import unittest
from unittest.mock import patch
from simulation.multiround import run_round, validate_round, learning_rows, downside_sensitivity
from agents.ceo_mentor import mentor_feedback, decision_change_lines, verified_facts

WORDS = 'I understand that revenue growth may improve customer experience but investment spending can reduce immediate year one profitability.'
RAT = 'We invest carefully while reviewing business risk and financial sustainability.'


def sample_history(ops=('Improve process efficiency', 'Improve process efficiency', 'Maintain current operations')):
    history = []
    for i, (m, t, h) in enumerate(((8,10,4),(4,5,3),(2,3,2))):
        history.append(run_round(history, dict(marketing_lakh=m, technology_lakh=t, training_lakh=h),
                                 'Maintain current prices', ops[i], RAT, WORDS))
    return history


class ReleaseTests(unittest.TestCase):
    def test_identical_inputs_identical_outputs(self):
        self.assertEqual(sample_history(), sample_history())

    def test_reproduces_uploaded_portfolio(self):
        f = verified_facts(sample_history())
        self.assertEqual((f['final_revenue_lakh'],f['final_profit_lakh'],f['final_satisfaction'],f['final_score']),
                         (263.02,12.74,91.65,84))

    def test_cumulative_caps(self):
        history = sample_history()[:2]
        with self.assertRaisesRegex(ValueError,'exceeds'):
            validate_round(history, dict(marketing_lakh=14,technology_lakh=5,training_lakh=0))
        with self.assertRaisesRegex(ValueError,'exceeds'):
            validate_round(history, dict(marketing_lakh=12,technology_lakh=8,training_lakh=3))

    def test_required_reflection_and_rationale(self):
        args = ([], dict(marketing_lakh=1,technology_lakh=1,training_lakh=1),
                'Maintain current prices','Maintain current operations')
        with self.assertRaisesRegex(ValueError,'Reflection'):
            run_round(*args, RAT, 'too short')
        with self.assertRaisesRegex(ValueError,'rationale'):
            run_round(*args, ' ', WORDS)

    def test_decision_changes_not_invented(self):
        lines = ' '.join(decision_change_lines(sample_history()))
        self.assertIn('Pricing remained unchanged', lines)
        self.assertIn('Operations changed', lines)
        self.assertIn('Round 3: Maintain current operations', lines)

    @patch('agents.ceo_mentor._call_ollama')
    def test_mentor_enforces_two_actions(self, mock):
        mock.return_value = '''### Strategic Strengths
The CEO retained a contingency reserve and linked investment to customer experience.
### Financial and Risk Trade-offs
The changing operations choice should be evaluated against the previous efficiency strategy.
### Reflection and Learning
The learner recognizes that improved revenue does not guarantee immediate profitability and suggests phased investment.
### Two Feasible Next Actions and One CEO Question
- Invest everything immediately.
- Raise prices sharply.
- Hire a new team.
- Acquire another business.
Question: Why not?'''
        out = mentor_feedback(sample_history(), 'Ollama (local, free)', model='llama3.2:1b')
        section = out.split('### Two Feasible Next Actions and One CEO Question')[-1]
        self.assertEqual(section.count('\n- '), 2)
        self.assertIn('Pricing remained unchanged',out)
        self.assertNotIn('Raise prices sharply',out)

    @patch('agents.ceo_mentor._call_ollama', side_effect=TimeoutError('offline'))
    def test_ollama_unavailable_keeps_verified_facts(self, mock):
        out = mentor_feedback(sample_history(), 'Ollama (local, free)', model='llama3.2:1b')
        self.assertIn('₹263.02', out)
        self.assertIn('AI mentor unavailable', out)

    def test_export_rows_and_sensitivity(self):
        h = sample_history()
        rows = learning_rows(h)
        self.assertEqual(len(rows),3)
        self.assertEqual(rows[-1]['Operations'],'Maintain current operations')
        self.assertEqual(rows[-1]['Total investment (₹ lakh)'],41)
        result = downside_sensitivity(h[-1], 0)
        self.assertAlmostEqual(result['profit_lakh'], h[-1]['result']['profit_lakh'], places=2)

if __name__ == '__main__': unittest.main()
