# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Purpose

A data-driven interview preparation hub for software engineers targeting Senior, Staff, and Principal-level roles. The goal is a single place to study key technologies in depth — concept overviews, quick-reference tables, level-tagged Q&A, and system design scenarios. Content is fully generic (no company-specific references) so it applies to any interview.

The hub is served as a static site: `index.html` is the landing page listing all topics; each topic is a self-contained HTML file (`kafka.html`, `kubernetes.html`, etc.) that works offline with no server.

## Architecture

```
content/        ← one YAML file per technology (source of truth)
templates/      ← topic.html.j2 (Jinja2 template)
shared/         ← style.css + script.js (inlined into every output file)
generate.py     ← reads content/*.yaml → renders template → writes HTML
site/           ← generated output (committed); index.html + all topic pages
```

Generated HTML files live in `site/` and are committed alongside the source YAMLs. The deploy workflow re-runs the generator then publishes `site/` directly to GitHub Pages — CSS and JS are inlined so no separate assets are needed.

**Adding a new topic = write one YAML file + run `python generate.py`.**

## Generator

```bash
python generate.py                  # regenerate all topics + index
python generate.py kafka            # regenerate one topic + index
python generate.py --index-only     # rebuild index.html only
```

Uses Python 3.9+ (`/usr/bin/python3` on macOS). Dependencies in `requirements.txt`:
```
jinja2>=3.1
pyyaml>=6.0
markdown>=3.5
```

Install once: `/usr/bin/pip3 install -r requirements.txt`

## YAML content schema

Every topic follows this base structure. Additional sections or fields can be added per topic as needed — the template renders only what's present.

```yaml
meta:
  id: kafka               # used as output filename: kafka.html
  title: Apache Kafka     # displayed as <h1>
  title_short: Kafka      # used in "Use X When" / "Don't Use X When" headings
  badge: "Interview Prep · Distributed Systems"  # small pill shown on the topic header
  subtitle: "// ..."      # monospace tagline under the title
  description: "..."      # shown on the index card below the title (1 sentence)
  category: Backend       # groups the card on the index page
  icon: "📨"              # emoji shown on the index card

colors:
  toggle_light: "#hex"    # accent color for light mode toggle knob + index card stripe
  toggle_dark:  "#hex"
  light_vars: >-          # raw CSS variable block injected into [data-theme="light"]
    --h1-from:#...; --h1-to:#...; --accent:#...; ...
  dark_vars: >-           # same for [data-theme="dark"]

overview:
  concepts:               # shown 3 per row
    - title: "..."
      body: "..."         # markdown
      tags:
        - {text: "label", color: green}   # color: green|orange|red|purple (optional)
      flows:              # array of step-arrays; each inner array renders as a → chain
        - ["Step A", "Step B", "Step C"]
  gotchas:                # warning-styled list
    - title: "..."
      body: "..."         # markdown
  when_to_use: []         # plain text strings
  when_not_to_use: []

deep_dive:
  tables:                 # key/value reference tables
    - title: "..."
      full_width: true    # optional — spans both columns instead of half-width
      rows:
        - {key: "setting-name", value: "description"}
  cli:                    # grouped CLI commands (optional)
    - group: "Group Name"
      commands:
        - {cmd: "...", desc: "..."}
  comparison:             # full-width multi-column table (optional)
    title: "..."
    headers: ["Col1", "Col2", "Col3"]
    rows:
      - ["row1col1", "row1col2", "row1col3"]

qa:
  senior: []              # questions with id (S-01), question, answer (markdown), staff_add (markdown)
  staff:  []              # same format, id prefix ST- (optional)
  principal: []           # same format, id prefix P- (optional)

scenarios:                # each with title, problem, constraints[], discussion[] (markdown), red_flags[] (markdown)
```

### Markdown fields

The Jinja2 template applies a `| md` filter to render Markdown → HTML. Fields that support Markdown: `concepts[].body`, `gotchas[].body`, `qa.*.answer`, `qa.*.staff_add`, `scenarios[].problem`, `scenarios[].discussion[]`, `scenarios[].red_flags[]`. All other fields are plain text.

### Q&A progress tracking

Q&A reviewed state is stored in `localStorage` keyed as `reviewed:{topicId}:{questionId}`. The `<body>` carries `data-topic-id="{{ meta.id }}"`. On load, `initReviewedState()` in `script.js` restores the reviewed state. The progress bar and label update via `updateQAProgress()`. Tab URL fragment sync uses `history.replaceState` with the tab name as the hash.

### Optional template sections

`deep_dive.cli`, `deep_dive.comparison`, `qa.senior`, `qa.staff`, and `qa.principal` are guarded by `{% if %}` in the template and can be omitted from the YAML with no errors.

## Template structure (4 tabs)

| Tab | Content |
|---|---|
| Overview | Concept cards (3/row) · Gotchas · When to use / not use |
| Deep Dive | Config tables · CLI commands · Comparison table |
| Q & A | Accordion Q&A grouped by Senior / Staff / Principal; each answer optionally has a "What a Staff+ adds on top" box |
| Scenarios | System design scenarios: Problem → Constraints → Discussion → Red flags |

## Shared CSS components

| Class | Purpose |
|---|---|
| `.concept-card` | Cards in a 3-column grid; left accent border, hover shadow |
| `.accordion` / `.acc-item` / `.acc-body` | Collapsible Q&A; JS scrollHeight animation (`setAccOpen` in script.js) |
| `.level-badge` `.level-senior/staff/principal` | Colored level tags on Q&A items |
| `.staff-add` | "What a Staff+ adds on top" box after answers |
| `.gotcha` / `.gotcha-list` | Warning-styled gotcha entries |
| `.when-grid` / `.when-use` / `.when-not` | Two-column use/don't-use grid |
| `.cheat-grid` / `.cheat-block` | Reference table layout |
| `.comparison-wrap` / `.comparison-table` | Scrollable full-width comparison table |
| `.scenario` / `.scenario-body` | Scenario cards with 2-column grid layout |
| `.flow` / `.flow-step` / `.flow-arrow` | Horizontal step-flow diagrams |
| `.tag` | Inline chips; variants: `.green`, `.orange`, `.red`, `.purple` |
| `.section-title` / `.section-sub` | Section headings — both prefixed with `//` via CSS `::before` |
| `.back-link` | Top-left "← Field Guide" link on topic pages; `span` hidden on mobile |
| `.qa-progress` / `.qa-progress-track` / `.qa-progress-fill` / `.qa-progress-label` | Progress bar tracking reviewed Q&As (persisted in localStorage) |
| `.qa-controls` / `.qa-search` / `.expand-all-btn` | Search input + expand/collapse all button above Q&A accordion |
| `.acc-footer` / `.mark-reviewed-btn` | Footer inside each accordion body with "Mark reviewed" button |
| `.acc-item.reviewed` | Applies strikethrough + muted style to reviewed Q&A items |

## Theming

Each topic has its own accent color palette defined in the YAML `colors` block as raw CSS variable strings (`light_vars`, `dark_vars`). These are injected directly into `[data-theme="light"]` and `[data-theme="dark"]` blocks in the template. Shared neutral variables (bg, surface, text, green, yellow, red, etc.) live in `shared/style.css` and are the same across all topics.

Fonts: **IBM Plex Sans** (body) + **IBM Plex Mono** (labels, code, monospace elements), loaded from Google Fonts.

## Index page categories

Topics are grouped by category on the index page. Current order: `Backend · Infrastructure · Security · Observability · Data · Quality · DevOps`

The order is controlled by `CATEGORY_ORDER` in `generate.py:35`. When adding a YAML with a `category` value not already in that list, append it there — otherwise the category appears after all known ones.

## Deploy

Push to `main` triggers GitHub Actions (`.github/workflows/deploy.yml`), which regenerates all HTML and deploys to `thisisbalu/thisisbalu.github.io` under `/projects/field-guide`.

Live URL: `https://www.balasubramanyamlanka.com/projects/field-guide`

## Topics

**Current (20):**

| Topic | Category |
|---|---|
| kafka | Backend |
| golang | Backend |
| distributed-systems | Backend |
| springboot | Backend |
| hibernate-jpa | Backend |
| rest-api | Backend |
| microservices | Backend |
| jvm-tuning | Backend |
| kubernetes | Infrastructure |
| ocp | Infrastructure |
| docker | Infrastructure |
| oauth2 | Security |
| jwt | Security |
| vault | Security |
| spring-security | Security |
| datadog | Observability |
| postgresql | Data |
| load-testing | Quality |
| maven-gradle | DevOps |
| jenkins-cicd | DevOps |

**Planned:** aws, helm, kibana, snowflake, sonarqube, trident, jfrog-nexus
