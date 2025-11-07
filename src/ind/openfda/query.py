from .schema import load_registry_for

def q(field: str, term: str, *, endpoint: str) -> str:
    """Builds a safe search fragment: field:"term" with quoting/validation."""
    reg = load_registry_for(endpoint)
    if not reg.has(field):
        sugg = reg.suggest(field)
        hint = f" Did you mean: {', '.join(sugg)}?" if sugg else ""
        raise ValueError(f"Unknown field '{field}' for {endpoint}.{hint}")
    # Quote term if it has spaces/specials; escape quotes
    needs_quotes = any(c.isspace() or c in ':/()' for c in term)
    safe = term.replace('"', r'\"')
    return f'{field}:"{safe}"' if needs_quotes else f"{field}:{safe}"