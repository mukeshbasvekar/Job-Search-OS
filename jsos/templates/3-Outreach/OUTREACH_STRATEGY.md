# Cold Email Outreach Strategy

A data-backed system for running high-volume, personalized cold email outreach to startup founders and hiring managers. Built on real results from 3 months of active searching.

---

## The Core Insight

**Cold emails to founders outperform cold applications by 2–3x.**

| Channel | Expected HM+ Rate |
|---|---|
| Cold Emails + LinkedIn (direct to founder) | 50–65% |
| Networking (warm intros) | 45–55% |
| Cold Applications (ATS) | 35–45% |
| Inbound (job boards, referrals) | 25–35% |

The leverage is in the numerator — getting in front of a founder directly rather than competing in an ATS queue. But volume without personalization kills reply rate. This system solves both.

---

## What We Built

The `4-Company-Research/` folder contains Python scrapers for startups.gallery that pull company data by funding stage (Series A, B, Seed, YC). Each scraper:

1. Downloads the public company index from startups.gallery
2. Filters by funding stage
3. Exports company name, description, industry, work type, location, size, funding date, lead investor

Then `enrich_and_score.py` scores each company against your target background (edit the scoring criteria to match your domain and role type preferences).

**Output files:**
- `startups_gallery_[stage].csv` — raw companies by stage
- `startups_gallery_[stage]_scored.csv` — same companies with fit scores
- `outreach_shortlist.csv` — top companies above your score threshold

---

## Priority Breakdown

| Priority | Score Range | Action |
|---|---|---|
| Top Target | 9–12 | Cold email founder directly, same day |
| High | 7–8 | Apply + follow up with cold email |
| Medium | 5–6 | Apply via ATS |
| Low | <5 | Skip for now |

---

## Scoring Criteria (Customize in enrich_and_score.py)

The default scoring weights are:
- **Industry alignment** to your background: 0–3 points
- **Description keyword match** (AI, LLM, automation, enterprise, SaaS, B2B, etc.): 0–3 points
- **Work type**: Remote = 2pts, Hybrid = 1pt
- **Company size**: 1–10 employees = 3pts (Founding PM roles), 11–50 = 2pts
- **Recently funded** (within 18 months): +1pt

Edit these weights in the script to match your preferences.

---

## The 5-Step Daily Workflow

### Step 1: Pick your batch (15 min)
Each morning, open `outreach_shortlist.csv` and pick 3–5 companies you haven't contacted yet. Filter by:
- Companies you find genuinely interesting (personalization shows)
- Remote or Hybrid first (unless targeting a specific city)
- Smallest team size for founding/early PM roles

### Step 2: Research the founder (5–10 min per company)
For each company:
1. Go to their `company_page_url` on startups.gallery → click "Visit Website"
2. Find the founder's name and title (CEO/CTO/CPO) on the About/Team page
3. Spend 3 min on their LinkedIn: recent posts, what they care about

### Step 3: Find their email (5 min per company)

**Option A: Apollo.io (best — 50 free credits/month)**
1. Go to app.apollo.io → sign in free
2. Search for the person by name + company
3. Click "Get Email" — reveals work email directly

**Option B: Hunter.io (25 free searches/month)**
1. Enter the company domain
2. See the email pattern used (e.g., firstname@company.com)
3. Apply pattern to the founder's name

**Option C: Pattern guessing (~60–70% hit rate)**
- Most common startup patterns: `firstname@company.com`, `firstname@company.ai`, `firstname@company.io`
- Use mail-tester.com or verify-email.org to check validity

**Option D: LinkedIn DM (always works, slightly lower reply rate)**
- Send directly on LinkedIn — good for founders who are active there

### Step 4: Write and send (10 min per email)
Use `email_prompt.md` with Claude/GPT-4o to generate tailored bullets for this specific role. Paste in: `email_prompt.md` + `YOUR_context.md` + company JD or description.

Fill in the 3 things per send:
1. First name
2. Personalization line (one specific thing about the company)
3. The 3 bullets from the AI output

### Step 5: Track and follow up
- Log the outreach in `tracker_template.csv`: Not Started → Sent → Replied → Meeting Booked
- If no reply in 5–7 business days: Email 2 goes out automatically (set up in your outreach tool)
- If no reply after Email 2: Email 3 goes out on Day 9–10 automatically
- If still no reply: Mark "No Response" and move on

---

## Volume Targets

| Track | Volume | When |
|---|---|---|
| Track 1: Core list (scored shortlist) | 25 emails/day | Daily, morning |
| Track 2: Opportunistic (found online, interesting) | 5–10 emails/day | As you spot them |
| Track 3: Big companies (polished, role-specific) | 5 emails/week | Sunday/Monday batch |

If you do 25 emails/day for 2 weeks:
- 350 emails → ~175–220 replies at 50–65% rate → ~175 founder-level conversations
- That's more pipeline than 6 months of cold applications combined

---

## What NOT to Do

- ❌ Don't email all shortlisted companies in one batch
- ❌ Don't send a generic email without a real personalization line
- ❌ Don't target seniority levels where your callback rate is low (check your data)
- ❌ Don't use email-finding services for every company before confirming the fit
- ❌ Don't skip international companies — many are remote-friendly
- ❌ Don't try to optimize the email further once it's working. If you're getting replies, send more

---

## Quick Start (Today)

1. Run `scrape_series_a.py` in `4-Company-Research/`
2. Run `enrich_and_score.py` — check the output CSV
3. Open the scored CSV and pick 5 companies that genuinely interest you
4. For each: find founder name → find email (Apollo free) → write personalized email (email_prompt.md + Claude)
5. Send today
6. Log in tracker

Repeat daily. The system compounds — each batch adds pipeline.
