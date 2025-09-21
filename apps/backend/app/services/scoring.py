from typing import Dict

def score(f: Dict[str, float]) -> float:
    impact = max(f.get("impact_finance", 0.0), f.get("impact_health", 0.0), f.get("impact_news", 0.0))
    actionability = f.get("actionability", 0.5)
    urgency = f.get("urgency", 0.2)
    relevance = f.get("personal_relevance", 0.5)
    s = 0.4 * impact + 0.25 * actionability + 0.2 * urgency + 0.15 * relevance
    return max(0.0, min(1.0, s))
