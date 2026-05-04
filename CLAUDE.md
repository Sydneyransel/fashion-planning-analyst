# CLAUDE.md — SKIMS Product Performance Analytics

## Project Overview

This is a portfolio analytics engineering project built to demonstrate skills relevant to a Planning Analyst role at SKIMS. It tracks product category demand trends using Google Trends data, transforms it through a dbt star schema in Snowflake, and surfaces insights in a deployed Streamlit dashboard.

**Job target:** Planning Analyst, SKIMS (Los Angeles HQ)
**Core focus:** Product performance — which SKIMS categories drive demand, when, and where.

## Tech Stack

| Layer | Tool |
|---|---|
| Data Source 1 | Google Trends via `pytrends` (Python) |
| Data Source 2 | Web scrape (SKIMS.com + fashion press) |
| Orchestration | GitHub Actions (scheduled) |
| Data Warehouse | Snowflake (raw → staging → mart) |
| Transformation | dbt |
| Dashboard | Streamlit (deployed to Streamlit Community Cloud) |
| Knowledge Base | Claude Code (scrape → wiki) |
| Version Control | Git + GitHub (public repo) |

## Directory Structure

```
fashion-planning-analyst/
├── docs/                  # Job posting, proposal, resume
├── pipeline/              # Python extraction scripts
│   └── extract_trends.py  # pytrends → Snowflake raw
├── dbt/                   # dbt project (staging + mart models)
├── dashboard/             # Streamlit app
├── knowledge/
│   ├── raw/               # Scraped sources (15+ files)
│   └── wiki/              # Claude Code-generated wiki pages
│       ├── index.md
│       ├── overview.md
│       ├── product-categories.md
│       └── demand-themes.md
├── .github/workflows/     # GitHub Actions pipelines
├── .gitignore
└── CLAUDE.md
```

## Data Sources

**Source 1 — API (Google Trends via pytrends):**
- Weekly interest scores (0–100) for SKIMS product categories
- Categories: shapewear, bodysuit, loungewear, swim, bra, dress, skims nipple covers, etc.
- Geography: United States (nationwide + top metros)
- Lookback: 5 years
- Scheduled weekly via GitHub Actions

**Source 2 — Web Scrape:**
- SKIMS.com (product pages, press releases, about)
- Fashion press: Vogue, WWD, Business of Fashion
- Reddit r/SKIMS
- Scraped using Firecrawl or similar; stored in `knowledge/raw/`

## Star Schema

**Fact table:** `SKIMS_ANALYTICS.MART.fact_weekly_interest`
- `interest_key` (PK), `category_key` (FK), `date_key` (FK)
- `interest_score` (0–100), `loaded_at`

**Dimensions:**
- `SKIMS_ANALYTICS.MART.dim_category` — keyword, category_group (intimates / lounge / swim / brand / ready-to-wear)
- `SKIMS_ANALYTICS.MART.dim_date` — week_start, month, quarter, year, season

## Business Questions

- Which SKIMS product categories have the highest demand right now?
- Which categories are growing or declining over time?
- What seasonal patterns exist across product groups?
- How does interest in the "skims" brand term compare to individual category keywords?

## Credentials & Security

- All credentials (Snowflake, API keys) stored as environment variables
- Never committed to the repo
- Use `.env` locally; GitHub Actions Secrets for CI/CD

## Knowledge Base

The `knowledge/` folder contains raw scraped sources and Claude Code-generated wiki pages about SKIMS, its product strategy, brand positioning, and the fashion/retail planning industry.

### How to Query the Knowledge Base

When answering questions about this project's domain, follow these conventions:
1. Read `knowledge/index.md` first to find the relevant wiki page(s)
2. Read the relevant wiki page(s) for synthesized insights
3. If more detail is needed, read the supporting raw sources listed in the wiki page
4. Cite which wiki page or raw source your answer draws from
5. If a question can't be answered from the knowledge base, say so clearly rather than guessing
