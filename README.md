# envcheck

A small, stdlib-only Python 3 CLI that compares a `.env.example` template with one or more `.env` files.

It reports keys that are **missing**, **extra** (undocumented) and **empty**. It prints key names only, never values, so the output is safe to paste into CI logs.

## Why

Config drift between `.env.example` and real env files causes "works on my machine" bugs. This catches it in seconds without any dependencies.

## Install

    pip install .        # provides the `envcheck` command
    # or run in place:
    python -m envcheck

## Usage

    python -m envcheck                          # .env.example vs .env
    python -m envcheck --example tpl.env prod.env staging.env
    python -m envcheck --allow-extra --json

Options: `--example PATH` (default `.env.example`), positional env files (default `.env`), `--allow-extra` (extra keys are not a problem), `--json`.

Parsed syntax: `KEY=VAL`, `export KEY=VAL`, single/double quotes, `#` comments (full-line and trailing after whitespace), blank lines.

Example output:

    .env:
      missing: DATABASE_URL
      extra: OLD_FLAG
      empty: API_KEY

## Exit codes

- 0: no problems
- 1: missing, extra (unless `--allow-extra`) or empty keys found
- 2: usage error or unreadable file

## Tests

    python -m unittest discover -s tests
