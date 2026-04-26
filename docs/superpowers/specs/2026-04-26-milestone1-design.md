# Milestone 01 Design — SKIMS Planning Analyst

**Date:** 2026-04-26
**Due:** 2026-04-27 at 9:55 AM
**Deliverables:** Source 1 extraction, dbt star schema, GitHub Actions pipeline, pipeline diagram

---

## Scope

Four graded deliverables:

1. `extract_trends.py` — Google Trends via pytrends → Snowflake raw (10 pts)
2. dbt project — staging + mart star schema with tests (15 pts)
3. GitHub Actions pipeline — scheduled, Source 1 automated (5 pts)
4. Pipeline diagram in README.md (5 pts)

Source 2 (Firecrawl/SKIMS scrape) is Milestone 02, due May 4.

---

## Directory Structure

```
fashion-planning-analyst/
├── pipeline/
│   ├── utils/
│   │   └── snowflake_utils.py
│   └── extract_trends.py
├── dbt/
│   ├── dbt_project.yml
│   ├── profiles.yml
│   └── models/
│       ├── staging/
│       │   ├── schema.yml
│       │   └── stg_google_trends.sql
│       └── mart/
│           ├── schema.yml
│           ├── dim_category.sql
│           ├── dim_date.sql
│           └── fact_weekly_interest.sql
├── .github/
│   └── workflows/
│       └── extract_trends.yml
├── README.md
├── requirements.txt
└── .env  (gitignored)
```

---

## Source 1: Google Trends Extraction

**Script:** `pipeline/extract_trends.py`

**Keywords (9 total, split into 2 pytrends batches):**
- Batch 1: shapewear, bodysuit, bra, underwear, dress
- Batch 2: skims, loungewear, pajamas, swim

**Parameters:**
- Timeframe: `today 5-y` (5-year weekly lookback)
- Geography: `US`
- Short sleep between batches to avoid pytrends rate limiting

**Snowflake target:** `SKIMS_ANALYTICS.RAW.GOOGLE_TRENDS_WEEKLY`

| Column | Type | Notes |
|---|---|---|
| keyword | VARCHAR | e.g. "shapewear" |
| week_start | DATE | Monday of each week |
| interest_score | INTEGER | 0–100 pytrends scale |
| loaded_at | TIMESTAMP_NTZ | UTC load time |

**Load pattern:** Truncate-and-reload (simple, idempotent for milestone 1)

---

## Snowflake Setup

- **Database:** `SKIMS_ANALYTICS`
- **Schema:** `RAW`
- **Warehouse:** `COMPUTE_WH`
- **Account:** `NBFBALO-FIC47143`
- All created by `snowflake_utils.py` on first run if they don't exist

**Credentials (env vars only, never committed):**
- `SNOWFLAKE_ACCOUNT`
- `SNOWFLAKE_USER`
- `SNOWFLAKE_PASSWORD`
- `SNOWFLAKE_DATABASE`
- `SNOWFLAKE_SCHEMA`
- `SNOWFLAKE_WAREHOUSE`

---

## dbt Star Schema

**Staging model:** `stg_google_trends.sql`
- Source: `RAW.GOOGLE_TRENDS_WEEKLY`
- Casts types, renames columns, adds `surrogate_key`

**Dimension: `dim_category`**
| Column | Type |
|---|---|
| category_key | VARCHAR (surrogate) |
| keyword | VARCHAR |
| category_group | VARCHAR | (e.g. intimates, ready-to-wear, swim — manually mapped) |

**Dimension: `dim_date`**
| Column | Type |
|---|---|
| date_key | VARCHAR (surrogate) |
| week_start | DATE |
| month | INTEGER |
| quarter | INTEGER |
| year | INTEGER |
| season | VARCHAR |

**Fact: `fact_weekly_interest`**
| Column | Type |
|---|---|
| interest_key | VARCHAR (surrogate) |
| category_key | VARCHAR (FK → dim_category) |
| date_key | VARCHAR (FK → dim_date) |
| interest_score | INTEGER |
| loaded_at | TIMESTAMP_NTZ |

**Tests (schema.yml):**
- `not_null` on `interest_score`, `keyword`, `week_start`
- `unique` on `fact_weekly_interest.interest_key`
- `accepted_range` on `interest_score` (0–100)

---

## GitHub Actions Pipeline

**File:** `.github/workflows/extract_trends.yml`

**Trigger:** Weekly schedule (`cron: '0 6 * * 1'` — every Monday 6 AM UTC) + manual `workflow_dispatch`

**Steps:**
1. Checkout repo
2. Set up Python 3.11
3. Install `requirements.txt`
4. Run `python pipeline/extract_trends.py`
5. Run `dbt run` and `dbt test` in `dbt/` directory

**Secrets (GitHub repo settings):**
- `SNOWFLAKE_ACCOUNT`, `SNOWFLAKE_USER`, `SNOWFLAKE_PASSWORD`
- `SNOWFLAKE_DATABASE`, `SNOWFLAKE_SCHEMA`, `SNOWFLAKE_WAREHOUSE`

---

## Pipeline Diagram (README.md)

Mermaid flowchart showing:

```
Google Trends API → GitHub Actions → Snowflake Raw → dbt Staging → dbt Mart → Streamlit (future)
```

---

## Dependencies (requirements.txt)

- `pytrends`
- `snowflake-connector-python`
- `pandas`
- `dbt-snowflake`
- `python-dotenv`
