"""render_png.py — SVG -> PNG through headless Chrome/Edge (no extra Python deps).
Usage: python -I render_png.py in.svg out.png
Reads width/height from the <svg> tag, so the whole image is captured."""
import io
import os
import pathlib
import re
import shutil
import subprocess
import sys

CANDIDATES = [
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
]
for name in ("google-chrome", "chromium", "chromium-browser", "chrome", "msedge"):
    p = shutil.which(name)
    if p:
        CANDIDATES.append(p)
exe = next((c for c in CANDIDATES if os.path.exists(c)), None)
if not exe:
    sys.exit("no Chrome/Edge/Chromium found; open the SVG in a browser instead")
src, dst = pathlib.Path(sys.argv[1]).resolve(), pathlib.Path(sys.argv[2]).resolve()
head = io.open(src, encoding="utf-8").read(400)
m = re.search(r'width="(\d+)" height="(\d+)"', head)
w, h = (int(m.group(1)), int(m.group(2))) if m else (2400, 3400)
subprocess.run([exe, "--headless", "--disable-gpu", "--hide-scrollbars",
                f"--window-size={w},{h + 90}", f"--screenshot={dst}", src.as_uri()],
               check=True, capture_output=True)
print(dst)
