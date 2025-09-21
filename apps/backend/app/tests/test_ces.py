from app.ingest.ces import Event

def test_fingerprint_stable():
    e1 = Event(source="rss", occurred_at=1, entity_type="topic", entity_id="ai", type="news", title="Hello")
    e2 = Event(source="rss", occurred_at=1, entity_type="topic", entity_id="ai", type="news", title="Hello")
    assert e1.fingerprint() == e2.fingerprint()
