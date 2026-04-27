import os
import sys
import time
from datetime import datetime, timezone

import pandas as pd
from dotenv import load_dotenv
from pytrends.request import TrendReq

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from pipeline.utils.snowflake_utils import get_connection, setup_snowflake

load_dotenv()

KEYWORD_BATCHES = [
    ["shapewear", "bodysuit", "bra", "underwear", "dress"],
    ["skims", "loungewear", "pajamas", "swim"],
]


def fetch_batch(keywords: list) -> pd.DataFrame:
    pytrends = TrendReq(hl="en-US", tz=360)
    pytrends.build_payload(keywords, timeframe="today 5-y", geo="US")
    df = pytrends.interest_over_time()
    if df.empty:
        return pd.DataFrame()
    df = df.drop(columns=["isPartial"], errors="ignore")
    df = df.reset_index()
    df = df.melt(id_vars=["date"], var_name="keyword", value_name="interest_score")
    df = df.rename(columns={"date": "week_start"})
    df["week_start"] = df["week_start"].dt.date
    df["interest_score"] = df["interest_score"].astype(int)
    return df


def load_to_snowflake(conn, df: pd.DataFrame, table: str) -> int:
    loaded_at = datetime.now(timezone.utc)
    rows = [
        (row["keyword"], str(row["week_start"]), int(row["interest_score"]), loaded_at)
        for _, row in df.iterrows()
    ]
    cur = conn.cursor()
    cur.executemany(
        f"INSERT INTO {table} (keyword, week_start, interest_score, loaded_at) "
        "VALUES (%s, %s, %s, %s)",
        rows,
    )
    cur.close()
    return len(rows)


def main():
    db = os.environ["SNOWFLAKE_DATABASE"]
    schema = os.environ["SNOWFLAKE_SCHEMA"]
    table = f"{db}.{schema}.GOOGLE_TRENDS_WEEKLY"

    print("Setting up Snowflake infrastructure...")
    setup_snowflake()

    conn = get_connection()
    cur = conn.cursor()
    cur.execute(f"USE DATABASE {db}")
    cur.execute(f"USE SCHEMA {db}.{schema}")
    cur.execute(f"""
        CREATE TABLE IF NOT EXISTS {table} (
            keyword        VARCHAR,
            week_start     DATE,
            interest_score INTEGER,
            loaded_at      TIMESTAMP_NTZ
        )
    """)
    cur.execute(f"TRUNCATE TABLE IF EXISTS {table}")
    cur.close()

    all_frames = []
    for batch in KEYWORD_BATCHES:
        print(f"Fetching: {batch}")
        df = fetch_batch(batch)
        if not df.empty:
            all_frames.append(df)
        time.sleep(5)  # avoid pytrends rate limit

    if not all_frames:
        print("ERROR: No data returned from pytrends.")
        sys.exit(1)

    combined = pd.concat(all_frames, ignore_index=True)
    print(f"Loading {len(combined)} rows to Snowflake...")
    nrows = load_to_snowflake(conn, combined, table)
    conn.close()
    print(f"Done. Loaded {nrows} rows.")


if __name__ == "__main__":
    main()
