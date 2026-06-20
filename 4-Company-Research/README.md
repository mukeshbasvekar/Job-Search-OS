# Company Research — Startup Sourcing

Python scrapers for [startups.gallery](https://startups.gallery) — a curated database of funded startups. Pull company lists by funding stage, score them against your background, and export a prioritized outreach shortlist.

---

## Setup

```bash
pip install -r requirements.txt
```

No API keys required. The scrapers pull from the public Framer search index JSON.

---

## Scripts

| Script | Output | Companies |
|---|---|---|
| `scrape_series_a.py` | `startups_gallery_series_a.csv` | Series A companies |
| `scrape_series_b.py` | `startups_gallery_series_b.csv` | Series B companies |
| `scrape_seed.py` | `startups_gallery_seed.csv` | Seed/Pre-Seed companies |
| `scrape_yc.py` | `startups_gallery_yc.csv` | YC companies |
| `enrich_and_score.py` | `*_scored.csv` + `outreach_shortlist.csv` | Scored + filtered |

---

## How to Use

### Step 1: Scrape a funding stage

```bash
python scrape_series_a.py
```

This downloads the search index, parses all company pages for Series A companies, and writes a CSV with:
- `company_name`, `stage`, `funding_date`, `funding_amount`, `lead_investor`
- `description`, `industry`, `work_type`, `location`, `company_size`
- `company_page_url`

### Step 2: Score companies by fit

```bash
python enrich_and_score.py
```

Open `enrich_and_score.py` and edit the scoring criteria at the top of the file to match your background:
- `INDUSTRY_ALIGNMENT`: industries you know well → higher score
- `KEYWORD_MATCH`: keywords from your background that align (AI, LLM, SaaS, B2B, etc.)
- `COMPANY_SIZE_PREFERENCE`: what team size you're targeting
- `SCORE_THRESHOLD`: minimum score to include in the shortlist

### Step 3: Work the shortlist

Open `outreach_shortlist.csv`. This is your prioritized outreach universe, sorted by fit score.

Top targets → cold email the founder directly (find email via Apollo.io free tier).
High fit → apply + follow up with a cold email.

---

## Data Source

All data comes from the public Framer search index JSON used by startups.gallery. No login required, no API key needed. The scrapers parse the same JSON that powers the site's search function.

URL pattern: `https://framerusercontent.com/sites/[site-id]/searchIndex-[hash].json`

If the scraper stops working, the JSON URL may have rotated — check the network tab on startups.gallery to find the current URL and update `SEARCH_INDEX_URL` in the scraper.

---

## Adding a New Funding Stage

To scrape a stage not covered by existing scripts:
1. Copy `scrape_series_a.py`
2. Change the stage filter string (e.g., `"Series A"` → `"Series C"`)
3. Change the date field name (`series_a_date` → `series_c_date`)
4. Change the output CSV filename
5. Run it

See `FUNDING_STAGE_SCRAPE_PLAYBOOK.md` for the full process.

---

## Output Files

After running the scripts, you'll have:

```
4-Company-Research/
├── startups_gallery_series_a.csv       ← Raw Series A companies
├── startups_gallery_series_a_scored.csv ← Same companies with fit scores
├── outreach_shortlist.csv              ← Top companies above score threshold
├── do_not_contact.csv                  ← (you create this) companies to skip
```

The `do_not_contact.csv` is a list of companies you've already emailed, rejected, or decided to skip — so you don't re-process them.
