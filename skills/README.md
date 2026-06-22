# Skills — Claude Code Slash Commands

These are Claude Code slash commands for every major workflow in Job Search OS.

Instead of manually pasting prompts + context into Claude, you run a command and Claude handles the rest — reading your profile, applying the right prompt, and producing the output.

---

## Activate

Copy the skills into your workspace's `.claude/commands/` folder:

```bash
mkdir -p ~/my-job-search/.claude/commands
cp skills/*.md ~/my-job-search/.claude/commands/
```

Then open Claude Code inside your workspace and the commands are live.

---

## Commands

| Command | What It Does |
|---|---|
| `/generate-resume` | Reads your profile + a JD → outputs a tailored `.tex` resume |
| `/cold-email` | Reads your profile + company context → writes a personalized outreach email |
| `/interview-prep` | Reads your profile + story bank + a JD → generates 8-phase prep doc |
| `/build-stories` | Reads your profile → builds a STAR story bank in YAML |
| `/diagnose` | Asks 3 questions → identifies where your funnel is breaking and gives a protocol |
| `/negotiate-offer` | Walks through the offer, the comp breakdown, and drafts your actual ask |

---

## How They Work

Each skill reads from `1-Profile/YOUR_context.md` automatically — that's the shared context that makes everything coherent. Fill in your profile once and every skill draws from it.

You can pass context directly:

```
/generate-resume [paste JD here]
/cold-email Acme AI, Series A, building dev tools
/interview-prep [paste JD here]
```

Or run the command with no arguments and Claude will ask.
