"""Score companies from a scraped CSV using weights from config.yaml."""
import csv
from datetime import date, datetime
from pathlib import Path

from jsos.config import load as load_config, DATA_DIR


def _suggest_role(company_size: str, cfg: dict) -> str:
    roles = cfg.get("target_roles", {})
    is_tiny = any(s in company_size for s in ["1–10", "1-10"])
    is_small = any(s in company_size for s in ["11–50", "11-50"])
    if is_tiny:
        return roles.get("founding", "Founding Role")
    elif is_small:
        return roles.get("early", "Early Role")
    return roles.get("standard", "Role")


def _priority_label(score: int, company_size: str) -> str:
    is_small = any(s in company_size for s in ["1–10", "1-10", "11–50", "11-50"])
    if score >= 9 and is_small:
        return "Top Target"
    elif score >= 7:
        return "High"
    elif score >= 5:
        return "Medium"
    return "Low"


def score_row(row: dict, cfg: dict) -> dict:
    scoring = cfg.get("scoring", {})
    industry_map = scoring.get("industry", {})
    keywords = [k.lower() for k in scoring.get("keywords", [])]
    work_type_map = scoring.get("work_type", {})
    size_map = scoring.get("company_size", {})
    recency_months = scoring.get("recency_months", 18)

    industry = row.get("industry", "").strip()
    description = row.get("description", "").lower()
    work_type = row.get("work_type", "").strip()
    company_size = row.get("company_size", "").strip()
    funding_date = (row.get("funding_date") or row.get("series_a_date") or
                    row.get("series_b_date") or row.get("seed_date") or
                    row.get("yc_date") or "").strip()

    industry_pts = industry_map.get(industry, 0)
    kw_hits = sum(1 for kw in keywords if kw in description)
    kw_pts = min(3, kw_hits)
    wt_pts = work_type_map.get(work_type, 0)
    size_pts = size_map.get(company_size, 0)

    recency_pts = 0
    if funding_date:
        try:
            funded = datetime.strptime(funding_date, "%Y-%m-%d").date()
            if (date.today() - funded).days / 30 <= recency_months:
                recency_pts = 1
        except ValueError:
            pass

    total = industry_pts + kw_pts + wt_pts + size_pts + recency_pts

    slug = row.get("company_page_url", "").rstrip("/").split("/")[-1]

    return {
        **row,
        "alignment_score": total,
        "alignment_pct": round(total / 12 * 100),
        "suggested_role": _suggest_role(company_size, cfg),
        "priority": _priority_label(total, company_size),
        "email_domain_guess": f"{slug}.com",
        "founder_name": row.get("founder_name", ""),
        "founder_email": row.get("founder_email", ""),
        "outreach_status": row.get("outreach_status", "Not Started"),
        "outreach_notes": row.get("outreach_notes", ""),
    }


def run(input_csv: Path, output_csv: Path | None = None, shortlist_csv: Path | None = None) -> list[dict]:
    cfg = load_config()
    scoring = cfg.get("scoring", {})
    threshold = scoring.get("threshold", 6)
    limit = scoring.get("shortlist_limit", 80)

    DATA_DIR.mkdir(exist_ok=True)

    with open(input_csv, encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))

    scored = [score_row(r, cfg) for r in rows]
    scored.sort(key=lambda r: (-r["alignment_score"], r.get("company_name", "")))

    if not scored:
        return scored

    cols = list(scored[0].keys())

    out = output_csv or DATA_DIR / (input_csv.stem + "_scored.csv")
    with open(out, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=cols)
        writer.writeheader()
        writer.writerows(scored)

    shortlist = [r for r in scored if r["alignment_score"] >= threshold][:limit]
    sl = shortlist_csv or DATA_DIR / "outreach_shortlist.csv"
    with open(sl, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=cols)
        writer.writeheader()
        writer.writerows(shortlist)

    return scored
