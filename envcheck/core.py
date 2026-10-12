import re

_KEY = re.compile(r"^[A-Za-z_][A-Za-z0-9_.\-]*$")


def _parse_value(raw):
    raw = raw.strip()
    if not raw:
        return ""
    q = raw[0]
    if q in "\"'":
        end = raw.find(q, 1)
        while q == '"' and end > 0 and raw[end - 1] == "\\":
            end = raw.find(q, end + 1)
        if end != -1:
            return raw[1:end]
        return raw[1:]
    m = re.search(r"\s#", raw)
    if m:
        raw = raw[: m.start()]
    return raw.strip()


def parse_env(text):
    """Parse env text into a dict of key -> value."""
    result = {}
    for line in text.splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        if line.startswith("export ") or line.startswith("export\t"):
            line = line[7:].lstrip()
        key, _, val = line.partition("=")
        key = key.strip()
        if not _KEY.match(key):
            continue
        result[key] = _parse_value(val)
    return result


def compare(example, env):
    """Return sorted key-name lists: missing, extra, empty."""
    return {
        "missing": sorted(k for k in example if k not in env),
        "extra": sorted(k for k in env if k not in example),
        "empty": sorted(k for k, v in env.items() if v == ""),
    }
