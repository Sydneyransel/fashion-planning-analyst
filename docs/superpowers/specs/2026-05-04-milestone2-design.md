# Milestone 02 Design Spec

**Date:** 2026-05-04  
**Due:** 2026-05-04 (today)  
**Goal:** Complete all Milestone 2 deliverables: dbt verified, Streamlit dashboard deployed, GitHub Actions for both sources, pipeline diagram updated, knowledge base wiki pages, README rewrite, ERD, python-pptx slides script.

---

## Confirmed State Going In

- ✅ dbt models materialized in Snowflake (`SKIMS_ANALYTICS.MART.dim_category`, `dim_date`, `fact_weekly_interest`)
- ✅ Source 1 GitHub Actions (`extract_trends.yml`) — manual trigger works; scheduled run fails due to Google rate-limiting GitHub IPs (manual trigger satisfies rubric)
- ✅ `knowledge/raw/` — 15 files from skims.com, vogue.com, wwd.com, forbes.com, whowhatwear.com, harpersbazaar.com
- ❌ `knowledge/wiki/` — empty
- ❌ `dashboard/` — empty
- ❌ Source 2 GitHub Actions
- ❌ README not updated to template
- ❌ ERD not generated
- ❌ Slides not created

---

## Deliverable 8: GitHub Actions — Source 2

**File:** `.github/workflows/extract_skims.yml`

- Runs `pipeline/extract_skims.py` on the same Monday schedule (`0 6 * * 1`) with `workflow_dispatch`
- Secrets needed: all Snowflake vars + `FIRECRAWL_API_KEY`
- After scraping, commits and pushes any new/changed files in `knowledge/raw/` back to the repo using `GITHUB_TOKEN` with write permissions
- Uses `actions/checkout@v6` with `token: ${{ secrets.GITHUB_TOKEN }}` and `persist-credentials: true`

---

## Deliverable 11: Knowledge Base Wiki

**Files:**
- `knowledge/wiki/index.md`
- `knowledge/wiki/overview.md`
- `knowledge/wiki/product-categories.md`
- `knowledge/wiki/demand-themes.md`

**`index.md`:** Lists all wiki pages with one-line summaries and links to each.

**`overview.md`:** SKIMS brand story synthesized across all 15 sources — founding (2019), Kim Kardashian's role, $4B+ valuation, body-inclusivity positioning, retail expansion, NBA partnership, product scope.

**`product-categories.md`:** Per-category breakdown for shapewear, bodysuits, bras, underwear, swim, loungewear, dresses — what each collection offers, price positioning, how SKIMS describes it, and what press says about it.

**`demand-themes.md`:** Synthesis page connecting demand drivers: seasonality (swim in summer, loungewear/shapewear in Q4), celebrity/press effect, body-positivity as competitive moat, DTC-to-retail expansion impact on awareness.

**`CLAUDE.md` addition:** "How to Query the Knowledge Base" section with conventions (read index.md first, then relevant wiki page, fall back to raw sources, cite sources).

---

## Deliverable 7: Streamlit Dashboard

**Files:**
- `dashboard/app.py`
- `.streamlit/config.toml`
- `requirements.txt` updated with `streamlit`, `plotly`

**Theme (`config.toml`):**
```toml
[theme]
primaryColor = "#000000"
backgroundColor = "#FAFAF8"
secondaryBackgroundColor = "#F0EAE2"
textColor = "#1A1A1A"
font = "sans serif"
```

**Layout:** Two-tab app with sidebar.

**Sidebar:** Category group multiselect (intimates / lounge / swim / brand / ready-to-wear), date range slider.

**Tab 1 — Descriptive ("What happened?"):**
- KPI row: most recent week avg interest (latest in dataset), 52-week high, top keyword
- Line chart: weekly interest over time per keyword, filtered by sidebar selection
- Chart colors: SKIMS nude palette (`#D4B896`, `#C4A882`, `#B49270`, `#8B6F5E`, `#6B5044`) with black for "skims" keyword

**Tab 2 — Diagnostic ("Why did it happen?"):**
- Bar chart: average interest by season per category group (Winter/Spring/Summer/Fall)
- Year-over-year line chart: current year vs prior year for selected category group
- Chart style: same nude palette, minimal gridlines, clean axis labels

**Snowflake connection:** `snowflake-connector-python`, reads from `SKIMS_ANALYTICS.MART`. Credentials from `st.secrets` in deployment, `.env` locally. Connection cached with `@st.cache_resource`.

**Deployment:** Streamlit Community Cloud connected to `Sydneyransel/fashion-planning-analyst`, main branch, `dashboard/app.py` as entry point. Secrets added via Streamlit Cloud UI.

---

## Deliverable 9: Pipeline Diagram (Updated)

**Location:** `README.md` (Mermaid block)

Updated to show the accurate two-path architecture — no placeholders, Source 2 correctly flows to `knowledge/raw/` not Snowflake, every tool labeled:

```
Structured path: Google Trends (pytrends) → GitHub Actions → Snowflake RAW → dbt Staging → dbt Mart → Streamlit Dashboard
Knowledge path:  SKIMS.com + Press (Firecrawl) → GitHub Actions → knowledge/raw/ → Claude Code → knowledge/wiki/
```

---

## Deliverable 12: README Rewrite

**File:** `README.md` — fully rewritten to match `readme-template.md`.

Sections:
1. Project overview paragraph
2. Job posting (role, company, link, 1-2 sentence skills connection)
3. Tech stack table (Source 1: Google Trends/pytrends, Source 2: Firecrawl web scrape)
4. Pipeline diagram (updated Mermaid)
5. ERD (Mermaid `erDiagram` block)
6. Dashboard preview (placeholder note)
7. Key insights (descriptive + diagnostic + recommendation)
8. Live dashboard URL (filled after deploy)
9. Knowledge base section with 3 example query questions
10. Setup & reproduction steps
11. Repository structure tree

---

## Deliverable 13: ERD

**Location:** Embedded in `README.md` as Mermaid `erDiagram`.

```
fact_weekly_interest }o--|| dim_category : "category_key"
fact_weekly_interest }o--|| dim_date : "date_key"
```

All columns listed per table with types.

---

## Deliverable 10: Slides Script (Private)

**File:** `docs/generate_slides.py` — added to `.gitignore` along with `docs/*.pptx`

**Output:** `docs/skims-analytics-slides.pptx` (also gitignored)

**SKIMS brand palette:** background `#FAFAF8`, accent `#000000`, card fill `#F0EAE2`, chart series nudes `#D4B896` / `#C4A882` / `#8B6F5E`

**Five slides:**
1. Title — "SKIMS Product Performance Analytics", your name, date
2. Descriptive insight — takeaway title + line chart image (matplotlib) + callout box
3. Diagnostic insight — takeaway title + seasonal bar chart + callout box
4. Recommendation — [Action] → [Expected outcome] format
5. Data & methodology note

User exports to PDF via PowerPoint: File → Export → Create PDF/XPS.

---

## Build Order

1. GitHub Actions Source 2
2. Knowledge base wiki pages + CLAUDE.md update
3. Streamlit dashboard + `.streamlit/config.toml`
4. README rewrite + ERD + pipeline diagram
5. `docs/generate_slides.py` (gitignored)
6. Final commit history cleanup
