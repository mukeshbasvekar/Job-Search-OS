# [YOUR FULL NAME] — Master Context File

> This is the single source of truth for all AI prompts in this system.
> All resume bullets, email bullets, interview prep, and story references pull from here.
> Fill in every section. Replace all [PLACEHOLDERS] with your real data.
> Never invent metrics — use exact values, ranges, or omit.

---

## Metrics (Exact Values Only)

Fill in the metrics table before writing bullets. This is the canonical reference.
The AI will cite these numbers exactly — be precise about what each number represents.

| Source (Company) | Metric | Exact Value |
|---|---|---|
| [Company A] | [e.g., Cost savings delivered] | [e.g., $400K+] |
| [Company A] | [e.g., Reporting time before → after] | [e.g., 6 hours → 45 minutes] |
| [Company A] | [e.g., Accounts / clients managed] | [e.g., 80+ enterprise clients] |
| [Company A] | [e.g., Feature adoption] | [e.g., 70% adoption of [feature name]] |
| [Company A] | [e.g., Team managed] | [e.g., 6 engineers and designers] |
| [Company A] | [e.g., Features shipped] | [e.g., 8+ features] |
| [Company A] | [e.g., Query/ticket reduction] | [e.g., 30%] |
| [Company A] | [e.g., Revenue recovered] | [e.g., $40K+/year] |
| [Company B] | [e.g., Users] | [e.g., 2,000+ users] |
| [Company B] | [e.g., Completion / efficiency metric] | [e.g., 20% faster project completion] |
| [Company C] | [e.g., Signups / early traction] | [e.g., 300+ early signups] |
| [Side Project / Product] | [e.g., Lifetime users] | [e.g., 20,000+ users] |
| [Side Project / Product] | [e.g., MAU] | [e.g., 2,000+ MAUs] |
| [Education] | [e.g., Scholarship or award] | [e.g., Top 10% recipient] |

---

## Professional Identity

Who you are in one sentence — this is your cold email opening identity, not your job title.

> [YOUR_IDENTITY]: e.g., "I built [Product] — [what it does] — reached [traction/signups] through [method], and before that was [Role] at [Company] ([domain]) where I [top achievement]."

**Do NOT open with your degree or graduation.** Lead with what you built or delivered.

---

## Experience Sections + Bullet Bank

For each role, write the canonical one-line description and a labeled bullet bank.
The AI will select bullets by label and combine them for each JD.

---

### [Company A] | [Role Title] | [Month YYYY – Month YYYY]
*[One-line description: what the company does, domain, scale — e.g., "Enterprise cybersecurity SaaS, $X ARR, 80+ enterprise clients"]*

**Bullet bank (label: bullet text):**

- **Cost Savings / Automation**: [Strong verb] [what you automated] for [scope] — [quantified result].
- **Reporting / Speed**: Reduced [metric] from [before] to [after] for [scope] through [method].
- **Cross-functional Delivery**: Led roadmap and sprint planning for [X] features across a team of [N engineers/designers]; delivered on schedule.
- **Customer Advisory / Design Partner**: Structured a [design partner / advisory] program with [customer type]; translated [what you heard] into product changes and drove [adoption metric].
- **Self-Serve / Onboarding**: Built [dashboard / playbook / system] that became the standard for [N accounts]; reduced [inbound queries / support tickets] [X]%.
- **Revenue / Billing**: Recovered $[X]/year by [replacing / fixing / standardizing] [what broke].
- **Scope & Launch**: Shipped [integration / feature] in [X weeks] (vs. [Y-week] estimate) by scoping to the core customer job; retained [ARR % or client type].
- **Team / Stakeholder Alignment**: [What you aligned / who you aligned] → [outcome].

*(Add more bullets as needed. Label each one — labels are how the AI selects them.)*

---

### [Company B] | [Role Title 1] | [Month YYYY – Month YYYY]
*[One-line description]*

**Bullet bank:**

- **[Label]**: [Bullet text].
- **[Label]**: [Bullet text].
- **[Label]**: [Bullet text].

### [Company B] | [Role Title 2 — if promoted/second role] | [Month YYYY – Month YYYY]
*[Same company, different role — use the `\expEntry{}{}` second-role format in LaTeX]*

**Bullet bank:**

- **[Label]**: [Bullet text].
- **[Label]**: [Bullet text].

---

### [Startup / Side Venture] | [Founder / PM / Builder] | [Month YYYY – Present]
*[What you built, for whom, why it matters — include any traction/signups]*

**Bullet bank:**

- **0-to-1 Ownership**: Defined and shipped [product] from concept through launch as [role] — discovery, [key technical work], and go-to-market.
- **AI / Technical**: Built [technical system — e.g., agent orchestration, LLM integration, recommendation engine] that [achieved X].
- **Market Validation**: Ran customer discovery and [method]; drove [N] early signups to validate demand before committing to full build.
- **Product Launch**: Owned full product lifecycle — [market sizing / architecture / engineering coordination / GTM planning].

---

### [Company C] | [Role Title] | [Month YYYY – Month YYYY]
*[One-line description]*

**Bullet bank:**

- **[Label]**: [Bullet text].
- **[Label]**: [Bullet text].

---

### [Side Project / Product] | [Creator / Builder] | [YYYY – Present]
*[What it is, who it's for, scale]*

**Bullet bank:**

- **Growth**: Grew [product] to [N]+ users and [N]+ MAUs through [method].
- **Engagement**: [What you built or changed] that increased [metric] [X]%.

---

## Section Plans (for Resume Prompt)

When giving a JD to the resume AI, it will ask for a section plan. Define yours here based on role types you're targeting:

| Role Type | Section Plan (entries × bullets) |
|---|---|
| [e.g., AI/Technical PM] | [Company A](2) + [Company B](3) + [Startup](2) + [Side Project](1) |
| [e.g., Enterprise SaaS PM] | [Company A](3–4) + [Company B](2) + [Startup](2) + [Side Project](1) |
| [e.g., Customer Success] | [Company A](4) + [Company B](2) + [Startup](2) + [Side Project](1) |
| [e.g., Product Ops] | [Company A](4) + [Company B](2) + [Startup](2) + [Side Project](1) |

---

## Education

| Institution | Degree | Dates | Notable |
|---|---|---|---|
| [University] | [Degree, e.g., MS Engineering Management] | [Month YYYY] | [e.g., Merit scholarship — top X%, key coursework, extracurriculars] |
| [University] | [Degree, e.g., BS Computer Engineering] | [Month YYYY] | [e.g., Leadership, honors, projects] |

---

## Skills & Competencies

Fill in your skills categories. These go directly into the LaTeX Skills section.

- **Product**: [e.g., Product roadmap, sprint planning, PRDs, user research, A/B testing, prioritization frameworks]
- **Technical**: [e.g., SQL, Python, REST APIs, LLMs, prompt engineering, Jira, Figma]
- **AI/ML**: [e.g., Agent orchestration, vector DBs, RAG, tool-calling, LLM fine-tuning]
- **Operations**: [e.g., Process design, workflow automation, SOPs, CRM, customer success]
- **Analytics**: [e.g., Amplitude, Google Analytics, Mixpanel, Excel, Looker]
- **Tools**: [Jira, Figma, Notion, Confluence, Cursor, Claude Code, etc.]
- **Languages**: [e.g., Fluent in English and [Language X]]

---

## Cold Email Identity

This is the fixed intro block that goes in every cold email. Fill it in once.

> "I [built / led] [Product/Company] — [one-line description] — reached [traction] through [method], and before that was [Role] at [Company] ([domain]) where I [top achievement]. Here's why I think I'd be useful at [Company]:"

**Rules for bullets in cold email (same as resume):**
- One idea per bullet, one bold number, ~15 words, lead with outcomes not process
- JD-first: each bullet maps to one of the role's top 3 JD priorities
- Never start a bullet with "I"
- Never use generic phrases like "passionate about your mission"

---

## Behavioral Stories (Quick Reference)

List your key STAR stories here as one-liners. Full YAML format is in `5-Interview-Prep/stories/YOUR_behavioral_stories.yaml`.

| Story # | Company | Hook (one line) | Themes |
|---|---|---|---|
| 1 | [Company] | [e.g., Scoped 10-week project to 4 weeks, saved key client] | Decision under uncertainty, prioritization |
| 2 | [Company] | [e.g., Fixed QA conflict by introducing co-testing model] | Influence without authority, conflict |
| 3 | [Company] | [e.g., Assumed X, was wrong → pivoted → improved outcome] | Failure & learning |
| 4 | [Company] | [e.g., Identified root cause behind 30% support load, fixed it] | Ownership, first principles |
| 5 | [Company] | [e.g., Pushed for website revamp over product polishing — +15% conversion] | Data-driven direction change |
| 6 | [Company] | [e.g., Turned demanding enterprise client into design partner] | Customer obsession, difficult customer |

*(Add as many stories as you have — minimum 6, ideally 10+)*

---

## Framing Notes

Things the AI needs to know about how to frame your background:

- **What NOT to lead with**: [e.g., "I recently graduated" or your degree — lead with work instead]
- **What to always include in summaries**: [e.g., your master's degree and engineering background]
- **Titles to target vs. avoid**: [e.g., PM / Founding PM = yes; Sr. PM = no (lower callback rate)]
- **Your strongest proof points by role type**:
  - For PM: [e.g., $400K+ savings, 8-feature roadmap, 70% adoption]
  - For CS: [e.g., 4.7/5.0 CSAT, 500+ interactions, onboarding playbook]
  - For AI roles: [e.g., Built [specific system] with LLMs/agents/vector DBs]
