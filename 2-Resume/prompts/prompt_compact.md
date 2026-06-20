# Resume from JD — Compact Flow

**Workflow:** When given a job description, **do not create a separate spec file**. Use the intake and rules below to decide role type, preset, section plan, and bullets, then **go directly to writing** the `.tex` file and compile the PDF.

**Canonical sources:**
- **Content:** `YOUR_context.md` — metrics, bullets, placement rules, and all narrative. Single source of truth.
- **Layout/template:** `resume_template.tex` — preamble, geometry, `\expEntry`/`\eduEntry`, section spacing. Start every new resume from this file.
- **Quick reference (optional):** `YOUR_resume_data_compact.md` — faster lookup; conflicts resolved by YOUR_context.md.

**Bullet punctuation:** Do **not** end resume bullets with a period. No trailing punctuation on any bullet line.

**Header/ATS contact:** Use plain separators (`\textbar{}`) between contact items. No math symbols in the contact line.

**Link styling:** Style email, LinkedIn, portfolio URL, and any company/product names with underline + black text: `\underline{\href{URL}{\color{black}display text}}`

---

## Step 0: JD Intake (fill first)

| Field | Value |
|---|---|
| Role Type | [e.g., AI_PM / Enterprise_SaaS_PM / CS / Product_Ops / Other] |
| Spacing Preset | Fill / Standard / Dense |
| Top 5 JD Keywords | [list exactly from JD] |
| Section Plan | [see Section Plans below] |
| Lead Bullet Theme | [one phrase, e.g., "operator workflows" / "customer journey" / "0-to-1 product"] |

---

## Section Plans (Pick One)

Define your section plans in `YOUR_context.md`. The table below is an example — replace with your own company names and role types.

| Role Type | Section Plan |
|---|---|
| AI_PM | [Startup/Venture](2) + [Company A](3) + [Company B](1) + [Side Project](1) |
| Enterprise_SaaS_PM | [Startup/Venture](2) + [Company A](3–4) + [Company B](2) + [Side Project](1) |
| CS | [Startup/Venture](2) + [Company A](4) + [Company B](1) + [Side Project](1) |
| Product_Ops | [Startup/Venture](2) + [Company A](4) + [Company B](2) + [Side Project](1) |

Rules:
- More bullets per entry = Dense preset
- Standard or Fill when fewer entries
- If you have a promotion/two roles at one company, use `\expEntry{}{}` second-role format for the second entry

---

## Spacing Presets

| Preset | `\titlespacing` | `itemsep` | `topsep` | Entry vspace |
|---|---|---|---|---|
| Fill | 7pt/4pt | 2pt | 2pt | 4pt |
| Standard | 5pt/2pt | 0pt | 1pt | 2pt |
| Dense | 4pt/1pt | -1pt | 0pt | 1pt |

**Every new resume:** After drafting content, adjust vertical spacing so the one-page PDF looks full with no large blank band at the bottom, while keeping symmetric geometry (`left` = `right`, `top` = `bottom`). Recompile and verify before handing off.

---

## Bullet Choices (by Label from YOUR_context.md)

Pick the number of bullets per entry from your Section Plan. Output as: `Company: [Label1, Label2, ...]`.

For each role in your context file, you defined labeled bullets. Reference them by label — the AI selects the best subset for the JD and role type.

**Selection rules:**
- Always prioritize bullets whose outcome directly addresses a top JD priority
- Never repeat the same metric or achievement twice in the same resume
- Lead the first bullet of the most prominent role with the strongest metric for this JD
- Prefer impact metrics (cost savings, adoption, revenue) over process metrics (interviews, surveys) as lead bullets

---

## Writing Rules

### No Hallucinations
Never invent roles, companies, metrics, or dates. If a metric is not in `YOUR_context.md`, do not use it.

### Professional Summary — 2 Sentences
- Sentence 1: Lead with impact metrics + context
- Sentence 2: Include your degree and background + what you bring to THIS role

Hook, not summary. The strongest signal first. Never lead with process metrics.

### Bullets
Strong Action Verb + What You Did + Quantified Impact. No trailing periods. Bold key numbers with `\textbf{}`.

### Page Fill
Adjust spacing presets until the page looks end-to-end full. No blank band at bottom.

---

## Output

Write the complete `.tex` file. Save as: `output/[your_name]_[company]_[role].tex`

Compile: `tectonic output/filename.tex`
