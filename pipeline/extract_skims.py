import os
import re
import time
from datetime import datetime, timezone
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.environ["FIRECRAWL_API_KEY"]
HEADERS = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
RAW_DIR = Path(__file__).parent.parent / "knowledge" / "raw"

SKIMS_PAGES = [
    ("https://skims.com/pages/about", "skims.com"),
    ("https://skims.com/collections/shapewear", "skims.com"),
    ("https://skims.com/collections/bras", "skims.com"),
    ("https://skims.com/collections/bodysuits", "skims.com"),
    ("https://skims.com/collections/swim", "skims.com"),
    ("https://skims.com/collections/loungewear", "skims.com"),
    ("https://skims.com/collections/dresses", "skims.com"),
    ("https://skims.com/collections/underwear", "skims.com"),
]

PRESS_SEARCHES = [
    ("SKIMS Kim Kardashian brand shapewear", "vogue.com", "vogue.com"),
    ("SKIMS collection launch growth", "vogue.com", "vogue.com"),
    ("SKIMS valuation funding round", "wwd.com", "wwd.com"),
    ("SKIMS store expansion retail", "wwd.com", "wwd.com"),
    ("SKIMS Kim Kardashian billion dollar brand", "forbes.com", "forbes.com"),
    ("SKIMS shapewear brand review", "harpersbazaar.com", "harpersbazaar.com"),
    ("SKIMS", "reddit.com/r/skims", "reddit"),
]


def slugify(url: str) -> str:
    slug = re.sub(r"https?://", "", url)
    slug = re.sub(r"[^\w]+", "-", slug).strip("-")
    return slug[:80]


def scrape_url(url: str) -> dict:
    resp = requests.post(
        "https://api.firecrawl.dev/v1/scrape",
        headers=HEADERS,
        json={"url": url, "formats": ["markdown"]},
        timeout=30,
    )
    resp.raise_for_status()
    data = resp.json()
    if not data.get("success"):
        raise ValueError(f"Firecrawl returned success=false for {url}")
    page = data["data"]
    return {
        "url": url,
        "title": page.get("metadata", {}).get("title", ""),
        "markdown": page.get("markdown", ""),
    }


def search_and_scrape(query: str, site: str, source_type: str) -> dict | None:
    resp = requests.post(
        "https://api.firecrawl.dev/v1/search",
        headers=HEADERS,
        json={"query": f"site:{site} {query}", "limit": 1},
        timeout=30,
    )
    resp.raise_for_status()
    data = resp.json()
    results = data.get("data", [])
    if not results:
        print(f"  No results for: {query} on {site}")
        return None
    top = results[0]
    url = top.get("url", "")
    return {
        "url": url,
        "title": top.get("metadata", {}).get("title", top.get("title", "")),
        "markdown": top.get("markdown", ""),
        "source_type": source_type,
    }


def save(result: dict, source_type: str):
    slug = slugify(result["url"])
    path = RAW_DIR / f"{slug}.md"
    scraped_at = datetime.now(timezone.utc).isoformat()
    content = (
        f"---\n"
        f"url: {result['url']}\n"
        f"source_type: {source_type}\n"
        f"title: {result['title']}\n"
        f"scraped_at: {scraped_at}\n"
        f"---\n\n"
        f"{result['markdown']}"
    )
    path.write_text(content, encoding="utf-8")
    print(f"  Saved: {path.name}")


def main():
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    saved = 0

    print("=== Scraping SKIMS.com pages ===")
    for url, source_type in SKIMS_PAGES:
        print(f"Scraping: {url}")
        try:
            result = scrape_url(url)
            save(result, source_type)
            saved += 1
        except Exception as e:
            print(f"  ERROR: {e}")
        time.sleep(1)

    print("\n=== Searching press sources ===")
    for query, site, source_type in PRESS_SEARCHES:
        print(f"Searching {site}: {query}")
        try:
            result = search_and_scrape(query, site, source_type)
            if result:
                save(result, source_type)
                saved += 1
        except Exception as e:
            print(f"  ERROR: {e}")
        time.sleep(1)

    print(f"\nDone. Saved {saved} files to {RAW_DIR}")


if __name__ == "__main__":
    main()
