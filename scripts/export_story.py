"""Export the story notebooks to docs/story/ with the code hidden, and add the page's tabs to each.

Run from the repo folder after editing a story notebook:
    .venv/bin/python scripts/export_story.py
"""
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NOTEBOOKS = sorted((ROOT / "notebooks" / "story").glob("*.ipynb"))
OUT = ROOT / "docs" / "story"

# The same tabs as on the graph page (docs/index.html).
TABS = [("../index.html", "Graph"), ("1_data.html", "1 · Data"), ("2_similarity.html", "2 · Similarity"),
        ("3_themes.html", "3 · Themes"), ("4_types.html", "4 · Types"), ("5_search.html", "5 · Search")]

STYLE = """<style>
  .story-nav { display: flex; flex-wrap: wrap; align-items: center; gap: 8px 16px; padding: 12px 16px;
    border-bottom: 1px solid #e4e3df; background: #fcfcfb; font: 14px/1.5 system-ui, -apple-system, "Segoe UI", sans-serif; }
  .story-nav strong { font-size: 15px; color: #0b0b0b; }
  .story-nav nav { display: flex; flex-wrap: wrap; gap: 2px; margin-left: auto; }
  .story-nav a { color: #52514e; text-decoration: none; font-size: 13px; padding: 5px 10px; border-radius: 8px; }
  .story-nav a:hover { color: #0b0b0b; background: #f3f2ef; }
  .story-nav a[aria-current="page"] { color: #0b0b0b; background: #f3f2ef; font-weight: 600; }
</style>"""


def nav(current):
    links = "".join(f'<a href="{href}"{" aria-current=\"page\"" if href == current else ""}>{label}</a>'
                    for href, label in TABS)
    return (f'<div class="story-nav"><strong>The Hundred Years\' War on Wikipedia</strong>'
            f'<nav aria-label="Pages">{links}</nav></div>')


subprocess.run([sys.executable, "-m", "jupyter", "nbconvert", "--to", "html", "--no-input",
                "--output-dir", str(OUT), *map(str, NOTEBOOKS)], check=True)

for notebook in NOTEBOOKS:
    page = OUT / f"{notebook.stem}.html"
    html = page.read_text(encoding="utf-8")
    label = dict(TABS)[page.name]
    html = re.sub(r"<title>.*?</title>", f"<title>{label} · Hundred Years' War</title>", html, count=1, flags=re.S)
    html = html.replace("</head>", STYLE + "\n</head>", 1)
    html = re.sub(r"(<body[^>]*>)", lambda m: m.group(1) + "\n" + nav(page.name), html, count=1)
    page.write_text(html, encoding="utf-8")
    print(f"added tabs to {page.relative_to(ROOT)}")
