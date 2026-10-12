import argparse
import json
import sys

from .core import parse_env, compare


def _load(path):
    with open(path, encoding="utf-8") as f:
        return parse_env(f.read())


def main(argv=None):
    p = argparse.ArgumentParser(
        prog="envcheck",
        description="Compare .env files with a .env.example template (key names only).",
    )
    p.add_argument("envfiles", nargs="*", default=None, help="env files (default .env)")
    p.add_argument("--example", default=".env.example", help="template path")
    p.add_argument("--allow-extra", action="store_true", help="do not fail on extra keys")
    p.add_argument("--json", action="store_true", help="JSON output")
    try:
        args = p.parse_args(argv)
    except SystemExit as e:
        return 2 if e.code else 0
    files = args.envfiles or [".env"]
    try:
        example = _load(args.example)
        envs = [(f, _load(f)) for f in files]
    except (OSError, UnicodeDecodeError) as e:
        print("envcheck: cannot read %s" % getattr(e, "filename", None) or "file", file=sys.stderr)
        return 2

    problems = False
    report = {}
    for name, env in envs:
        r = compare(example, env)
        if args.allow_extra:
            r["extra"] = []
        if r["missing"] or r["extra"] or r["empty"]:
            problems = True
        report[name] = r

    if args.json:
        print(json.dumps({"ok": not problems, "files": report}, indent=2))
    else:
        for name, r in report.items():
            if not any(r.values()):
                print("%s: OK" % name)
                continue
            print("%s:" % name)
            for kind in ("missing", "extra", "empty"):
                for k in r[kind]:
                    print("  %s: %s" % (kind, k))
    return 1 if problems else 0
