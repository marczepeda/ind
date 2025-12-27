def _coerce_first(xs, default: str = "") -> str:
    if isinstance(xs, list):
        return xs[0] if xs else default
    return xs or default