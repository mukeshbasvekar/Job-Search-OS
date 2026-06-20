# Job Search OS

[![Stars](https://img.shields.io/github/stars/mukeshbasvekar/Job-Search-OS?style=flat-square)](https://github.com/mukeshbasvekar/Job-Search-OS/stargazers)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](LICENSE)

> Most job searches fail not from lack of effort — but from lack of system.

I spent 3 months job searching the right way: cold emails to founders, a tailored resume for every JD, deep interview prep from scratch each time. I built tooling to stop doing it manually. **It worked.** This is that system, open-sourced.

**What this is:** a CLI (`jsos`) + AI prompts + LaTeX templates + Python scrapers that work together as a single, coherent job search engine.

**What this is not:** a Notion template collection you'll open once and forget.

---

### Numbers from running it live

- **25–50 personalized cold emails/day** — AI does the tailoring, you do the sending
- **Cold emails to founders convert 2–3× better** than job board applications
- **Tailored resume in under 10 minutes** — rebuilt from scratch for each JD
- **8-phase interview prep** that predicts their questions before you walk in
- **One profile file** (`YOUR_context.md`) — fill it in once, every prompt reads from it

---

Built by [Mukesh Basvekar](https://www.linkedin.com/in/mukeshbasvekar/) · If this saves you time, drop a ⭐ — it helps others find it.

---

## Install

```bash
# Clone or download this folder, then:
python3 -m venv .venv
source .venv/bin/activate       # Windows: .venv\Scripts\activate
pip install -e .

# Verify
jsos --help
```

## Usage

```bash
jsos scrape --stage series-a    # Pull Series A companies from startups.gallery
jsos scrape --stage seed        # Pull Seed/Pre-Seed companies

jsos score  --stage series-a    # Score companies by fit (uses config.yaml)
jsos list                       # Show your top targets
jsos list   --min-score 8       # Only show high-fit companies

jsos track  --company "Stripe" --status sent     # Log an outreach
jsos track  --company "Stripe" --status replied  # Update when they reply
jsos stats                      # See your full pipeline stats
```

## Configure

Open `config.yaml` and set your preferences once. The scoring weights — which industries matter to you, which keywords match your background, company size preference — all live there. No code changes needed.

---

## What's Inside

| Module | What It Does |
|---|---|
| [1-Profile](1-Profile/) | Your single source of truth — fill this in once, everything else draws from it |
| [2-Resume](2-Resume/) | AI-powered LaTeX resume generation tailored to any job description |
| [3-Outreach](3-Outreach/) | Cold email system — 3-email sequence, AI prompt, strategy, tracker |
| [4-Company-Research](4-Company-Research/) | Python scrapers for startups.gallery (Series A/B/Seed/YC) + scoring |
| [5-Interview-Prep](5-Interview-Prep/) | 8-phase interview prep system, story bank, company research template |
| [6-Strategy](6-Strategy/) | The full job search playbook — channel data, Rule of Three, daily ops |

---

## Setup (30 Minutes)

### Step 1 — Fill in your profile (20 min)
Open [1-Profile/YOUR_context.md](1-Profile/YOUR_context.md) and fill in every section. This is the most important step. Every AI prompt in this system reads from this file.

Then fill in [1-Profile/YOUR_resume_data_compact.md](1-Profile/YOUR_resume_data_compact.md) — a faster-lookup version for AI.

### Step 2 — Set up your resume template (5 min)
Open [2-Resume/template/resume_template.tex](2-Resume/template/resume_template.tex) and replace the placeholder header with your real name, email, LinkedIn, and portfolio URL.

Install [Tectonic](https://tectonic-typesetting.github.io/) (LaTeX compiler) if you don't have it:
```bash
brew install tectonic
```

Test the build:
```bash
cd 2-Resume/template
bash build.sh
```

### Step 3 — Configure the resume prompt (5 min)
Open [2-Resume/prompts/prompt.md](2-Resume/prompts/prompt.md) and read through it. The prompts reference `YOUR_context.md` — you don't need to change file paths as long as you're giving both files to your AI.

### Step 4 — Set up the outreach tracker (2 min)
Copy [3-Outreach/tracker_template.csv](3-Outreach/tracker_template.csv) and rename it `outreach_tracker.csv`. This is where you track every company you contact.

---

## How to Use Each Module

### Generating a Tailored Resume

1. Find a job description you want to apply to
2. Open a new chat with Claude (or GPT-4o)
3. Paste in: `2-Resume/prompts/prompt_compact.md` + `1-Profile/YOUR_context.md` + the job description
4. The AI will generate a production-ready `.tex` file tailored to that JD
5. Compile with `tectonic output/your_resume.tex`

### Writing a Cold Email

1. Find a company + founder email (Apollo.io free tier works)
2. Open a new chat with Claude
3. Paste in: `3-Outreach/email_prompt.md` + `1-Profile/YOUR_context.md` + the JD or role description
4. The AI generates a personalized 3-bullet cold email
5. Send Email 1 manually, set Email 2 and 3 as automated follow-ups

### Sourcing Companies to Email

1. Run the scrapers in `4-Company-Research/` to pull fresh startup data from startups.gallery
2. Run `enrich_and_score.py` to score companies by fit with your background
3. Export the shortlist and work through it top-down

### Preparing for an Interview

1. Open a new chat with Claude
2. Paste in: `5-Interview-Prep/prompts/interview_prep_prompt.md` + `1-Profile/YOUR_context.md` + `5-Interview-Prep/stories/YOUR_behavioral_stories.yaml` + the JD
3. The AI generates an 8-phase prep doc: role decode, company research, narrative, behavioral prep, questions to ask, objections, logistics, thank-you email

---

## The Philosophy

Three things that actually move the needle in a job search:

**1. Volume with personalization at the top of funnel.** Cold emails to founders outperform cold applications by 2–3x. But mass-blasting generic emails kills your reply rate. The system here runs 25–50 cold emails/day while keeping each one genuinely personalized — because the AI does the tailoring work.

**2. Resume as a positioning document, not a CV.** Every resume here is rebuilt from scratch for each job, leading with the metrics and framing that matter for that specific role. The LaTeX template ensures it looks polished every time.

**3. Interview prep as prediction, not just rehearsal.** The 8-phase prep system forces you to predict what they'll ask before they ask it — based on the JD, company stage, and role type. You walk in knowing the questions.

---

## What You'll Need

- **AI:** Claude (claude.ai or Claude Code) or GPT-4o — paste prompts + context files into any of them
- **LaTeX compiler:** [Tectonic](https://tectonic-typesetting.github.io/) (recommended) or `pdflatex`
- **Python 3.8+:** For the company scrapers
- **Apollo.io (free tier):** 50 email lookups/month — enough for 50 cold emails
- **A spreadsheet (Google Sheets or Excel):** For the outreach tracker

---

## Folder Structure

```
Job-Search-OS/
├── README.md                               ← You are here
├── 1-Profile/
│   ├── YOUR_context.md                     ← Fill this in first (master context)
│   ├── YOUR_resume_data_compact.md         ← Fill this in second (compact AI lookup)
│   └── README.md                           ← Instructions for profile setup
├── 2-Resume/
│   ├── template/
│   │   ├── resume_template.tex             ← LaTeX template (replace header with your info)
│   │   └── build.sh                        ← Compile script
│   ├── prompts/
│   │   ├── prompt.md                       ← Full resume generation prompt
│   │   └── prompt_compact.md               ← Fast version (recommended)
│   └── output/                             ← Generated resumes go here
├── 3-Outreach/
│   ├── email_prompt.md                     ← AI prompt for cold email generation
│   ├── cold_email_sequence.md              ← 3-email sequence template
│   ├── OUTREACH_STRATEGY.md                ← Full outreach strategy guide
│   └── tracker_template.csv               ← Blank outreach tracker
├── 4-Company-Research/
│   ├── README.md                           ← How to run the scrapers
│   ├── scrape_series_a.py                  ← Scrape Series A startups
│   ├── scrape_series_b.py                  ← Scrape Series B startups
│   ├── scrape_seed.py                      ← Scrape Seed/Pre-Seed startups
│   ├── scrape_yc.py                        ← Scrape YC companies
│   ├── enrich_and_score.py                 ← Score companies by fit
│   ├── FUNDING_STAGE_SCRAPE_PLAYBOOK.md    ← Full scraping playbook
│   └── requirements.txt                   ← Python dependencies
├── 5-Interview-Prep/
│   ├── prompts/
│   │   └── interview_prep_prompt.md        ← 8-phase prep generator
│   ├── stories/
│   │   ├── story_prompt.md                 ← AI prompt for structuring your stories
│   │   ├── YOUR_behavioral_stories.yaml    ← Your STAR story bank (fill in)
│   │   └── behavioral_questions.md         ← 32 master behavioral questions
│   └── prep/
│       └── research_template.md            ← 53-question company research template
└── 6-Strategy/
    ├── PLAYBOOK.md                         ← Rule of Three + channel data
    └── DAILY_OPS.md                        ← Morning ritual + daily workflow
```
