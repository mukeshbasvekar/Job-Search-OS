"""Read and update the outreach tracker CSV."""
import csv
from datetime import date
from pathlib import Path

from jsos.config import get_tracker_csv

VALID_STATUSES = ["Not Started", "Sent", "Replied", "Meeting Booked", "No Response", "Rejected"]

TEMPLATE_HEADERS = [
    "company_name", "stage", "industry", "work_type", "location",
    "company_size", "contact_name", "contact_title", "contact_email",
    "outreach_status", "email_sent_date", "reply_date", "reply_type",
    "meeting_booked_date", "notes",
]


def _ensure_tracker() -> Path:
    tracker_csv = get_tracker_csv()
    if not tracker_csv.exists():
        tracker_csv.parent.mkdir(parents=True, exist_ok=True)
        with open(tracker_csv, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=TEMPLATE_HEADERS)
            writer.writeheader()
    return tracker_csv


def load() -> list[dict]:
    tracker_csv = _ensure_tracker()
    with open(tracker_csv, encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def update_status(company_name: str, status: str) -> bool:
    """Update the outreach_status for a company. Returns True if found."""
    rows = load()
    updated = False
    for row in rows:
        if row.get("company_name", "").lower() == company_name.lower():
            row["outreach_status"] = status
            if status == "Sent" and not row.get("email_sent_date"):
                row["email_sent_date"] = date.today().isoformat()
            elif status == "Replied" and not row.get("reply_date"):
                row["reply_date"] = date.today().isoformat()
            elif status == "Meeting Booked" and not row.get("meeting_booked_date"):
                row["meeting_booked_date"] = date.today().isoformat()
            updated = True

    if updated:
        tracker_csv = get_tracker_csv()
        cols = list(rows[0].keys()) if rows else TEMPLATE_HEADERS
        with open(tracker_csv, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.DictWriter(f, fieldnames=cols)
            writer.writeheader()
            writer.writerows(rows)

    return updated


def add(company: dict) -> None:
    """Append a new company row to the tracker."""
    rows = load()
    tracker_csv = get_tracker_csv()
    cols = list(rows[0].keys()) if rows else TEMPLATE_HEADERS
    with open(tracker_csv, "a", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=cols)
        if not rows:
            writer.writeheader()
        writer.writerow({k: company.get(k, "") for k in cols})


def stats() -> dict:
    rows = load()
    counts = {}
    for row in rows:
        s = row.get("outreach_status", "Unknown")
        counts[s] = counts.get(s, 0) + 1
    return {"total": len(rows), "by_status": counts}
