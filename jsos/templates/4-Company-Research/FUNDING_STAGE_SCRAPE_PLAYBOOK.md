# startups.gallery Funding-Stage Scrape Playbook

Single source of truth for scraping any funding stage from startups.gallery, scoring companies, and managing your outreach pipeline.

---

## 1. Data Source

- **Source:** The public Framer search index JSON used by startups.gallery
- **URL:** `https://framerusercontent.com/sites/[site-id]/searchIndex-[hash].json`
- **Extraction strategy:** Parse `/companies/<slug>` entries to get metadata; parse `/news` to map company names to lead investors. No login required.

If the URL breaks (it can rotate): open startups.gallery in Chrome, open DevTools → Network tab → filter for `searchIndex` → copy the current URL and update `SEARCH_INDEX_URL` in the scraper.

---

## 2. Scripts

| Stage | Script | Output CSV |
|---|---|---|
| Series A | `scrape_series_a.py` | `startups_gallery_series_a.csv` |
| Series B | `scrape_series_b.py` | `startups_gallery_series_b.csv` |
| Seed/Pre-Seed | `scrape_seed.py` | `startups_gallery_seed.csv` |
| YC | `scrape_yc.py` | `startups_gallery_yc.csv` |

Output columns: `company_name, stage, [stage]_date, funding_amount, lead_investor, description, industry, work_type, location, company_size, company_page_url`

---

## 3. Running a Scrape

```bash
# From the 4-Company-Research/ directory:
pip install -r requirements.txt
python scrape_series_a.py
```

The script will:
1. Download the Framer search index JSON
2. Parse `/news` for lead investors by stage
3. Parse `/companies/*` pages and keep only the target stage companies
4. Sort by funding date (newest first), then alphabetically
5. Write the CSV

---

## 4. Scoring (enrich_and_score.py)

After scraping, run the scoring script to rank companies by fit:

```bash
python enrich_and_score.py
```

**Customize the scoring criteria** at the top of `enrich_and_score.py`:

```python
# Industries you know well → higher score
INDUSTRY_ALIGNMENT = {
    "AI / Machine Learning": 3,
    "Developer Tools": 3,
    "Cybersecurity": 3,
    "SaaS": 2,
    "Productivity": 2,
    "Healthcare": 2,
    # ... add your own
}

# Keywords that match your background
KEYWORD_MATCH = ["agent", "LLM", "automation", "enterprise", "B2B", ...]

# Target company size
COMPANY_SIZE_SCORES = {
    "1-10": 3,   # Founding PM territory
    "11-50": 2,
    "51-200": 1,
    "201+": 0,
}

# Score threshold for shortlist
SCORE_THRESHOLD = 6  # out of 12
```

**Output:**
- `startups_gallery_[stage]_scored.csv` — all companies with scores
- `outreach_shortlist.csv` — companies above threshold, sorted by score

---

## 5. Adding a New Stage

To scrape a stage not yet covered:

1. Copy `scrape_series_a.py` → rename to `scrape_series_c.py`
2. Change the stage filter:
   ```python
   TARGET_STAGE = "Series C"  # was "Series A"
   ```
3. Change the date field:
   ```python
   date_field = "series_c_date"  # was "series_a_date"
   ```
4. Change the output filename:
   ```python
   OUTPUT_CSV = "startups_gallery_series_c.csv"
   ```
5. Run it

---

## 6. Managing the Pipeline

**Tracking files you should maintain:**

| File | Purpose |
|---|---|
| `outreach_shortlist.csv` | Companies you're actively targeting |
| `do_not_contact.csv` | Companies to skip (already emailed, rejected, not a fit) |
| `../3-Outreach/tracker_template.csv` | Full outreach tracker with status per company |

**Status flow:**
Not Started → Sent → Replied → Meeting Booked → No Response / Rejected

Work through the shortlist top-down. When a company moves to Sent in the tracker, add it to `do_not_contact.csv` so it doesn't appear in future shortlists.

---

## 7. End-to-End Checklist

When you want to refresh your pipeline with a new stage:

1. Run the scraper: `python scrape_[stage].py`
2. Run scoring: `python enrich_and_score.py`
3. Open `outreach_shortlist.csv` — sort by score descending
4. Filter out any companies already in `do_not_contact.csv`
5. Add top 20–30 to your active outreach batch
6. Send 5–10 emails/day, tracking in `tracker_template.csv`
