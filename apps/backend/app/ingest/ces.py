from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional
import hashlib, json

@dataclass
class Metric:
    name: str
    value: float
    unit: Optional[str] = None

@dataclass
class Event:
    source: str
    occurred_at: int
    entity_type: str
    entity_id: str
    type: str
    title: str
    body: str = ""
    severity_raw: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    metrics: Dict[str, float] = field(default_factory=dict)
    links: List[str] = field(default_factory=list)
    extras: Dict[str, Any] = field(default_factory=dict)

    def fingerprint(self) -> str:
        core = {
            "source": self.source,
            "occurred_at": self.occurred_at,
            "entity_type": self.entity_type,
            "entity_id": self.entity_id,
            "type": self.type,
            "title": self.title,
        }
        h = hashlib.sha256(json.dumps(core, sort_keys=True).encode()).hexdigest()
        return f"{self.source}:{h[:20]}"

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        d["id"] = self.fingerprint()
        return d
