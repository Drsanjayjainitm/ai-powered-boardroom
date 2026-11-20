from agents.grounding import safe_qualitative, sanitize_ai_prose
from agents.ceo_mentor import _validated_ai_sections


def test_fenced_python_removed_from_advisor_response():
    raw = '''```python
trends = {"revenue": "up", "profit": "down"}
print(trends)
```
The investment is deducted from year-one profit. Compare the operating contribution separately from implementation spending.'''
    clean = safe_qualitative(raw)
    assert clean and 'investment' in clean
    assert 'trends' not in clean and 'print(' not in clean


def test_unfenced_python_removed_from_advisor_response():
    raw = '''# DECISION FACTS
trends = {
    "revenue": "up",
    "profit": "down"
}
Focus on testing whether the planned investment produces a sustainable benefit, while monitoring the operating contribution and preserving contingency flexibility.'''
    clean = safe_qualitative(raw)
    assert clean and 'Focus on testing' in clean
    assert 'trends' not in clean and '"revenue"' not in clean


def test_numeric_claim_still_rejected():
    assert safe_qualitative('Revenue is ₹300 lakh, which proves that our business has already recovered and will grow.') is None


def test_mentor_heading_variations_and_decision_mentions():
    answer = '''**Strategic Strengths:**
The student connects training with service quality and explains why change readiness matters to employees.

**Financial & Risk Trade-offs:**
The one-time investment reduces year-one profit in this model, so phased commitments may preserve flexibility.

**Reflection & Learning:**
The learner recognizes a trade-off between customer satisfaction and immediate profitability and proposes measurable review checkpoints.'''
    result = _validated_ai_sections(answer)
    assert result and '### Strategic Strengths' in result
    assert '### Financial and Risk Trade-offs' in result
    assert '### Reflection and Learning' in result


def test_mentor_code_and_numbers_excluded():
    answer = '''### Strategic Strengths
The CEO explains the importance of employee readiness and links technology investment to customer experience.
```python
facts = {"revenue": "up"}
```
### Financial and Risk Trade-offs
The investment is a one-time year-one deduction, so compare underlying performance with the cost of implementation.
Revenue was ₹900 lakh.
### Reflection and Learning
The reflection identifies phased spending and measurable performance reviews as useful next steps for the team.'''
    result = _validated_ai_sections(answer)
    assert result and 'facts' not in result and '₹900' not in result
