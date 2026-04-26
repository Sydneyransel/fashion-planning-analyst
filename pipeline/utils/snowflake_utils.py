import os
import snowflake.connector
from dotenv import load_dotenv

load_dotenv()


def setup_snowflake():
    """Creates database, schema, and warehouse on first run."""
    conn = snowflake.connector.connect(
        account=os.environ["SNOWFLAKE_ACCOUNT"],
        user=os.environ["SNOWFLAKE_USER"],
        password=os.environ["SNOWFLAKE_PASSWORD"],
    )
    cur = conn.cursor()
    db = os.environ["SNOWFLAKE_DATABASE"]
    schema = os.environ["SNOWFLAKE_SCHEMA"]
    wh = os.environ["SNOWFLAKE_WAREHOUSE"]
    cur.execute(f"CREATE DATABASE IF NOT EXISTS {db}")
    cur.execute(f"CREATE SCHEMA IF NOT EXISTS {db}.{schema}")
    cur.execute(f"CREATE SCHEMA IF NOT EXISTS {db}.MART")
    cur.execute(
        f"CREATE WAREHOUSE IF NOT EXISTS {wh} "
        f"WAREHOUSE_SIZE='X-SMALL' AUTO_SUSPEND=60 AUTO_RESUME=TRUE"
    )
    cur.close()
    conn.close()


def get_connection():
    return snowflake.connector.connect(
        account=os.environ["SNOWFLAKE_ACCOUNT"],
        user=os.environ["SNOWFLAKE_USER"],
        password=os.environ["SNOWFLAKE_PASSWORD"],
        database=os.environ["SNOWFLAKE_DATABASE"],
        schema=os.environ["SNOWFLAKE_SCHEMA"],
        warehouse=os.environ["SNOWFLAKE_WAREHOUSE"],
    )
