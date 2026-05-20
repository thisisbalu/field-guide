# Tech Interview Field Guide

A self-contained study hub for software engineers targeting Senior, Staff, and Principal-level roles. Each topic includes concept overviews, quick-reference tables, level-tagged Q&A, and system design scenarios — all served as a static site with no backend.

**Live:** [balasubramanyamlanka.com/projects/field-guide](https://www.balasubramanyamlanka.com/projects/field-guide)

## Running locally

```bash
pip install -r requirements.txt

python generate.py              # regenerate all topics + index
python generate.py kafka        # regenerate one topic
python generate.py --index-only # rebuild index only
```

Open any `.html` file directly in a browser — no server needed.

## Adding a topic

1. Create `content/<id>.yaml` following the schema in an existing file
2. Run `python generate.py <id>`
3. Commit and push — GitHub Actions deploys automatically

## Stack

- **Content**: YAML (one file per topic)
- **Template**: Jinja2 (`templates/topic.html.j2`)
- **Generator**: Python 3.9+ (`generate.py`)
- **Styling**: IBM Plex Sans + IBM Plex Mono, per-topic accent colors, dark mode
- **Deploy**: GitHub Actions → GitHub Pages under `/projects/field-guide`
