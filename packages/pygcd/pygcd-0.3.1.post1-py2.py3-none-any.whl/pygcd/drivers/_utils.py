def iterdict(d):
    queue = list(d.items())
    while queue:
        k, v = queue.pop()
        if isinstance(v, dict):
            for _k, _v in v.items():
                queue.append((f"{k}:{_k}", _v))
        else:
            yield k, v
