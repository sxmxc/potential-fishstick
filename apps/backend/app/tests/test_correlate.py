from app.services.correlate import should_merge

def test_merge_same_entity_close_time():
    a = {"entity_id":"ETH", "occurred_at": 1000, "tags":[]}
    b = {"entity_id":"ETH", "occurred_at": 1000 + 10*60*1000, "tags":[]}
    assert should_merge(a,b) is True

def test_no_merge_far_apart():
    a = {"entity_id":"ETH", "occurred_at": 1000, "tags":[]}
    b = {"entity_id":"ETH", "occurred_at": 1000 + 60*60*1000, "tags":[]}
    assert should_merge(a,b) is False

def test_merge_shared_tag():
    a = {"entity_id":"AAPL", "occurred_at": 0, "tags":["finance"]}
    b = {"entity_id":"ETH", "occurred_at": 0, "tags":["finance"]}
    assert should_merge(a,b) is True
