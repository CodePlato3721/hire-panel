def format_criteria(criteria) -> str:
    return "\n".join(f"- **{c['name']}**: {c['description']}" for c in criteria)
