from typing import Dict, Any

def feature_vector(evt: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, float]:
    f: Dict[str, float] = {}
    t = evt.get("type")
    metrics = evt.get("metrics", {})
    if t == "price_move":
        pct = float(metrics.get("pct_change", 0.0))
        exposure = float(context.get("portfolio_exposure", 0.0))
        f["impact_finance"] = min(1.0, abs(pct) * exposure)
        f["urgency"] = min(1.0, abs(metrics.get("pct_change_5m", pct)))
        f["actionability"] = 1.0 if context.get("market_open", True) else 0.3
    elif t == "health_anomaly":
        z = float(metrics.get("rhr_z", 0.0))
        f["impact_health"] = min(1.0, abs(z) / 3.0)
        f["urgency"] = 0.4 if int(metrics.get("days_persistent", 0)) >= 3 else 0.2
        f["actionability"] = 0.6
    elif t == "news":
        cred = float(metrics.get("credibility", 0.3))
        rel = float(metrics.get("topic_relevance", 0.3))
        f["impact_news"] = cred * rel
        f["actionability"] = 0.5 if metrics.get("has_action", False) else 0.2
        f["urgency"] = float(metrics.get("velocity", 0.2))
    f["personal_relevance"] = float(context.get("personal_relevance", 0.5))
    return f
