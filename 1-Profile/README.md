# Profile Setup Guide

The profile folder is the foundation of the entire system. Every AI prompt in this system reads from these two files. Fill them in carefully — garbage in, garbage out.

---

## Files to Fill In

### YOUR_context.md (Primary — fill this first)

This is the **single source of truth** for everything: your experience, metrics, bullet bank, skills, and education.

Rules for filling it in:
- **Every metric must be real.** If you don't have a specific number, don't invent one. Use a range (e.g., "5–10 customers") or omit.
- **Be specific about scope.** "75% adoption of the prioritization feature" is better than "75% adoption." Precision matters — the AI will repeat what you write.
- **Write bullets in strong action verb format.** Start with Led / Built / Shipped / Drove / Delivered / Automated. Never start with "Responsible for" or "Helped."
- **Include a bullet bank per role.** The more labeled bullets you have per role, the better the AI can select and combine them for different JD types.

### YOUR_resume_data_compact.md (Secondary — fill after context.md)

A condensed version used for faster AI lookups. Derived from YOUR_context.md. When the two conflict, context.md wins.

---

## What Makes a Good Bullet

**Formula:** Strong Action Verb + What You Did + Quantified Business Impact

| Bad | Good |
|---|---|
| Responsible for managing customer relationships | Maintained 4.7/5.0 CSAT across 500+ customer interactions |
| Worked on product roadmap | Led roadmap and sprint planning for 10+ features across a team of 8 engineers |
| Helped reduce costs | Delivered $300K+ in cost savings by automating manual workflows for 40+ clients |
| Improved the onboarding process | Built an onboarding playbook that became the standard for 80+ accounts; cut inbound queries 30% |

**One idea per bullet.** Don't combine two achievements into one sentence.

**Lead with impact, not process.** "$600K+ in cost savings" > "50+ customer interviews."

---

## Metrics Table

Before writing bullets, fill in your metrics table. This forces precision upfront.

For each metric:
- What's the exact number or range?
- What company / role is this from?
- What exactly does it represent? (Don't inflate scope)

The AI will use these exact numbers. Over-precision is better than ambiguity.
