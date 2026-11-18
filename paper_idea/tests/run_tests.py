"""Regression test: every examples/*.json must regenerate its expected SVG exactly,
with no overflow warnings.   Usage: python -I tests/run_tests.py   (from paper_idea/)
To accept an intended style change: python -I tests/run_tests.py --update"""
import io
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
GEN = os.path.join(ROOT, "scripts", "gen_logic_flow.py")
EX = os.path.join(ROOT, "examples")
EXPECTED = os.path.join(HERE, "expected")
update = "--update" in sys.argv
env = dict(os.environ, PYTHONIOENCODING="utf-8")
failed = 0
for name in sorted(f for f in os.listdir(EX) if f.endswith(".json")):
    stem = name[:-5]
    out = os.path.join(tempfile.mkdtemp(), stem + ".svg")
    r = subprocess.run([sys.executable, "-I", GEN, os.path.join(EX, name), out], capture_output=True, env=env)
    err = r.stderr.decode("utf-8", "replace")
    got = io.open(out, encoding="utf-8").read() if os.path.exists(out) else ""
    exp_path = os.path.join(EXPECTED, stem + ".svg")
    if update:
        io.open(exp_path, "w", encoding="utf-8", newline="").write(got)
        print("updated", stem)
        continue
    exp = io.open(exp_path, encoding="utf-8").read() if os.path.exists(exp_path) else None
    problems = []
    if r.returncode != 0:
        problems.append("exit code %d" % r.returncode)
    if "WARN" in err:
        problems.append(err.strip())
    if exp is None:
        problems.append("no expected SVG (run with --update)")
    elif got != exp:
        problems.append("SVG differs from expected")
    print(("FAIL " if problems else "ok   ") + stem + ("  -> " + "; ".join(problems) if problems else ""))
    failed += bool(problems)
sys.exit(1 if failed else 0)
