# Job Search OS

[![Stars](https://img.shields.io/github/stars/mukeshbasvekar/Job-Search-OS?style=flat-square)](https://github.com/mukeshbasvekar/Job-Search-OS/stargazers)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=flat-square)](LICENSE)

> Most job searches fail not from lack of effort — but from lack of system.

I spent multiple months job searching the right way: cold emails to founders, a tailored resume for every JD, deep interview prep from scratch each time. I built tooling to stop doing it manually. **It worked.** This is that system, open-sourced.

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

## The 4Ps — How This System Thinks

Every tool in this repo maps to one of four principles. When something isn't working, one of these four is broken.

| Principle | What It Means | Where It Lives |
|---|---|---|
| **Protect** | Guard your mental state — rejection is structural, not personal | `6-Strategy/DAILY_OPS.md` |
| **Pipeline** | Keep enough in motion that one silent process never stalls you | `3-Outreach/` · `4-Company-Research/` |
| **Prove** | Specific proof beats generic claims — on paper and in the room | `2-Resume/` · `5-Interview-Prep/` |
| **Prep** | Segment → Target → Position. Know your material cold before you're in it | `1-Profile/` · `6-Strategy/PLAYBOOK.md` |

Read [PHILOSOPHY.md](PHILOSOPHY.md) for the full reasoning. It's the why behind every tool in here — worth 20 minutes before you start.

---

## What's Inside

| Module | What It Does |
|---|---|
| [1-Profile](1-Profile/) | Your single source of truth — fill this in once, everything else draws from it |
| [2-Resume](2-Resume/) | AI-powered LaTeX resume generation tailored to any job description |
| [3-Outreach](3-Outreach/) | Cold email system — 3-email sequence, AI prompt, strategy, tracker |
| [4-Company-Research](4-Company-Research/) | Python scrapers for startups.gallery (Series A/B/Seed/YC) + fit scoring |
| [5-Interview-Prep](5-Interview-Prep/) | 8-phase prep system, story bank, 53-question company research template |
| [6-Strategy](6-Strategy/) | The full playbook — Rule of Three, channel data, daily ops ritual |
| [7-Situations](7-Situations/) | When you're stuck — diagnostic guides for every funnel breakdown |
| [PHILOSOPHY.md](PHILOSOPHY.md) | The 4Ps framework — the mental model that holds the whole system together |

---

## Install

```bash
# Clone and install:
git clone https://github.com/mukeshbasvekar/Job-Search-OS.git
cd Job-Search-OS
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

Open `config.yaml` and set your preferences once. Scoring weights, target industries, company size — all there. No code changes needed.

---

## Setup (30 Minutes)

### Step 1 — Fill in your profile (20 min)
Open [1-Profile/YOUR_context.md](1-Profile/YOUR_context.md) and fill in every section. **This is the most important step.** Every AI prompt in this system reads from this file.

Then fill in [1-Profile/YOUR_resume_data_compact.md](1-Profile/YOUR_resume_data_compact.md) — a faster-lookup version for AI.

### Step 2 — Set up your resume template (5 min)
Open [2-Resume/template/resume_template.tex](2-Resume/template/resume_template.tex) and replace the placeholder header with your real name, email, LinkedIn, and portfolio URL.

Install [Tectonic](https://tectonic-typesetting.github.io/) (LaTeX compiler):
```bash
brew install tectonic   # macOS
```

### Step 3 — Configure the resume prompt (3 min)
Read through [2-Resume/prompts/prompt_compact.md](2-Resume/prompts/prompt_compact.md). The prompts reference `YOUR_context.md` — no file path changes needed as long as you're giving both to your AI.

### Step 4 — Set up the outreach tracker (2 min)
Copy [3-Outreach/tracker_template.csv](3-Outreach/tracker_template.csv) → rename to `outreach_tracker.csv`. This is where every company you contact gets logged.

---

## How to Use Each Module

### Generating a Tailored Resume
1. Find a job description
2. Open a new chat with Claude (or GPT-4o)
3. Paste: `2-Resume/prompts/prompt_compact.md` + `1-Profile/YOUR_context.md` + the JD
4. AI generates a production-ready `.tex` file tailored to that role
5. Compile: `tectonic output/your_resume.tex`

### Writing a Cold Email
1. Find a company + founder email (Apollo.io free tier works)
2. Open a new chat with Claude
3. Paste: `3-Outreach/email_prompt.md` + `1-Profile/YOUR_context.md` + the JD or role description
4. AI generates a personalized 3-bullet cold email
5. Send Email 1 manually, automate Email 2 and 3 as follow-ups

### Sourcing Companies to Email
1. Run the scrapers in `4-Company-Research/` to pull fresh startup data
2. Run `enrich_and_score.py` to score companies by fit with your background
3. Export the shortlist and work it top-down

### Preparing for an Interview
1. Open a new chat with Claude
2. Paste: `5-Interview-Prep/prompts/interview_prep_prompt.md` + `1-Profile/YOUR_context.md` + your behavioral stories YAML + the JD
3. AI generates an 8-phase prep doc: role decode, company research, narrative, behavioral prep, questions to ask, objections, logistics, thank-you email

### When You're Stuck
Open [7-Situations/WHEN_STUCK.md](7-Situations/WHEN_STUCK.md). It has a three-question diagnostic that tells you exactly where your funnel is breaking — no replies, replies but no meetings, meetings but no offers, or something else. Each situation has a specific protocol.

If you're getting objections in interviews, [7-Situations/OBJECTION_PLAYBOOK.md](7-Situations/OBJECTION_PLAYBOOK.md) covers every common one: experience gaps, short tenures, career pivots, comp conversations, and more. The structure is always: **acknowledge → reframe → redirect to evidence.**

---

## The Philosophy

The full version is in [PHILOSOPHY.md](PHILOSOPHY.md). The short version:

Most searches fail because effort is pointed in the wrong direction. People spend 80% of their time on ATS applications (low leverage) and 20% on everything else. They write generic emails. They prepare generic answers. They stop sending when one process gets interesting — then have nothing when that process goes quiet.

This system inverts that:

- **Cold email to founders** is the highest-leverage channel. 2–3× better conversion than job boards.
- **Every resume is rebuilt for the JD** — not tweaked, rebuilt — in under 10 minutes with AI.
- **Interview prep predicts questions** before they're asked, based on the JD, company stage, and role type.
- **The pipeline runs even when you have active interviews** — so a quiet process doesn't stall the whole search.
- **When something breaks**, `7-Situations/` tells you exactly where and what to fix.

The 4Ps — Protect, Pipeline, Prove, Prep — are a check you can run on yourself at any time. If all four are healthy, the outcome follows.

---

## What You'll Need

- **AI:** Claude (claude.ai or Claude Code) or GPT-4o — paste prompts + context files into either
- **LaTeX compiler:** [Tectonic](https://tectonic-typesetting.github.io/) (recommended) or `pdflatex`
- **Python 3.8+:** For the company scrapers
- **Apollo.io (free tier):** 50 email lookups/month — enough for 50 cold emails
- **Google Sheets or Excel:** For the outreach tracker

---

## Folder Structure

```
Job-Search-OS/
├── PHILOSOPHY.md                           ← Read this first — the 4Ps framework
├── README.md                               ← You are here
├── config.yaml                             ← Scoring weights + targeting preferences
├── install.sh                              ← One-command install
├── 1-Profile/
│   ├── YOUR_context.md                     ← Fill this in first (master AI context)
│   ├── YOUR_resume_data_compact.md         ← Fill this in second (compact lookup)
│   └── README.md                           ← Profile setup instructions
├── 2-Resume/
│   ├── template/
│   │   ├── resume_template.tex             ← LaTeX template (replace header)
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
│   ├── scrape_series_a.py                  ← Scrape Series A startups
│   ├── scrape_series_b.py                  ← Scrape Series B startups
│   ├── scrape_seed.py                      ← Scrape Seed/Pre-Seed startups
│   ├── scrape_yc.py                        ← Scrape YC companies
│   ├── enrich_and_score.py                 ← Score companies by fit
│   ├── FUNDING_STAGE_SCRAPE_PLAYBOOK.md    ← Full scraping playbook
│   └── README.md                           ← How to run the scrapers
├── 5-Interview-Prep/
│   ├── prompts/
│   │   └── interview_prep_prompt.md        ← 8-phase prep generator
│   ├── stories/
│   │   ├── story_prompt.md                 ← AI prompt for structuring your stories
│   │   ├── YOUR_behavioral_stories.yaml    ← Your STAR story bank (fill in)
│   │   └── behavioral_questions.md         ← 32 master behavioral questions
│   └── prep/
│       └── research_template.md            ← 53-question company research template
├── 6-Strategy/
│   ├── PLAYBOOK.md                         ← Rule of Three + channel data
│   └── DAILY_OPS.md                        ← Morning ritual + daily workflow
└── 7-Situations/
    ├── WHEN_STUCK.md                       ← 3-question diagnostic + situation protocols
    └── OBJECTION_PLAYBOOK.md               ← Interview objection handling (acknowledge → reframe → evidence)
```
