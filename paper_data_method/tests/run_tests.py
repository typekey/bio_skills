"""Regression test: every examples/*.json must regenerate its expected SVG exactly,
with no overflow warnings.   Usage: python -I tests/run_tests.py   (from paper_data_method/)
To accept an intended style change, regenerate with --update."""
import io
import os
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
GEN = os.path.join(ROOT, "scripts", "gen_mindmap.py")
EX = os.path.join(ROOT, "examples")
EXPECTED = os.path.join(HERE, "expected")
update = "--update" in sys.argv
env = dict(os.environ, PYTHONIOENCODING="utf-8")
failed = 0

for name in sorted(f for f in os.listdir(EX) if f.endswith(".json")):
    stem = name[:-5]
    out = os.path.join(tempfile.mkdtemp(), stem + ".svg")
    r = subprocess.run([sys.executable, "-I", GEN, os.path.join(EX, name), out],
                       capture_output=True, env=env)
    err = r.stderr.decode("utf-8", "replace")
    got = io.open(out, encoding="utf-8").read() if os.path.exists(out) else ""
    exp_path = os.path.join(EXPECTED, stem + ".svg")
    if update:
        io.open(exp_path, "w", encoding="utf-8", newline="").write(got)
        print("updated", stem)
        continue
    exp = io.open(exp_path, encoding="utf-8").read()
    problems = []
    if r.returncode != 0:
        problems.append("generator failed")
    if "WARN" in err:
        problems.append("overflow warnings:\n" + err)
    if got != exp:
        problems.append("output differs from expected/" + stem + ".svg")
    print(("FAIL " if problems else "ok   ") + stem)
    for p in problems:
        print("   ", p)
    failed += bool(problems)

sys.exit(1 if failed else 0)
