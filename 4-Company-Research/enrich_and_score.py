"""
Outreach Enrichment & Alignment Scoring
-----------------------------------------
Reads startups_gallery_series_a.csv, scores each company for alignment
with YOUR background, and outputs:

  1. startups_gallery_series_a_scored.csv   — all companies with scores
  2. outreach_shortlist.csv                 — top companies prioritized for cold email

CUSTOMIZE: Edit the scoring tables below (INDUSTRY_SCORE, HIGH_FIT_KEYWORDS,
WORK_TYPE_SCORE, COMPANY_SIZE_SCORE) to match YOUR background and preferences.

Run: python enrich_and_score.py
"""

import csv
import re
import subprocess
from dataclasses import dataclass, asdict, fields
from datetime import datetime, date

INPUT_CSV = "startups_gallery_series_a.csv"
SCORED_CSV = "startups_gallery_series_a_scored.csv"
SHORTLIST_CSV = "outreach_shortlist.csv"

# ─── YOUR profile: customize these to match your background ─────────────────
# Edit the values below to reflect your domain expertise and preferences.

# Industry scores (out of 3)
INDUSTRY_SCORE = {
    "AI": 3,
    "DevTools": 3,
    "Cybersecurity": 3,
    "Productivity": 2,
    "Analytics": 2,
    "HR & Recruiting": 2,
    "Healthcare": 2,
    "Education": 2,
    "Fintech": 1,
    "Consumer": 1,
    "Energy": 1,
    "Design": 1,
    "Logistics": 1,
    "Legal": 1,
    "Robotics": 1,
    "Marketing": 1,
    "Operations": 2,
    "Health & Wellness": 1,
}

# Keywords in description that signal strong fit (from YOUR background — edit this list)
HIGH_FIT_KEYWORDS = [
    "agent", "agentic", "llm", "generative", "ai-native", "copilot",
    "automation", "workflow", "enterprise", "b2b", "saas", "platform",
    "operator", "operations", "clinical", "security", "compliance",
    "api", "developer", "infrastructure", "orchestration",
    "product-led", "self-serve", "adoption", "onboarding",
    "data", "intelligence", "insights", "decision",
]

# Work type scores
WORK_TYPE_SCORE = {
    "Remote": 2,
    "Hybrid": 1,
    "Onsite": 0,
}

# Company size scores
COMPANY_SIZE_SCORE = {
    "1–10":   3,  # Founding PM opportunity
    "1-10":   3,
    "11–50":  2,  # Early-stage PM
    "11-50":  2,
    "51–200": 1,
    "51-200": 1,
}

# Role suggested based on score + size + industry
def suggest_role(company_size: str, score: int, description: str, industry: str) -> str:
    desc_lower = description.lower()
    is_tiny = any(s in company_size for s in ["1–10", "1-10"])
    is_small = any(s in company_size for s in ["11–50", "11-50"])
    is_ai = industry == "AI" or any(k in desc_lower for k in ["agent", "llm", "agentic", "ai-native"])
    is_ops = any(k in desc_lower for k in ["operations", "workflow", "operator", "deployment"])

    if is_tiny:
        if is_ai:
            return "Founding PM / Agent PM"
        return "Founding PM"
    elif is_small:
        if is_ai:
            return "PM / Agent PM"
        if is_ops:
            return "PM / Product Ops"
        return "PM"
    else:
        return "PM"


def cold_email_priority(score: int, company_size: str, work_type: str) -> str:
    is_small = any(s in company_size for s in ["1–10", "1-10", "11–50", "11-50"])
    if score >= 9 and is_small:
        return "🔥 Top Target"
    elif score >= 7:
        return "✅ High"
    elif score >= 5:
        return "Medium"
    else:
        return "Low"


# ─── Scoring ─────────────────────────────────────────────────────────────

def score_row(row: dict) -> dict:
    industry = row.get("industry", "").strip()
    description = row.get("description", "").lower()
    work_type = row.get("work_type", "").strip()
    company_size = row.get("company_size", "").strip()
    series_a_date = row.get("series_a_date", "").strip()
    funding_amount = row.get("funding_amount", "").strip()

    # 1. Industry alignment (0–3)
    industry_pts = INDUSTRY_SCORE.get(industry, 0)

    # 2. Description keyword match (0–3, capped)
    kw_hits = sum(1 for kw in HIGH_FIT_KEYWORDS if kw in description)
    kw_pts = min(3, kw_hits)

    # 3. Work type (0–2)
    wt_pts = WORK_TYPE_SCORE.get(work_type, 0)

    # 4. Company size (0–3)
    size_pts = COMPANY_SIZE_SCORE.get(company_size, 0)

    # 5. Recency bonus (0–1): funded in last 18 months → actively building
    recency_pts = 0
    if series_a_date:
        try:
            funded = datetime.strptime(series_a_date, "%Y-%m-%d").date()
            months_ago = (date.today() - funded).days / 30
            if months_ago <= 18:
                recency_pts = 1
        except ValueError:
            pass

    total = industry_pts + kw_pts + wt_pts + size_pts + recency_pts
    max_score = 12

    pct = round(total / max_score * 100)

    role = suggest_role(company_size, total, description, industry)
    priority = cold_email_priority(total, company_size, work_type)

    # Email domain guess: for cold emailing once you find the founder name
    # Most common startup email patterns: firstname@company.com or firstname@company.ai
    # We can't know the domain automatically, so flag it for manual fill
    slug = row.get("company_page_url", "").rstrip("/").split("/")[-1]
    email_domain_guess = f"{slug}.com  ← verify"

    return {
        **row,
        "alignment_score": total,
        "alignment_pct": pct,
        "suggested_role": role,
        "cold_email_priority": priority,
        "email_domain_guess": email_domain_guess,
        "founder_name": "",          # fill via Apollo.io / LinkedIn
        "founder_email": "",         # fill via Apollo.io / Hunter.io
        "founder_linkedin": "",      # fill manually or via LinkedIn Sales Nav
        "outreach_status": "Not Started",
        "outreach_notes": "",
    }


# ─── Main ─────────────────────────────────────────────────────────────────

def main():
    print("=== Outreach Enrichment & Scoring ===\n")

    with open(INPUT_CSV, encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))
    print(f"Loaded {len(rows)} rows from {INPUT_CSV}\n")

    scored = [score_row(r) for r in rows]

    # Sort by score desc, then company name
    scored.sort(key=lambda r: (-r["alignment_score"], r["company_name"]))

    all_cols = list(scored[0].keys())

    # ── Write full scored CSV ──────────────────────────────────────────
    with open(SCORED_CSV, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=all_cols)
        writer.writeheader()
        writer.writerows(scored)
    print(f"Wrote {len(scored)} scored rows → {SCORED_CSV}")

    # ── Write shortlist: score >= 6 (top ~60 companies) ───────────────
    shortlist = [r for r in scored if r["alignment_score"] >= 6][:80]
    with open(SHORTLIST_CSV, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=all_cols)
        writer.writeheader()
        writer.writerows(shortlist)
    print(f"Wrote {len(shortlist)} shortlisted rows → {SHORTLIST_CSV}\n")

    # ── Print summary ─────────────────────────────────────────────────
    top_targets = [r for r in scored if "🔥" in r["cold_email_priority"]]
    high_priority = [r for r in scored if r["cold_email_priority"] == "✅ High"]

    print("=== PRIORITY BREAKDOWN ===")
    print(f"  🔥 Top Targets  : {len(top_targets)}")
    print(f"  ✅ High         : {len(high_priority)}")
    print(f"  Medium          : {len([r for r in scored if r['cold_email_priority'] == 'Medium'])}")
    print()

    print("=== TOP 20 COMPANIES FOR COLD EMAIL ===")
    print(f"{'#':>3}  {'Company':<28} {'Score':>5}  {'Role':<25}  {'Size':<8}  {'Location'}")
    print("─" * 105)
    for i, r in enumerate(scored[:20], 1):
        print(
            f"{i:>3}  {r['company_name']:<28} {r['alignment_score']:>4}/{12}  "
            f"{r['suggested_role']:<25}  {r['company_size']:<8}  {r['location'][:30]}"
        )

    print()
    print("=== SCORE BREAKDOWN BY INDUSTRY ===")
    ind_scores: dict[str, list[int]] = {}
    for r in scored:
        ind = r.get("industry", "Other") or "Other"
        ind_scores.setdefault(ind, []).append(r["alignment_score"])
    for ind, scores in sorted(ind_scores.items(), key=lambda x: -sum(x[1]) / max(len(x[1]), 1)):
        avg = sum(scores) / len(scores)
        count = len(scores)
        print(f"  {ind:<22} avg {avg:4.1f}  ({count} companies)")

    print()
    print("Opening shortlist CSV...")
    subprocess.run(["open", SHORTLIST_CSV], check=False)
    print("\nDone!")


if __name__ == "__main__":
    main()
