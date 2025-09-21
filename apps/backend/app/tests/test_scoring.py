from app.services.scoring import score

def test_score_bounds():
    s = score({"impact_finance": 1.0, "actionability": 1.0, "urgency": 1.0, "personal_relevance": 1.0})
    assert 0.0 <= s <= 1.0

def test_score_increases_with_impact():
    s1 = score({"impact_finance": 0.1, "actionability": 0.5, "urgency": 0.2, "personal_relevance": 0.5})
    s2 = score({"impact_finance": 0.9, "actionability": 0.5, "urgency": 0.2, "personal_relevance": 0.5})
    assert s2 > s1
