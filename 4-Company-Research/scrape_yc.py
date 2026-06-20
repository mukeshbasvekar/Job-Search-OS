"""
YC companies scraper (no HTML rendering)
----------------------------------------
Fetches Y Combinator companies from the unofficial but stable `yc-oss` JSON API:

  https://yc-oss.github.io/api/companies/all.json

Then writes a CSV suitable for the same scoring pipeline we use for
startups.gallery stages (industry/work_type/location/company_size, etc.).

Run:
  python scrape_yc.py
"""

from __future__ import annotations

import csv
import re
from datetime import datetime
from typing import Any

import requests


YC_ALL_URL = "https://yc-oss.github.io/api/companies/all.json"
OUTPUT_CSV = "startups_gallery_yc.csv"


WORK_TYPES = {"Remote": "Remote", "Onsite": "Onsite", "Hybrid": "Hybrid"}


def normalize_iso_date(raw: str) -> str:
    """
    Normalize dates coming from yc-oss (e.g. '2019-06-01' or ISO timestamps)
    to 'YYYY-MM-DD'. Returns '' if unknown.
    """
    if not raw:
        return ""
    raw = str(raw).strip()
    if not raw:
        return ""

    # Common patterns first.
    if re.match(r"^\d{4}-\d{2}-\d{2}$", raw):
        return raw

    # Try ISO datetime.
    try:
        # Handle trailing Z
        raw2 = raw.replace("Z", "+00:00")
        dt = datetime.fromisoformat(raw2)
        return dt.strftime("%Y-%m-%d")
    except Exception:
        pass

    # Best-effort: first 10 chars might be YYYY-MM-DD
    if len(raw) >= 10 and raw[4] == "-" and raw[7] == "-":
        maybe = raw[:10]
        if re.match(r"^\d{4}-\d{2}-\d{2}$", maybe):
            return maybe

    return ""


def team_size_bucket(team_size: Any) -> str:
    """
    Convert YC `team_size` (number of people, often a string) into the
    same buckets we use for startups.gallery scoring.
    """
    if team_size is None or team_size == "":
        return ""
    try:
        n = int(str(team_size).strip())
    except Exception:
        return ""

    if n <= 10:
        return "1–10"
    if n <= 50:
        return "11–50"
    if n <= 200:
        return "51–200"
    if n <= 500:
        return "201–500"
    return "500+"


def work_type_from_regions(regions: Any, all_locations: str) -> str:
    """
    Infer work type from YC regions.
    This is heuristic; YC doesn't explicitly say Remote/Hybrid/Onsite.
    """
    region_list = regions if isinstance(regions, list) else []
    region_lowers = {str(r).strip().lower() for r in region_list}

    # Common values include 'Remote'
    if "remote" in region_lowers:
        return WORK_TYPES["Remote"]

    # If we see 'Remote' in all_locations string, also treat as Remote.
    if isinstance(all_locations, str) and "remote" in all_locations.lower():
        return WORK_TYPES["Remote"]

    return WORK_TYPES["Onsite"]


def classify_industry_bucket_blob(blob: str) -> str:
    """
    Map free-form YC metadata to the same industry buckets used by
    our existing enrichment/scoring scripts.
    """
    if not blob:
        return ""
    t = blob.lower()

    # 1) Security first (more specific)
    security_terms = [
        "security", "cyber", "fraud", "aml", "kyc", "soc2", "compliance",
        "vulnerability", "infosec", "threat", "ransomware", "secure",
    ]
    if any(x in t for x in security_terms):
        return "Cybersecurity"

    # 2) AI
    ai_terms = [
        "ai", "artificial intelligence", "llm", "llms", "agent", "agentic",
        "generative", "ml", "machine learning", "predictive", "copilot",
        "deep learning", "multimodal", "vision-language", "rag",
    ]
    if any(x in t for x in ai_terms):
        return "AI"

    # 3) Developer tools / infrastructure / data platforms
    devtools_terms = [
        "developer", "devtools", "api", "sdk", "tooling", "infrastructure",
        "observability", "evaluation", "monitoring", "pipeline", "data",
        "db", "database", "postgres", "kubernetes", "terraform",
        "orchestration", "workflow", "platform",
    ]
    if any(x in t for x in devtools_terms):
        return "DevTools"

    # 4) Analytics
    analytics_terms = [
        "analytics", "insights", "dashboard", "metrics", "reporting",
        "telemetry", "intelligence", "evaluation", "experimentation",
    ]
    if any(x in t for x in analytics_terms):
        return "Analytics"

    # 5) Productivity / knowledge tools
    productivity_terms = [
        "productivity", "collaboration", "docs", "documentation", "knowledge",
        "work management", "inbox", "writing", "teamwork", "automation",
        "workflow automation", "operations", "tasks",
    ]
    if any(x in t for x in productivity_terms):
        return "Productivity"

    # 6) Fintech
    fintech_terms = [
        "payments", "fintech", "wallet", "bank", "lending", "credit", "card",
        "treasury", "insurance", "risk", "underwriting", "kyb", "compliance",
    ]
    if any(x in t for x in fintech_terms):
        return "Fintech"

    # 7) Healthcare / biotech
    healthcare_terms = [
        "health", "hospital", "clinical", "hipaa", "medical", "biotech",
        "care", "patients", "healthcare",
    ]
    if any(x in t for x in healthcare_terms):
        return "Healthcare"

    # 8) HR / Recruiting
    hr_terms = ["hiring", "recruit", "talent", "workforce", "employee", "hr"]
    if any(x in t for x in hr_terms):
        return "HR & Recruiting"

    # 9) Web3
    web3_terms = ["web3", "blockchain", "crypto", "smart contract", "token"]
    if any(x in t for x in web3_terms):
        return "Web3"

    return ""


def main() -> None:
    print(f"Downloading YC companies list: {YC_ALL_URL}")
    resp = requests.get(YC_ALL_URL, timeout=60)
    resp.raise_for_status()
    data = resp.json()

    if not isinstance(data, list):
        raise RuntimeError("Unexpected YC API response: expected a list.")

    # CSV columns designed to mirror our stage CSVs closely.
    fieldnames = [
        "company_name",
        "stage",
        "yc_date",
        "funding_amount",
        "lead_investor",
        "description",
        "industry",
        "work_type",
        "location",
        "company_size",
        "company_page_url",
        "founders",
        # extra metadata (useful for scoring/debug)
        "batch",
        "website",
        "tags",
    ]

    rows: list[dict[str, str]] = []

    for c in data:
        name = (c.get("name") or "").strip()
        if not name:
            continue

        batch = (c.get("batch") or "").strip()
        stage = "YC"

        # "launched_at" is best proxy for "when they launched / became a company".
        yc_date = normalize_iso_date(c.get("launched_at") or "")

        long_description = (c.get("long_description") or "").strip()
        one_liner = (c.get("one_liner") or "").strip()
        description = long_description or one_liner

        tags = c.get("tags") or []
        tags_str = ", ".join([str(t).strip() for t in tags if str(t).strip()]) if isinstance(tags, list) else ""

        website = (c.get("website") or "").strip()
        url = (c.get("url") or "").strip()

        regions = c.get("regions") or []
        all_locations = (c.get("all_locations") or "").strip()

        work_type = work_type_from_regions(regions, all_locations)
        company_size = team_size_bucket(c.get("team_size"))

        # Location: use all_locations when possible; fall back to a region/company field.
        location = all_locations or ""
        if not location and isinstance(regions, list) and regions:
            # Use the first region as fallback
            location = str(regions[0])

        blob = " ".join([name, description or "", tags_str])
        industry_bucket = classify_industry_bucket_blob(blob)

        # company_page_url: use YC-hosted company URL if website missing
        company_page_url = website or url

        rows.append(
            {
                "company_name": name,
                "stage": stage,
                "yc_date": yc_date,
                "funding_amount": "",
                "lead_investor": "",
                "description": description,
                "industry": industry_bucket,
                "work_type": work_type,
                "location": location,
                "company_size": company_size,
                "company_page_url": company_page_url,
                "founders": "",
                "batch": batch,
                "website": website,
                "tags": tags_str,
            }
        )

    print(f"Writing {len(rows)} rows → {OUTPUT_CSV}")
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print("Done.")


if __name__ == "__main__":
    main()

