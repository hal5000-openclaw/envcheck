import io
import json
import os
import tempfile
import unittest
from contextlib import redirect_stdout, redirect_stderr

from envcheck.core import parse_env, compare
from envcheck.cli import main


class ParseTests(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(parse_env("A=1\nB=two"), {"A": "1", "B": "two"})

    def test_export(self):
        self.assertEqual(parse_env("export A=1"), {"A": "1"})

    def test_quotes(self):
        self.assertEqual(parse_env('A="x # y"\nB=\'z\''), {"A": "x # y", "B": "z"})

    def test_comments_blank(self):
        self.assertEqual(parse_env("# c\n\nA=1 # tail\n"), {"A": "1"})

    def test_empty_values(self):
        self.assertEqual(parse_env('A=\nB=""'), {"A": "", "B": ""})


class CompareTests(unittest.TestCase):
    def test_compare(self):
        r = compare({"A": "", "B": ""}, {"B": "", "C": "x"})
        self.assertEqual(r, {"missing": ["A"], "extra": ["C"], "empty": ["B"]})


class CliTests(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.TemporaryDirectory()
        self.addCleanup(self.d.cleanup)

    def w(self, name, text):
        p = os.path.join(self.d.name, name)
        with open(p, "w") as f:
            f.write(text)
        return p

    def run_cli(self, *args):
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            code = main(list(args))
        return code, out.getvalue()

    def test_ok(self):
        ex = self.w("ex", "A=\nB=\n")
        e = self.w("e", "A=1\nB=2\n")
        self.assertEqual(self.run_cli("--example", ex, e)[0], 0)

    def test_missing_and_no_values_printed(self):
        ex = self.w("ex", "A=\nSECRET=\n")
        e = self.w("e", "A=hunter2\n")
        code, out = self.run_cli("--example", ex, e)
        self.assertEqual(code, 1)
        self.assertIn("SECRET", out)
        self.assertNotIn("hunter2", out)

    def test_extra_allowed(self):
        ex = self.w("ex", "A=\n")
        e = self.w("e", "A=1\nZ=9\n")
        self.assertEqual(self.run_cli("--example", ex, e)[0], 1)
        self.assertEqual(self.run_cli("--example", ex, "--allow-extra", e)[0], 0)

    def test_json_multi(self):
        ex = self.w("ex", "A=\n")
        e1 = self.w("e1", "A=1\n")
        e2 = self.w("e2", "A=\n")
        code, out = self.run_cli("--example", ex, "--json", e1, e2)
        self.assertEqual(code, 1)
        data = json.loads(out)
        self.assertEqual(data["files"][e2]["empty"], ["A"])
        self.assertEqual(data["files"][e1]["empty"], [])

    def test_file_error(self):
        self.assertEqual(self.run_cli("--example", "/nonexistent/x", "/nonexistent/y")[0], 2)

    def test_usage_error(self):
        self.assertEqual(self.run_cli("--bogus")[0], 2)


if __name__ == "__main__":
    unittest.main()
