# Daily Operations

A concrete, repeatable daily workflow that keeps the system running.

---

## Morning Block (2–3 hours) — NON-NEGOTIABLE

This is the most important block of the day. Do it first.

### 1. Anchor Moment (1–2 min)
Close your eyes. Picture the feeling of having the job — what does life look like? What are you doing? What does it feel like to have made it through this stretch? Not the salary. The feeling.

Then open your eyes and start.

### 2. Music On
Put on something that helps you focus. This is a signal to your brain that the work has started.

### 3. Pick 5 Companies (15 min)
Open your scored outreach shortlist. Pick 5 companies:
- You find genuinely interesting (your personalization will show)
- Remote or hybrid first (unless you're targeting a city)
- Smallest team size for founding/early PM roles
- Haven't contacted yet (check `do_not_contact.csv`)

### 4. For Each Company: Find Email → Generate Email → Send (10–12 min each)
For each of the 5 companies:
1. Find the founder's name on their website (About/Team page)
2. Find their email via Apollo.io (free: 50 credits/month)
3. Open Claude → paste `email_prompt.md` + `YOUR_context.md` + the JD/company description
4. Copy the generated bullets → fill in the 3 manual fields (first name, personalization line, bullets)
5. Send
6. Log in `tracker_template.csv` with status "Sent"

### 5. Track What You Sent (5 min)
Update the tracker. If you've hit a reply, move it to "Replied" and note whether it's positive.

---

## Afternoon Block (1 hour)

### 6. Opportunistic Emails (30 min)
Any interesting companies you came across today — LinkedIn, Twitter/X, newsletters, conversations? Send them today, not later. These are bonus reps and often the best ones.

### 7. Applications (30 min — hard cap)
5 applications via ATS. This is not your primary pipeline — it's a background habit. Don't let this expand beyond 30 min. Stop at 5 applications regardless of how many you've found.

---

## Weekly Cadence

### Monday
- Review last week's reply rate and HM calls booked
- If reply rate < 30%: tweak the email (subject line, personalization hook, or lead bullet)
- If HM calls < 2: check if you're reaching the right people (founders vs. HR vs. wrong company)
- Queue up Track 3 (big company) emails for the week

### Sunday
- Batch and send Track 3 emails (so they hit inboxes Monday morning)
- Refresh your scored shortlist if running low on companies
- Run the scraper for a new funding stage if needed

---

## Trigger Rules

### When to refresh the company list
- Shortlist has fewer than 20 companies remaining
- You've been sending for 3+ weeks from the same stage
→ Run `scrape_[stage].py` + `enrich_and_score.py` to add a new batch

### When to tweak the email
- Reply rate < 30% after 50+ sends
- HM+ rate < 40% of replies
→ Change one variable at a time: subject line first, then personalization line, then bullets

### When to add a new track
- Current tracks are running smoothly AND you want more volume
→ Add Track 3 if you haven't started it yet

### When NOT to change the strategy
- You've been running for less than 2 weeks
- You're getting replies but just not enough (keep sending, it's a numbers game)
- You're distracted by a shiny new tactic you read about

---

## Key Metrics Dashboard

Track these weekly:

| Metric | Target | How to Track |
|---|---|---|
| Emails sent (Track 1) | 25/day, 125/week | Tracker CSV |
| Reply rate | 30–50% | (Replies / Sent) × 100 |
| HM+ rate from replies | 50%+ | (HM calls / Replies) × 100 |
| HM calls booked | 2+/week | Calendar or tracker |
| Active rounds | Track count | Running list |
| Offers in progress | Track count | Running list |

If HM calls booked ≥ 2/week, the system is working. Don't change it.

---

## What "Done" Looks Like Each Day

- [ ] 25 Track 1 emails sent
- [ ] All 25 logged in tracker
- [ ] 5 Track 2 (opportunistic) emails sent (if found)
- [ ] 5 ATS applications submitted
- [ ] Reply queue cleared (every reply gets same-day or next-morning response)
- [ ] Track 3 batch queued (Sunday only)

If you do this for 4 weeks straight, you'll have:
- ~500 Track 1 emails sent
- ~200–250 replies (at 40–50%)
- ~30–50 HM/founder calls
- Multiple active interview rounds

That's the pipeline you need.
