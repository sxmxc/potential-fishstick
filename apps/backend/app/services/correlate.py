def should_merge(a: dict, b: dict) -> bool:
    same_entity = (a.get("entity_id") == b.get("entity_id"))
    close_in_time = abs(int(a.get("occurred_at", 0)) - int(b.get("occurred_at", 0))) <= 15 * 60 * 1000
    share_tag = bool(set(a.get("tags", [])) & set(b.get("tags", [])))
    return (same_entity and close_in_time) or share_tag
