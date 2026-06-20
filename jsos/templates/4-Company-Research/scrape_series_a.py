"""
startups.gallery Series A Scraper
----------------------------------
Downloads the Framer site search-index JSON (which contains all page text)
and extracts every Series A company with full metadata.

Data sources (all from one public JSON endpoint — no HTML scraping):
  • /companies/<slug>  → name, description, location, industry, work_type,
                         company_size, funding_amount, series_a_date
  • /news              → lead_investor (best-effort, some entries missing)

Company detail pages require login, so founders / website URLs are left blank.

Run:
    pip install requests
    python scrape_series_a.py
"""

import csv
import json
import re
import subprocess
import sys
from dataclasses import asdict, dataclass, fields
from datetime import datetime
from typing import Optional

import requests

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
SEARCH_INDEX_URL = (
    "https://framerusercontent.com/sites/"
    "eQ8EfGgqmp8FpeXNnf1bo/searchIndex-3LpVJKKep0Xv.json"
)
BASE_URL = "https://startups.gallery"
OUTPUT_CSV = "startups_gallery_series_a.csv"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    )
}

# Regex helpers
RE_ROUND = re.compile(r"^\$[\d.,]+[KMB]?\s+", re.IGNORECASE)           # e.g. "$10M Series A"
RE_ROUND_DOT = re.compile(r"^\$[\d.,]+[KMB]?\s*·\s*", re.IGNORECASE)  # e.g. "$10M · Series A"
RE_DATE_FULL = re.compile(
    r"^(January|February|March|April|May|June|July|August|September|"
    r"October|November|December|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|"
    r"Oct|Nov|Dec)\s+\d{1,2},\s+\d{4}$",
    re.IGNORECASE,
)
RE_RAISED = re.compile(
    r"Raised\s+\$[\d.,]+[KMB]?\s+Series A\s+on\s+(.+)",
    re.IGNORECASE,
)
RE_AMOUNT_STAGE = re.compile(r"^\$([\d.,]+[KMB]?)\s+Series A$", re.IGNORECASE)
RE_LOCATION = re.compile(r"^[A-Za-z][A-Za-z\s\-'.]+,\s+[A-Za-z\s]+$")
RE_SIZE = re.compile(r"^\d+[\u2013\-]\d+$")  # e.g. "11–50"
WORK_TYPES = {"Remote", "Onsite", "Hybrid"}
SKIP_TOKENS = {
    "Join for free", "Backed by", "Visit Website", "View Jobs",
    "Work Type", "Stages", "Industries", "Investors", "Cities", "Countries",
    "Bootstrapped", "Pre-Seed", "Seed", "Series A", "Series B", "Series C",
    "Series D", "Series E", "Venture", "Explore", "Jobs", "News",
    "About · Sponsor · Submit ↗", "See all Industries", "See all Investors",
}

# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------
@dataclass
class CompanyRecord:
    company_name: str = ""
    stage: str = "Series A"
    series_a_date: str = ""       # ISO YYYY-MM-DD when available
    funding_amount: str = ""      # e.g. "$11M"
    lead_investor: str = ""
    description: str = ""
    industry: str = ""
    work_type: str = ""
    location: str = ""
    company_size: str = ""
    company_page_url: str = ""
    founders: str = ""            # not available without login

CSV_COLUMNS = [f.name for f in fields(CompanyRecord)]

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def normalize_date(raw: str) -> str:
    """Convert 'March 10, 2026' or 'Mar 10, 2026' to '2026-03-10'."""
    raw = raw.strip()
    for fmt in ("%B %d, %Y", "%b %d, %Y"):
        try:
            return datetime.strptime(raw, fmt).strftime("%Y-%m-%d")
        except ValueError:
            pass
    return raw


def is_date(s: str) -> bool:
    return bool(RE_DATE_FULL.match(s.strip()))


def is_round_dot(s: str) -> bool:
    return bool(RE_ROUND_DOT.match(s.strip()))


def slug_to_name(slug: str) -> str:
    return slug.replace("-", " ").title()

# ---------------------------------------------------------------------------
# Parse a company page from the search index
# ---------------------------------------------------------------------------
NOISE_P = {
    "Join for free", "Backed by", "Visit Website", "View Jobs",
    "Work Type", "Remote", "Onsite", "Hybrid",
    "Bootstrapped", "Pre-Seed", "Seed", "Series A", "Series B",
    "Series C", "Series D", "Series E", "Venture",
    "Explore", "Jobs", "News", "About · Sponsor · Submit ↗",
    "Crafted by Louis and Gonzalo",
    "See all Industries", "See all Investors",
}

def parse_company_page(slug: str, page: dict) -> Optional[CompanyRecord]:
    """
    Extract a CompanyRecord from a company page entry in the search index.
    Returns None if the company is not Series A.

    The p-array layout for every company page is predictable:
      [0]  "Join for free"
      [1]  "Backed by"
      [2]  "Visit Website"
      [3]  "View Jobs"
      [4]  "Raised $X Series A on [date]"  -- only for recently-funded
      OR
      [4]  description (when no Raised string)
      [5]  description (when Raised string is at [4])
      [6 or 5]  location  e.g. "New York, United States"
      [7 or 6]  "$X Series A"  (funding line)
      [8 or 7]  industry  e.g. "AI"
      [9 or 8]  work_type  e.g. "Remote"
      [10 or 9] company_size  e.g. "11–50"
      rest:  job postings + similar company cards (skip)
    """
    p_items = page.get("p", [])
    h1 = page.get("h1", [])

    company_name = h1[0].strip() if h1 else slug_to_name(slug)

    funding_amount = ""
    series_a_date = ""
    description = ""
    location = ""
    industry = ""
    work_type = ""
    company_size = ""
    is_series_a = False

    # Skip the fixed header noise items (variable length: 3 or 4)
    FIXED_HEADERS = {"Join for free", "Backed by", "Visit Website", "View Jobs"}
    start_idx = 0
    for item in p_items:
        if item.strip() in FIXED_HEADERS:
            start_idx += 1
        else:
            break
    items = [item.strip() for item in p_items[start_idx:] if item.strip()]
    if not items:
        return None

    idx = 0

    # Check if first item is a "Raised..." line
    if items[idx].startswith("Raised "):
        m_raised = RE_RAISED.match(items[idx])
        if m_raised:
            is_series_a = True
            series_a_date = normalize_date(m_raised.group(1).strip())
            amount_match = re.search(r"\$[\d.,]+[KMB]?", items[idx])
            if amount_match:
                funding_amount = amount_match.group(0)
        idx += 1

    # Description: the next item is the company description (long text)
    if idx < len(items) and len(items[idx]) > 20 and "·" not in items[idx]:
        description = items[idx]
        idx += 1

    # Location: "City, Country"
    if idx < len(items) and RE_LOCATION.match(items[idx]):
        location = items[idx]
        idx += 1

    # Funding line: "$X Series A" or "$X Seed" etc.
    if idx < len(items) and items[idx].startswith("$"):
        funding_line = items[idx]
        m_amt = RE_AMOUNT_STAGE.match(funding_line)
        if m_amt:
            is_series_a = True
            funding_amount = funding_amount or f"${m_amt.group(1)}"
        # Also check for other stages to confirm it's Series A
        elif "Series A" in funding_line:
            is_series_a = True
            amt_m = re.search(r"\$([\d.,]+[KMB]?)", funding_line)
            if amt_m:
                funding_amount = funding_amount or f"${amt_m.group(1)}"
        idx += 1

    # Industry (short word/phrase, no special chars)
    if (
        idx < len(items)
        and "·" not in items[idx]
        and "Posted on" not in items[idx]
        and not items[idx].startswith("$")
        and items[idx] not in WORK_TYPES
        and not RE_SIZE.match(items[idx])
        and len(items[idx].split()) <= 4
    ):
        industry = items[idx]
        idx += 1

    # Work type
    if idx < len(items) and items[idx] in WORK_TYPES:
        work_type = items[idx]
        idx += 1

    # Company size
    if idx < len(items) and RE_SIZE.match(items[idx]):
        company_size = items[idx]

    if not is_series_a:
        return None

    return CompanyRecord(
        company_name=company_name,
        stage="Series A",
        series_a_date=series_a_date,
        funding_amount=funding_amount,
        description=description,
        industry=industry,
        work_type=work_type,
        location=location,
        company_size=company_size,
        company_page_url=f"{BASE_URL}/companies/{slug}",
    )

# ---------------------------------------------------------------------------
# Parse news page → {company_name: lead_investor}
# ---------------------------------------------------------------------------
def parse_news_investors(news_page: dict, known_investors: set[str] = None) -> dict[str, str]:
    """
    Use the news p-array to build a best-effort map of
    company_name → lead_investor for Series A entries only.

    Strategy: find all round tokens ($X · Stage) in the p-array.
    For each round token at index i:
      - Name  = p[i-1]
      - Round = p[i]
      - Date  = p[i+1] if matches date pattern (optional, skip)
      - Investor = first non-date, non-skip token after round
    """
    p_items = news_page.get("p", [])
    investor_map: dict[str, str] = {}

    for i, item in enumerate(p_items):
        if not is_round_dot(item):
            continue

        # Stage must be "Series A"
        stage_part = item.split("·", 1)[-1].strip() if "·" in item else ""
        if stage_part.lower() != "series a":
            continue

        # Company name is the item before this round
        if i == 0:
            continue
        name = p_items[i - 1].strip()
        if not name or name in SKIP_TOKENS or is_round_dot(name) or is_date(name):
            continue

        # Find the investor after the round (skip optional date)
        investor = ""
        j = i + 1
        while j < len(p_items):
            candidate = p_items[j].strip()
            if is_date(candidate):
                j += 1
                continue
            if candidate in SKIP_TOKENS or candidate == "Source" or not candidate:
                break
            if is_round_dot(candidate):
                break
            # Validate against known investors whitelist to avoid picking up
            # the next company name as the investor
            if known_investors is not None:
                if candidate.lower() not in known_investors:
                    break  # not a known investor, skip
            investor = candidate
            break
        
        if name and investor:
            investor_map[name.lower()] = investor

    return investor_map

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    print("=== startups.gallery Series A Scraper ===\n")

    print("[1/4] Downloading Framer site search index...")
    resp = requests.get(SEARCH_INDEX_URL, headers=HEADERS, timeout=20)
    resp.raise_for_status()
    index_data: dict = resp.json()
    print(f"      Loaded {len(index_data)} page entries.\n")

    print("[2/4] Parsing news page for lead investor data...")
    # Build a whitelist of known investor names from the index
    known_investors: set[str] = set()
    for page_key, page in index_data.items():
        if page_key.startswith("/investors/"):
            h1 = page.get("h1", [])
            if h1:
                known_investors.add(h1[0].strip().lower())

    news_data = index_data.get("/news", {})
    investor_map = parse_news_investors(news_data, known_investors)
    print(f"      Mapped {len(investor_map)} Series A investor entries.\n")

    print("[3/4] Scanning all company pages for Series A companies...")
    records: list[CompanyRecord] = []
    company_keys = [k for k in index_data if k.startswith("/companies/")]

    for page_key in company_keys:
        slug = page_key.removeprefix("/companies/")
        rec = parse_company_page(slug, index_data[page_key])
        if rec is None:
            continue

        # Enrich with investor from news page
        rec.lead_investor = investor_map.get(rec.company_name.lower(), "")
        records.append(rec)

    # Sort: dated entries first (newest → oldest), then undated by name
    def sort_key(r: CompanyRecord):
        if r.series_a_date:
            try:
                return (0, datetime.strptime(r.series_a_date, "%Y-%m-%d"))
            except ValueError:
                pass
        return (1, datetime.min)

    records.sort(key=lambda r: (sort_key(r)[0], sort_key(r)[1], r.company_name), reverse=True)
    # undated go to end; among undated, sort by name asc
    dated = [r for r in records if r.series_a_date]
    undated = sorted([r for r in records if not r.series_a_date], key=lambda r: r.company_name)
    final_records = dated + undated

    print(f"      Found {len(final_records)} Series A companies "
          f"({len(dated)} with date, {len(undated)} without).\n")

    print("[4/4] Writing CSV...")
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS)
        writer.writeheader()
        for rec in final_records:
            writer.writerow(asdict(rec))

    print(f"      Wrote {len(final_records)} rows → {OUTPUT_CSV}\n")

    print("Opening CSV...")
    subprocess.run(["open", OUTPUT_CSV], check=False)

    print("Done!")


if __name__ == "__main__":
    main()
