# Scoring v1 (Explainable Heuristics)
S ∈ [0,1] = w1*Impact + w2*Actionability + w3*Urgency + w4*PersonalRelevance.

- Finance impact: |pct_change| * portfolio_exposure_weight (capped)
- Health impact: z-score vs personal baseline
- News impact: source_cred * topic_relevance
- Actionability: presence of concrete next step; market open; patch available
- Urgency: short windows, expiries, steep slopes
- PersonalRelevance: exposure, ownership, user interests

Store top contributors in `explain` for transparency.
