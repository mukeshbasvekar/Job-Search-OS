"""
startups.gallery Series B Scraper
----------------------------------
Downloads the Framer site search-index JSON (which contains all page text)
and extracts every Series B company with full metadata.

Data sources (all from one public JSON endpoint — no HTML scraping):
  • /companies/<slug>  → name, description, location, industry, work_type,
                         company_size, funding_amount, series_b_date
  • /news              → lead_investor (best-effort, some entries missing)

Company detail pages require login, so founders / website URLs are left blank.

Run:
    pip install requests
    python scrape_series_b.py
"""

import csv
import json
import re
import subprocess
from dataclasses import asdict, dataclass, fields
from datetime import datetime
from typing import Optional

import requests

from scrape_series_a import (  # reuse shared constants/helpers where safe
    SEARCH_INDEX_URL,
    BASE_URL,
    HEADERS,
    WORK_TYPES,
    SKIP_TOKENS,
    normalize_date,
    is_date,
    is_round_dot,
    slug_to_name,
    parse_news_investors as parse_news_investors_a,
)

# ---------------------------------------------------------------------------
# Config (Series B–specific)
# ---------------------------------------------------------------------------
OUTPUT_CSV = "startups_gallery_series_b.csv"

# Regex helpers — tuned for Series B
RE_RAISED_B = re.compile(
    r"Raised\s+\$[\d.,]+[KMB]?\s+Series B\s+on\s+(.+)",
    re.IGNORECASE,
)
RE_AMOUNT_STAGE_B = re.compile(r"^\$([\d.,]+[KMB]?)\s+Series B$", re.IGNORECASE)
RE_LOCATION = re.compile(r"^[A-Za-z][A-Za-z\s\-'.]+,\s+[A-Za-z\s]+$")
RE_SIZE = re.compile(r"^\d+[\u2013\-]\d+$")  # e.g. "11–50"


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------
@dataclass
class CompanyRecordB:
    company_name: str = ""
    stage: str = "Series B"
    series_b_date: str = ""  # ISO YYYY-MM-DD when available
    funding_amount: str = ""  # e.g. "$25M"
    lead_investor: str = ""
    description: str = ""
    industry: str = ""
    work_type: str = ""
    location: str = ""
    company_size: str = ""
    company_page_url: str = ""
    founders: str = ""  # not available without login


CSV_COLUMNS_B = [f.name for f in fields(CompanyRecordB)]


# ---------------------------------------------------------------------------
# Parse a company page from the search index (Series B flavour)
# ---------------------------------------------------------------------------
NOISE_P = {
    "Join for free",
    "Backed by",
    "Visit Website",
    "View Jobs",
    "Work Type",
    "Remote",
    "Onsite",
    "Hybrid",
    "Bootstrapped",
    "Pre-Seed",
    "Seed",
    "Series A",
    "Series B",
    "Series C",
    "Series D",
    "Series E",
    "Venture",
    "Explore",
    "Jobs",
    "News",
    "About · Sponsor · Submit ↗",
    "Crafted by Louis and Gonzalo",
    "See all Industries",
    "See all Investors",
}


def parse_company_page_b(slug: str, page: dict) -> Optional[CompanyRecordB]:
    """
    Extract a CompanyRecordB from a company page entry in the search index.
    Returns None if the company is not Series B.

    This mostly mirrors scrape_series_a.parse_company_page but targets Series B.
    """
    p_items = page.get("p", [])
    h1 = page.get("h1", [])

    company_name = h1[0].strip() if h1 else slug_to_name(slug)

    funding_amount = ""
    series_b_date = ""
    description = ""
    location = ""
    industry = ""
    work_type = ""
    company_size = ""
    is_series_b = False

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

    # Check if first item is a "Raised ... Series B on ..." line
    if items[idx].startswith("Raised "):
        m_raised = RE_RAISED_B.match(items[idx])
        if m_raised:
            is_series_b = True
            series_b_date = normalize_date(m_raised.group(1).strip())
            amount_match = re.search(r"\$[\d.,]+[KMB]?", items[idx])
            if amount_match:
                funding_amount = amount_match.group(0)
        idx += 1

    # Description: next item is the long description
    if idx < len(items) and len(items[idx]) > 20 and "·" not in items[idx]:
        description = items[idx]
        idx += 1

    # Location: "City, Country"
    if idx < len(items) and RE_LOCATION.match(items[idx]):
        location = items[idx]
        idx += 1

    # Funding line: "$X Series B" or "$X Seed" etc.
    if idx < len(items) and items[idx].startswith("$"):
        funding_line = items[idx]
        m_amt = RE_AMOUNT_STAGE_B.match(funding_line)
        if m_amt:
            is_series_b = True
            funding_amount = funding_amount or f"${m_amt.group(1)}"
        elif "Series B" in funding_line:
            is_series_b = True
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

    if not is_series_b:
        return None

    return CompanyRecordB(
        company_name=company_name,
        stage="Series B",
        series_b_date=series_b_date,
        funding_amount=funding_amount,
        description=description,
        industry=industry,
        work_type=work_type,
        location=location,
        company_size=company_size,
        company_page_url=f"{BASE_URL}/companies/{slug}",
    )


# ---------------------------------------------------------------------------
# Parse news page → {company_name: lead_investor} for Series B
# ---------------------------------------------------------------------------
def parse_news_investors_b(news_page: dict, known_investors: set[str] | None = None) -> dict[str, str]:
    """
    Series B variant of parse_news_investors:
    - Only keep entries where stage is "Series B".
    """
    # Reuse the core logic from the Series A parser, but filter on stage
    # by temporarily tweaking the p-array to blank out non-Series-B stages.
    # Simpler: copy logic from parse_news_investors and change stage filter.
    p_items = news_page.get("p", [])
    investor_map: dict[str, str] = {}

    for i, item in enumerate(p_items):
        if not is_round_dot(item):
            continue

        # Stage must be "Series B"
        stage_part = item.split("·", 1)[-1].strip() if "·" in item else ""
        if stage_part.lower() != "series b":
            continue

        if i == 0:
            continue
        name = p_items[i - 1].strip()
        if not name or name in SKIP_TOKENS or is_round_dot(name) or is_date(name):
            continue

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
            if known_investors is not None:
                if candidate.lower() not in known_investors:
                    break
            investor = candidate
            break

        if name and investor:
            investor_map[name.lower()] = investor

    return investor_map


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    print("=== startups.gallery Series B Scraper ===\n")

    print("[1/4] Downloading Framer site search index...")
    resp = requests.get(SEARCH_INDEX_URL, headers=HEADERS, timeout=20)
    resp.raise_for_status()
    index_data: dict = resp.json()
    print(f"      Loaded {len(index_data)} page entries.\n")

    print("[2/4] Parsing news page for Series B lead investor data...")
    known_investors: set[str] = set()
    for page_key, page in index_data.items():
        if page_key.startswith("/investors/"):
            h1 = page.get("h1", [])
            if h1:
                known_investors.add(h1[0].strip().lower())

    news_data = index_data.get("/news", {})
    investor_map = parse_news_investors_b(news_data, known_investors)
    print(f"      Mapped {len(investor_map)} Series B investor entries.\n")

    print("[3/4] Scanning all company pages for Series B companies...")
    records: list[CompanyRecordB] = []
    company_keys = [k for k in index_data if k.startswith("/companies/")]

    for page_key in company_keys:
        slug = page_key.removeprefix("/companies/")
        rec = parse_company_page_b(slug, index_data[page_key])
        if rec is None:
            continue

        rec.lead_investor = investor_map.get(rec.company_name.lower(), "")
        records.append(rec)

    # Sort: dated entries first (newest → oldest), then undated by name
    def sort_key(r: CompanyRecordB):
        if r.series_b_date:
            try:
                return (0, datetime.strptime(r.series_b_date, "%Y-%m-%d"))
            except ValueError:
                pass
        return (1, datetime.min)

    records.sort(key=lambda r: (sort_key(r)[0], sort_key(r)[1], r.company_name), reverse=True)
    dated = [r for r in records if r.series_b_date]
    undated = sorted([r for r in records if not r.series_b_date], key=lambda r: r.company_name)
    final_records = dated + undated

    print(
        f"      Found {len(final_records)} Series B companies "
        f"({len(dated)} with date, {len(undated)} without).\n"
    )

    print("[4/4] Writing CSV...")
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_COLUMNS_B)
        writer.writeheader()
        for rec in final_records:
            writer.writerow(asdict(rec))

    print(f"      Wrote {len(final_records)} rows → {OUTPUT_CSV}\n")

    try:
        print("Opening CSV...")
        subprocess.run(["open", OUTPUT_CSV], check=False)
    except Exception:
        pass

    print("Done!")


if __name__ == "__main__":
    main()

