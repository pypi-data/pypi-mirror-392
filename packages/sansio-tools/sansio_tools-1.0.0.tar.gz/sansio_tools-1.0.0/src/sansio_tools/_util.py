def repr_helper(obj, d):
    s = ", ".join(f"{k}={str(v)}" for k, v in d.items())
    return f"{type(obj).__name__}({s})"
