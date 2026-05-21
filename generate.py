#!/usr/bin/env python3
"""
Interview Field Guide Generator
Usage: python generate.py
       python generate.py kafka          # regenerate one topic
       python generate.py --index-only   # rebuild index.html only
"""
import sys
import yaml
import markdown as md_lib
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

BASE = Path(__file__).parent
CONTENT_DIR = BASE / "content"
TEMPLATE_DIR = BASE / "templates"
SHARED_DIR = BASE / "shared"


# ── Markdown filter ────────────────────────────────────────────────────────
_md = md_lib.Markdown(extensions=["fenced_code", "tables"])

def to_html(text):
    if not text:
        return ""
    _md.reset()
    html = _md.convert(str(text))
    # Strip wrapping <p> tags from single-paragraph text so inline use looks clean
    if html.startswith("<p>") and html.endswith("</p>") and html.count("<p>") == 1:
        html = html[3:-4]
    return html


# ── Index page builder ─────────────────────────────────────────────────────
CATEGORY_ORDER = ["Backend", "Infrastructure", "Security", "Observability", "Data", "Quality", "DevOps"]

def build_index(topics: list[dict]) -> str:
    # Group by category
    groups: dict[str, list] = {}
    for t in topics:
        cat = t["meta"].get("category", "Other")
        groups.setdefault(cat, []).append(t)

    shared_css = (SHARED_DIR / "style.css").read_text()
    shared_js = (SHARED_DIR / "script.js").read_text()

    cards_html = ""
    for cat in CATEGORY_ORDER + [c for c in groups if c not in CATEGORY_ORDER]:
        if cat not in groups:
            continue
        cards_html += f'<div class="cat-label">{cat}</div><div class="card-row">'
        for t in groups[cat]:
            m = t["meta"]
            c = t["colors"]
            file_name = f"{m['id']}.html"
            desc = m.get('description', '')
            desc_html = f'\n  <div class="card-desc">{desc}</div>' if desc else ''
            cards_html += f"""
<a class="card" href="{file_name}" style="--card-accent:{c['toggle_light']}">
  <div class="card-icon">{m.get('icon','📄')}</div>
  <div class="card-name">{m['title']}</div>{desc_html}
  <div class="card-badge">{cat}</div>
</a>"""
        cards_html += "</div>"

    return f"""<!DOCTYPE html>
<html lang="en" data-theme="light">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Tech Interview Field Guide</title>
<script>(function(){{var t=localStorage.getItem('theme');if(t)document.documentElement.setAttribute('data-theme',t);}})()</script>
<style>
  @import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;600;700&family=IBM+Plex+Sans:wght@400;600;700&display=swap');
  [data-theme="light"]{{--bg:#f0f4f8;--surface:#fff;--border:#c5d4e8;--text:#1a2235;--muted:#64748b;--badge-bg:#e2e8f0;}}
  [data-theme="dark"]{{--bg:#0a0e1a;--surface:#111827;--border:#1e3a5f;--text:#e2e8f0;--muted:#64748b;--badge-bg:#1a2235;}}
  [data-theme="light"] .toggle-knob{{background:#1a2235;transform:translateX(0);}}
  [data-theme="dark"] .toggle-knob{{background:#e2e8f0;transform:translateX(16px);}}
  {shared_css}
  /* Index-specific overrides */
  body{{max-width:1100px;margin:0 auto;}}
  .index-header{{text-align:center;padding:3rem 0 2rem;}}
  .index-header h1{{font-size:2.5rem;font-weight:800;background:linear-gradient(135deg,#1a6b3a,#0077aa);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;margin-bottom:.5rem;}}
  .index-header p{{color:var(--muted);font-family:'IBM Plex Mono',monospace;font-size:.83rem;}}
  .cat-label{{font-family:'IBM Plex Mono',monospace;font-size:.72rem;font-weight:600;text-transform:uppercase;letter-spacing:.12em;color:var(--muted);margin:2rem 0 .75rem;padding-bottom:.4rem;border-bottom:1px solid var(--border);}}
  .card-row{{display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:1rem;margin-bottom:.5rem;}}
  .card{{background:var(--surface);border:1px solid var(--border);border-top:3px solid var(--card-accent,#1a2235);border-radius:8px;padding:1.25rem;text-decoration:none;color:var(--text);transition:box-shadow .2s,transform .15s;display:flex;flex-direction:column;gap:.4rem;}}
  .card:hover{{box-shadow:0 6px 20px rgba(0,0,0,.1);transform:translateY(-2px);}}
  [data-theme="dark"] .card:hover{{box-shadow:0 6px 20px rgba(0,0,0,.35);}}
  .card-icon{{font-size:1.5rem;line-height:1;}}
  .card-name{{font-size:.95rem;font-weight:700;margin-top:.2rem;}}
  .card-badge{{display:inline-block;font-family:'IBM Plex Mono',monospace;font-size:.6rem;padding:.15rem .5rem;border-radius:2px;background:var(--badge-bg);color:var(--muted);text-transform:uppercase;letter-spacing:.1em;width:fit-content;}}
  .card-desc{{font-size:.72rem;color:var(--muted);line-height:1.45;margin-top:.1rem;}}
</style>
</head>
<body>
<div class="theme-toggle" onclick="toggleTheme()">
  <div class="toggle-track"><div class="toggle-knob"></div></div>
  <span id="toggle-label">DARK MODE</span>
</div>
<div class="index-header">
  <h1>Field Guide</h1>
  <p>// {len(topics)} topics · deep dives · Q&A by level · system design</p>
</div>
{cards_html}
<script>{shared_js}</script>
</body>
</html>"""


# ── Main ───────────────────────────────────────────────────────────────────
def main():
    args = sys.argv[1:]
    index_only = "--index-only" in args
    filter_id = next((a for a in args if not a.startswith("--")), None)

    shared_css = (SHARED_DIR / "style.css").read_text()
    shared_js = (SHARED_DIR / "script.js").read_text()

    env = Environment(loader=FileSystemLoader(str(TEMPLATE_DIR)), autoescape=False)
    env.filters["md"] = to_html
    template = env.get_template("topic.html.j2")

    yaml_files = sorted(CONTENT_DIR.glob("*.yaml"))
    if not yaml_files:
        print("No content files found in content/")
        return

    all_topics = []
    for yaml_file in yaml_files:
        data = yaml.safe_load(yaml_file.read_text(encoding="utf-8"))
        all_topics.append(data)

        topic_id = data["meta"]["id"]
        if index_only or (filter_id and filter_id != topic_id):
            continue

        html = template.render(**data, shared_css=shared_css, shared_js=shared_js)
        out = BASE / f"{topic_id}.html"
        out.write_text(html, encoding="utf-8")
        print(f"  ✓  {out.name}")

    # Always rebuild index
    index_html = build_index(all_topics)
    (BASE / "index.html").write_text(index_html, encoding="utf-8")
    print(f"  ✓  index.html  ({len(all_topics)} topics)")


if __name__ == "__main__":
    main()
