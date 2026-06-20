"""
startups.gallery Seed + Pre-Seed Scraper
-----------------------------------------
Downloads the Framer site search-index JSON and extracts every
Seed and Pre-Seed company with full metadata into one CSV.

Run:
    python scrape_seed.py
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

SEARCH_INDEX_URL = (
    "https://framerusercontent.com/sites/"
    "eQ8EfGgqmp8FpeXNnf1bo/searchIndex-3LpVJKKep0Xv.json"
)
BASE_URL = "https://startups.gallery"
OUTPUT_CSV = "startups_gallery_seed.csv"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/122.0.0.0 Safari/537.36"
    )
}

RE_ROUND_DOT = re.compile(r"^\$[\d.,]+[KMB]?\s*·\s*", re.IGNORECASE)
RE_DATE_FULL = re.compile(
    r"^(January|February|March|April|May|June|July|August|September|"
    r"October|November|December|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|"
    r"Oct|Nov|Dec)\s+\d{1,2},\s+\d{4}$",
    re.IGNORECASE,
)
RE_RAISED = re.compile(
    r"Raised\s+\$[\d.,]+[KMB]?\s+(Pre-Seed|Seed)\s+on\s+(.+)",
    re.IGNORECASE,
)
RE_AMOUNT_STAGE = re.compile(r"^\$([\d.,]+[KMB]?)\s+(Pre-Seed|Seed)$", re.IGNORECASE)
RE_LOCATION = re.compile(r"^[A-Za-z][A-Za-z\s\-'.]+,\s+[A-Za-z\s]+$")
RE_SIZE = re.compile(r"^\d+[\u2013\-]\d+$")
WORK_TYPES = {"Remote", "Onsite", "Hybrid"}
SKIP_TOKENS = {
    "Join for free", "Backed by", "Visit Website", "View Jobs",
    "Work Type", "Stages", "Industries", "Investors", "Cities", "Countries",
    "Bootstrapped", "Pre-Seed", "Seed", "Series A", "Series B", "Series C",
    "Series D", "Series E", "Venture", "Explore", "Jobs", "News",
    "About · Sponsor · Submit ↗", "See all Industries", "See all Investors",
}
FIXED_HEADERS = {"Join for free", "Backed by", "Visit Website", "View Jobs"}


@dataclass
class CompanyRecord:
    company_name: str = ""
    stage: str = ""
    round_date: str = ""
    funding_amount: str = ""
    lead_investor: str = ""
    description: str = ""
    industry: str = ""
    work_type: str = ""
    location: str = ""
    company_size: str = ""
    company_page_url: str = ""
    founders: str = ""


CSV_COLUMNS = [f.name for f in fields(CompanyRecord)]


def normalize_date(raw: str) -> str:
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


def parse_company_page(slug: str, page: dict) -> Optional[CompanyRecord]:
    p_items = page.get("p", [])
    h1 = page.get("h1", [])

    company_name = h1[0].strip() if h1 else slug_to_name(slug)

    funding_amount = ""
    round_date = ""
    description = ""
    location = ""
    industry = ""
    work_type = ""
    company_size = ""
    stage = ""
    is_target = False

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

    if items[idx].startswith("Raised "):
        m_raised = RE_RAISED.match(items[idx])
        if m_raised:
            is_target = True
            stage = m_raised.group(1)
            round_date = normalize_date(m_raised.group(2).strip())
            amount_match = re.search(r"\$[\d.,]+[KMB]?", items[idx])
            if amount_match:
                funding_amount = amount_match.group(0)
        idx += 1

    if idx < len(items) and len(items[idx]) > 20 and "·" not in items[idx]:
        description = items[idx]
        idx += 1

    if idx < len(items) and RE_LOCATION.match(items[idx]):
        location = items[idx]
        idx += 1

    if idx < len(items) and items[idx].startswith("$"):
        funding_line = items[idx]
        m_amt = RE_AMOUNT_STAGE.match(funding_line)
        if m_amt:
            is_target = True
            stage = stage or m_amt.group(2)
            funding_amount = funding_amount or f"${m_amt.group(1)}"
        elif "Seed" in funding_line or "Pre-Seed" in funding_line:
            is_target = True
            if "Pre-Seed" in funding_line:
                stage = stage or "Pre-Seed"
            else:
                stage = stage or "Seed"
            amt_m = re.search(r"\$([\d.,]+[KMB]?)", funding_line)
            if amt_m:
                funding_amount = funding_amount or f"${amt_m.group(1)}"
        idx += 1

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

    if idx < len(items) and items[idx] in WORK_TYPES:
        work_type = items[idx]
        idx += 1

    if idx < len(items) and RE_SIZE.match(items[idx]):
        company_size = items[idx]

    if not is_target:
        return None

    return CompanyRecord(
        company_name=company_name,
        stage=stage,
        round_date=round_date,
        funding_amount=funding_amount,
        description=description,
        industry=industry,
        work_type=work_type,
        location=location,
        company_size=company_size,
        company_page_url=f"{BASE_URL}/companies/{slug}",
    )


def parse_news_investors(news_page: dict, known_investors: set[str] = None) -> dict[str, str]:
    p_items = news_page.get("p", [])
    investor_map: dict[str, str] = {}

    for i, item in enumerate(p_items):
        if not is_round_dot(item):
            continue

        stage_part = item.split("·", 1)[-1].strip() if "·" in item else ""
        if stage_part.lower() not in ("seed", "pre-seed"):
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


def main():
    print("=== startups.gallery Seed + Pre-Seed Scraper ===\n")

    print("[1/4] Downloading Framer site search index...")
    resp = requests.get(SEARCH_INDEX_URL, headers=HEADERS, timeout=20)
    resp.raise_for_status()
    index_data: dict = resp.json()
    print(f"      Loaded {len(index_data)} page entries.\n")

    print("[2/4] Parsing news page for lead investor data...")
    known_investors: set[str] = set()
    for page_key, page in index_data.items():
        if page_key.startswith("/investors/"):
            h1 = page.get("h1", [])
            if h1:
                known_investors.add(h1[0].strip().lower())

    news_data = index_data.get("/news", {})
    investor_map = parse_news_investors(news_data, known_investors)
    print(f"      Mapped {len(investor_map)} Seed/Pre-Seed investor entries.\n")

    print("[3/4] Scanning all company pages for Seed + Pre-Seed companies...")
    records: list[CompanyRecord] = []
    company_keys = [k for k in index_data if k.startswith("/companies/")]

    for page_key in company_keys:
        slug = page_key.removeprefix("/companies/")
        rec = parse_company_page(slug, index_data[page_key])
        if rec is None:
            continue
        rec.lead_investor = investor_map.get(rec.company_name.lower(), "")
        records.append(rec)

    dated = sorted(
        [r for r in records if r.round_date],
        key=lambda r: r.round_date,
        reverse=True,
    )
    undated = sorted([r for r in records if not r.round_date], key=lambda r: r.company_name)
    final_records = dated + undated

    seed_count = sum(1 for r in final_records if r.stage == "Seed")
    preseed_count = sum(1 for r in final_records if r.stage == "Pre-Seed")
    print(f"      Found {len(final_records)} companies "
          f"({seed_count} Seed, {preseed_count} Pre-Seed, "
          f"{len(dated)} with date, {len(undated)} without).\n")

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
