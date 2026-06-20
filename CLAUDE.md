# Job Search OS — Claude Code Guide

This is **Job Search OS**, a terminal-first job search system with a CLI (`jsos`), AI prompts, LaTeX resume templates, company scrapers, and an outreach tracker.

---

## Install (do this first)

```bash
bash install.sh
```

That script checks for pipx (preferred) and falls back to a local venv. After it runs, `jsos` is available globally.

**Verify:**
```bash
jsos --version
jsos
```

**No pipx?** Install it first:
```bash
brew install pipx && pipx ensurepath   # macOS
```

---

## Set up your workspace

```bash
jsos init ~/my-job-search
cd ~/my-job-search
jsos
```

`jsos init` is interactive — it walks you through 4 steps and creates your workspace folder with all templates pre-filled.

---

## The workflow

```
jsos scrape --stage series-a   # pull companies from startups.gallery
jsos score  --stage series-a   # score them by fit (uses config.yaml)
jsos list                       # see your top targets
jsos track  --company "Acme" --status sent   # log outreach
jsos stats                      # pipeline stats + reply rate
```

Running `jsos` with no arguments inside your workspace shows a live dashboard of all of the above.

---

## Key files (after jsos init)

| File | What to do |
|---|---|
| `1-Profile/YOUR_context.md` | Fill this in first — every AI prompt reads from here |
| `config.yaml` | Set scoring weights, target industries, company size |
| `2-Resume/prompts/prompt_compact.md` | Paste into Claude + a JD → get a tailored resume |
| `3-Outreach/email_prompt.md` | Paste into Claude + a JD → get a cold email |
| `5-Interview-Prep/prompts/interview_prep_prompt.md` | Paste into Claude + a JD → get 8-phase prep |

---

## Tab completion (optional)

```bash
jsos completion     # prints the line to add to ~/.zshrc or ~/.bashrc
```

---

## If you're helping the user get set up

1. Run `bash install.sh` first
2. Ask them where they want their workspace (`jsos init <path>`)
3. Help them fill in `1-Profile/YOUR_context.md` — ask about their background, target roles, industries, and what they're looking for
4. Help them configure `config.yaml` — scoring weights should match their profile
5. Run `jsos scrape --stage series-a` to pull the first batch of companies
6. Run `jsos score` and `jsos list` to see their top targets
