import csv
import importlib.resources
import os
import shutil
import subprocess
import sys
from pathlib import Path

import click

from jsos.config import get_data_dir, get_research_dir


STAGE_SCRIPTS = {
    "series-a": "scrape_series_a.py",
    "series-b": "scrape_series_b.py",
    "seed":     "scrape_seed.py",
    "yc":       "scrape_yc.py",
}

STAGE_OUTPUT = {
    "series-a": "startups_gallery_series_a.csv",
    "series-b": "startups_gallery_series_b.csv",
    "seed":     "startups_gallery_seed.csv",
    "yc":       "startups_gallery_yc.csv",
}

BANNER = """\
\033[1m
     ██╗███████╗ ██████╗ ███████╗
     ██║██╔════╝██╔═══██╗██╔════╝
     ██║███████╗██║   ██║███████╗
██   ██║╚════██║██║   ██║╚════██║
╚█████╔╝███████║╚██████╔╝███████║
 ╚════╝ ╚══════╝ ╚═════╝ ╚══════╝
\033[0m\033[2m  Job Search OS — terminal-first job search\033[0m
"""

G  = "\033[32m✓\033[0m"   # green check
X  = "\033[31m✗\033[0m"   # red cross
AR = "\033[33m→\033[0m"   # yellow arrow (next action)
DIM = "\033[2m"
BOLD = "\033[1m"
CYAN = "\033[36m"
RESET = "\033[0m"


def _csv_row_count(path: Path) -> int:
    with open(path, encoding="utf-8-sig") as f:
        return max(0, sum(1 for _ in f) - 1)


def _workspace_summary() -> dict | None:
    """Return a dict of workspace state, or None if not in a workspace."""
    try:
        from jsos.config import workspace_root
        root = workspace_root()
    except Exception:
        return None

    data_dir = root / "data"
    summary = {
        "root": root,
        "profile_ok": (root / "1-Profile" / "YOUR_context.md").exists(),
        "config_ok": (root / "config.yaml").exists(),
        "stages": {},
        "shortlist_count": 0,
        "tracker": {"total": 0, "by_status": {}},
    }

    for stage, csv_name in STAGE_OUTPUT.items():
        scraped = data_dir / csv_name
        scored = data_dir / csv_name.replace(".csv", "_scored.csv")
        count = _csv_row_count(scraped) if scraped.exists() else 0
        summary["stages"][stage] = {
            "scraped": scraped.exists(),
            "scored": scored.exists(),
            "count": count,
        }

    shortlist = data_dir / "outreach_shortlist.csv"
    if shortlist.exists():
        summary["shortlist_count"] = _csv_row_count(shortlist)

    try:
        from jsos import tracker
        summary["tracker"] = tracker.stats()
    except Exception:
        pass

    return summary


def _print_status(s: dict) -> None:
    """Render the workspace dashboard."""
    root = s["root"]
    click.echo(f"\n  {BOLD}Workspace:{RESET}  {CYAN}{root}{RESET}\n")

    # ── Setup ─────────────────────────────────────────────────────────────────
    click.echo(f"{DIM}  ─── Setup {'─'*42}{RESET}")
    click.echo(f"  {G if s['profile_ok'] else X}  Profile       {DIM}1-Profile/YOUR_context.md{RESET}")
    click.echo(f"  {G if s['config_ok']  else X}  Config        {DIM}config.yaml{RESET}")

    # ── Data ──────────────────────────────────────────────────────────────────
    click.echo(f"\n{DIM}  ─── Data {'─'*44}{RESET}")
    any_scraped = any(v["scraped"] for v in s["stages"].values())
    for stage, info in s["stages"].items():
        if info["scraped"]:
            scored_tag = f"{DIM}· scored{RESET}" if info["scored"] else f"  \033[33mnot scored\033[0m  →  jsos score --stage {stage}"
            click.echo(f"  {G}  {stage:<12} {info['count']:>5} companies  {scored_tag}")
    if not any_scraped:
        click.echo(f"  {X}  No data scraped yet")
        click.echo(f"  {AR}  {BOLD}jsos scrape --stage series-a{RESET}")

    # ── Shortlist ─────────────────────────────────────────────────────────────
    click.echo(f"\n{DIM}  ─── Shortlist {'─'*39}{RESET}")
    sc = s["shortlist_count"]
    any_scored = any(v["scored"] for v in s["stages"].values())
    if sc > 0:
        click.echo(f"  {G}  {sc} companies above threshold")
        click.echo(f"  {AR}  {BOLD}jsos list{RESET}  to see them")
    elif any_scored:
        click.echo(f"  {X}  Shortlist empty — lower threshold in config.yaml")
    elif any_scraped:
        click.echo(f"  {X}  Not scored yet")
        click.echo(f"  {AR}  {BOLD}jsos score --stage series-a{RESET}")
    else:
        click.echo(f"  {DIM}—  Waiting for data{RESET}")

    # ── Outreach ──────────────────────────────────────────────────────────────
    click.echo(f"\n{DIM}  ─── Outreach {'─'*40}{RESET}")
    t = s["tracker"]
    total = t["total"]
    bs = t["by_status"]
    if total == 0:
        click.echo(f"  {X}  No outreach logged yet")
        click.echo(f"  {AR}  {BOLD}jsos track --company \"Acme\" --status sent{RESET}")
    else:
        sent     = bs.get("Sent", 0)
        replied  = bs.get("Replied", 0) + bs.get("Meeting Booked", 0)
        meetings = bs.get("Meeting Booked", 0)
        click.echo(f"  Sent {BOLD}{sent}{RESET}  ·  Replied {BOLD}{replied}{RESET}  ·  Meetings {BOLD}{meetings}{RESET}  ·  Total tracked {BOLD}{total}{RESET}")
        if sent > 0:
            click.echo(f"  Reply rate:  {BOLD}{replied/sent*100:.0f}%{RESET}   HM+ rate: {BOLD}{meetings/sent*100:.0f}%{RESET}")

    click.echo()


# ─── CLI group ────────────────────────────────────────────────────────────────

@click.group(invoke_without_command=True)
@click.version_option(package_name="jobsearchos")
@click.pass_context
def cli(ctx: click.Context):
    """Job Search OS — a terminal-first job search system."""
    if ctx.invoked_subcommand is not None:
        return

    click.echo(BANNER)
    s = _workspace_summary()
    if s:
        # Inside a workspace — show the live dashboard
        _print_status(s)
        click.echo(f"{DIM}  Run  jsos <command> --help  for details on any command.{RESET}\n")
    else:
        # No workspace — show how to get started
        click.echo(f"  {BOLD}Get started:{RESET}\n")
        click.echo(f"    {CYAN}jsos init{RESET} ~/my-job-search   ← set up your workspace")
        click.echo(f"    cd ~/my-job-search")
        click.echo(f"    {CYAN}jsos{RESET}                        ← see your dashboard\n")
        click.echo(f"  {DIM}Run  jsos --help  for all commands.{RESET}\n")


# ─── status ───────────────────────────────────────────────────────────────────

@cli.command()
def status():
    """Show a live dashboard of your workspace — data, shortlist, outreach."""
    click.echo(BANNER)
    s = _workspace_summary()
    if s is None:
        click.echo("  No workspace found in this directory or any parent.\n")
        click.echo(f"  {AR}  {BOLD}jsos init ~/my-job-search{RESET}\n")
        return
    _print_status(s)


# ─── init ─────────────────────────────────────────────────────────────────────

@cli.command()
@click.argument("path", default=None, required=False, type=click.Path())
@click.option("--force", is_flag=True, help="Overwrite existing files.")
def init(path: str | None, force: bool):
    """Set up a new Job Search OS workspace (interactive)."""
    click.echo(BANNER)

    # Step 1: location
    click.echo(f"{BOLD}Step 1 of 4 — Choose your workspace location{RESET}")
    click.echo("  This is the folder where your entire job search will live.\n")
    if path is None:
        path = click.prompt("  Workspace path", default="~/job-search", show_default=True)

    dest = Path(path).expanduser().resolve()
    dest.mkdir(parents=True, exist_ok=True)
    click.echo(f"\n  {G}  {dest}\n")

    # Copy templates
    try:
        pkg = importlib.resources.files("jsos") / "templates"
        templates_dir = Path(str(pkg))
    except Exception:
        templates_dir = None
    if templates_dir is None or not templates_dir.exists():
        templates_dir = Path(__file__).parent / "templates"
    if not templates_dir.exists():
        raise click.ClickException("Template directory not found. Try reinstalling: pip install jobsearchos")

    copied = skipped = 0
    for src in templates_dir.rglob("*"):
        if src.name in {"__init__.py", "__pycache__"} or src.suffix == ".pyc":
            continue
        rel = src.relative_to(templates_dir)
        out = dest / rel
        if src.is_dir():
            out.mkdir(parents=True, exist_ok=True)
        else:
            if out.exists() and not force:
                skipped += 1
                continue
            out.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, out)
            copied += 1

    click.echo(f"  {G}  {copied} files scaffolded" + (f"  {DIM}({skipped} already existed){RESET}" if skipped else ""))

    # Step 2: profile
    click.echo(f"\n{BOLD}Step 2 of 4 — Fill in your profile{RESET}  {DIM}(most important step){RESET}")
    click.echo(f"  Every AI prompt in this system reads from one file:")
    click.echo(f"  {CYAN}{dest}/1-Profile/YOUR_context.md{RESET}\n")
    click.echo("  Open it and fill in: your background, target roles, industries,")
    click.echo("  skills, experience, and what you're looking for.\n")
    click.pause("  Press Enter when you're ready to continue...")

    # Step 3: config
    click.echo(f"\n{BOLD}Step 3 of 4 — Configure scoring preferences{RESET}")
    click.echo(f"  Scoring weights live here — no code changes needed:")
    click.echo(f"  {CYAN}{dest}/config.yaml{RESET}\n")
    click.echo("  Set: target industries, keywords, company size, work type,")
    click.echo("  and minimum score threshold.\n")
    click.pause("  Press Enter when ready...")

    # Step 4: go
    click.echo(f"\n{BOLD}Step 4 of 4 — Pull your first batch of companies{RESET}\n")
    click.echo(f"    {BOLD}cd {dest}{RESET}")
    click.echo(f"    {BOLD}jsos scrape --stage series-a{RESET}   ← pull Series A companies")
    click.echo(f"    {BOLD}jsos score  --stage series-a{RESET}   ← score them by fit")
    click.echo(f"    {BOLD}jsos list{RESET}                      ← see your top targets\n")
    click.echo("─" * 56)
    click.echo(f"  {G} {BOLD} Workspace ready.{RESET}  Full guide: {dest}/README.md")
    click.echo("─" * 56)


# ─── scrape ───────────────────────────────────────────────────────────────────

@cli.command()
@click.option(
    "--stage",
    type=click.Choice(["series-a", "series-b", "seed", "yc"]),
    default="series-a",
    show_default=True,
    help="Funding stage to scrape from startups.gallery.",
)
def scrape(stage: str):
    """Scrape companies from startups.gallery by funding stage.

    \b
    Examples:
        jsos scrape --stage series-a
        jsos scrape --stage seed
    """
    research_dir = get_research_dir()
    data_dir = get_data_dir()
    script = research_dir / STAGE_SCRIPTS[stage]
    if not script.exists():
        raise click.ClickException(f"Scraper not found: {script}")

    output_name = STAGE_OUTPUT[stage]
    data_dir.mkdir(exist_ok=True)

    click.echo(f"\n  Scraping {BOLD}{stage.replace('-', ' ').title()}{RESET} companies from startups.gallery...\n")

    result = subprocess.run([sys.executable, str(script)], cwd=str(research_dir))

    if result.returncode != 0:
        raise click.ClickException("Scraper failed. See output above.")

    scraped = research_dir / output_name
    dest = data_dir / output_name
    if scraped.exists():
        scraped.rename(dest)
        count = _csv_row_count(dest)
        click.echo(f"\n  {G}  {count} companies saved → data/{output_name}")
    else:
        click.echo(f"\n  Warning: expected output not found at {scraped}")

    click.echo(f"\n  {AR}  Next:  {BOLD}jsos score --stage {stage}{RESET}\n")


# ─── score ────────────────────────────────────────────────────────────────────

@cli.command()
@click.option(
    "--stage",
    type=click.Choice(["series-a", "series-b", "seed", "yc"]),
    default="series-a",
    show_default=True,
    help="Stage CSV to score (must be scraped first).",
)
@click.option("--threshold", type=int, default=None, help="Override min score from config.yaml.")
def score(stage: str, threshold: int | None):
    """Score companies for fit using weights from config.yaml.

    \b
    Examples:
        jsos score --stage series-a
        jsos score --stage seed --threshold 7
    """
    from jsos import scorer
    from jsos.config import load as load_config

    input_csv = get_data_dir() / STAGE_OUTPUT[stage]
    if not input_csv.exists():
        raise click.ClickException(
            f"No scraped data found for {stage}.\n"
            f"  {AR}  Run: jsos scrape --stage {stage}"
        )

    cfg = load_config()
    if threshold is not None:
        cfg.setdefault("scoring", {})["threshold"] = threshold

    click.echo(f"\n  Scoring {BOLD}{input_csv.name}{RESET}...")
    scored = scorer.run(input_csv)

    if not scored:
        click.echo("  No companies found in CSV.")
        return

    scfg = cfg.get("scoring", {})
    thresh = threshold or scfg.get("threshold", 6)
    shortlist   = [r for r in scored if r["alignment_score"] >= thresh]
    top_targets = [r for r in scored if r.get("priority") == "Top Target"]
    high        = [r for r in scored if r.get("priority") == "High"]
    medium      = [r for r in scored if r.get("priority") == "Medium"]

    click.echo(f"\n  {G}  Scored {BOLD}{len(scored)}{RESET} companies\n")
    click.echo(f"  {'Top Target':<14} {BOLD}{len(top_targets)}{RESET}")
    click.echo(f"  {'High':<14} {BOLD}{len(high)}{RESET}")
    click.echo(f"  {'Medium':<14} {BOLD}{len(medium)}{RESET}")
    click.echo(f"\n  Shortlist (score ≥ {thresh}):  {BOLD}{len(shortlist)} companies{RESET}")
    click.echo(f"  {DIM}data/{input_csv.stem}_scored.csv{RESET}")
    click.echo(f"  {DIM}data/outreach_shortlist.csv{RESET}")
    click.echo(f"\n  {AR}  Next:  {BOLD}jsos list{RESET}\n")


# ─── list ─────────────────────────────────────────────────────────────────────

@cli.command(name="list")
@click.option("--min-score", type=int, default=6, show_default=True, help="Minimum alignment score.")
@click.option("--limit", type=int, default=25, show_default=True, help="Max rows to show.")
@click.option("--stage", type=click.Choice(["series-a", "series-b", "seed", "yc"]),
              default=None, help="Show from a specific stage's scored CSV.")
def list_companies(min_score: int, limit: int, stage: str | None):
    """Show your top target companies from the shortlist.

    \b
    Examples:
        jsos list
        jsos list --min-score 8
        jsos list --limit 50 --stage seed
    """
    if stage:
        csv_path = get_data_dir() / (STAGE_OUTPUT[stage].replace(".csv", "_scored.csv"))
    else:
        csv_path = get_data_dir() / "outreach_shortlist.csv"

    if not csv_path.exists():
        raise click.ClickException(
            f"No shortlist found.\n"
            f"  {AR}  Run: jsos scrape --stage series-a  then  jsos score"
        )

    with open(csv_path, encoding="utf-8-sig") as f:
        rows = list(csv.DictReader(f))

    filtered = [r for r in rows if int(r.get("alignment_score", 0)) >= min_score][:limit]

    if not filtered:
        click.echo(f"\n  No companies with score ≥ {min_score}.")
        click.echo(f"  {AR}  Try lowering --min-score or updating config.yaml\n")
        return

    click.echo(f"\n{'#':>4}  {'Company':<28} {'Score':>5}  {'Priority':<12}  {'Role':<20}  {'Size':<8}  Location")
    click.echo("─" * 110)
    for i, r in enumerate(filtered, 1):
        score_val = r.get("alignment_score", "?")
        priority  = r.get("priority", "")
        role      = r.get("suggested_role", "")[:20]
        size      = r.get("company_size", "")
        loc       = (r.get("location") or "")[:28]
        name      = r.get("company_name", "")[:27]
        p_color   = BOLD if priority == "Top Target" else ""
        click.echo(f"{i:>4}  {p_color}{name:<28}{RESET} {score_val:>4}/12  {priority:<12}  {role:<20}  {size:<8}  {loc}")

    click.echo(f"\n  Showing {BOLD}{len(filtered)}{RESET} companies  (score ≥ {min_score})")
    click.echo(f"  {AR}  Next:  {BOLD}jsos track --company \"<name>\" --status sent{RESET}\n")


# ─── stats ────────────────────────────────────────────────────────────────────

@cli.command()
def stats():
    """Show your outreach pipeline — status breakdown and reply rates."""
    from jsos import tracker

    data = tracker.stats()
    total = data["total"]
    by_status = data["by_status"]

    if total == 0:
        from jsos.config import get_tracker_csv
        click.echo(f"\n  No outreach logged yet.")
        click.echo(f"  Tracker: {DIM}{get_tracker_csv()}{RESET}")
        click.echo(f"  {AR}  {BOLD}jsos track --company \"Acme\" --status sent{RESET}\n")
        return

    click.echo(f"\n  {BOLD}Outreach Pipeline{RESET} — {total} companies tracked\n")
    click.echo(f"  {'Status':<20} {'Count':>5}  Bar")
    click.echo("  " + "─" * 48)

    order = ["Sent", "Replied", "Meeting Booked", "No Response", "Rejected", "Not Started"]
    for s in order:
        count = by_status.get(s, 0)
        if count == 0:
            continue
        bar = "█" * min(count, 36)
        click.echo(f"  {s:<20} {BOLD}{count:>5}{RESET}  {bar}")

    for s, count in by_status.items():
        if s not in order:
            click.echo(f"  {s:<20} {BOLD}{count:>5}{RESET}  {'█' * min(count, 36)}")

    sent     = by_status.get("Sent", 0)
    replied  = by_status.get("Replied", 0) + by_status.get("Meeting Booked", 0)
    meetings = by_status.get("Meeting Booked", 0)
    click.echo()
    if sent > 0:
        click.echo(f"  Reply rate  {BOLD}{replied/sent*100:.0f}%{RESET}  ({replied}/{sent})")
    if replied > 0:
        click.echo(f"  HM+ rate    {BOLD}{meetings/replied*100:.0f}%{RESET}  ({meetings}/{replied})")
    click.echo()


# ─── track ────────────────────────────────────────────────────────────────────

@cli.command()
@click.option("--company", required=True, help="Company name (must match tracker).")
@click.option(
    "--status",
    required=True,
    type=click.Choice(["sent", "replied", "meeting", "no-response", "rejected"], case_sensitive=False),
    help="New outreach status.",
)
def track(company: str, status: str):
    """Update a company's outreach status in the tracker.

    \b
    Examples:
        jsos track --company "Stripe" --status sent
        jsos track --company "Notion" --status replied
        jsos track --company "Linear" --status meeting
    """
    from jsos import tracker

    status_map = {
        "sent":        "Sent",
        "replied":     "Replied",
        "meeting":     "Meeting Booked",
        "no-response": "No Response",
        "rejected":    "Rejected",
    }
    canonical = status_map[status.lower()]
    found = tracker.update_status(company, canonical)
    if found:
        click.echo(f"\n  {G}  {BOLD}{company}{RESET} → {canonical}\n")
    else:
        click.echo(f"\n  {X}  Company not found: '{company}'")
        click.echo(f"  {AR}  Name must match exactly. Run {BOLD}jsos stats{RESET} to see tracked companies.\n")


# ─── completion ───────────────────────────────────────────────────────────────

@cli.command()
@click.option("--shell", type=click.Choice(["zsh", "bash", "fish"]), default=None,
              help="Shell to generate completion for (auto-detected if omitted).")
def completion(shell: str | None):
    """Print shell tab-completion setup instructions.

    \b
    After running this, restart your shell or source your profile.
    Tab completion lets you do:  jsos sc[TAB] → jsos scrape
    """
    if shell is None:
        detected = Path(os.environ.get("SHELL", "")).name
        shell = detected if detected in {"zsh", "bash", "fish"} else "zsh"

    click.echo(f"\n  {BOLD}Tab completion for {shell}{RESET}\n")

    if shell == "zsh":
        click.echo(f"  Add this line to {CYAN}~/.zshrc{RESET}:\n")
        click.echo(f'    eval "$(_JSOS_COMPLETE=zsh_source jsos)"\n')
        click.echo(f"  Then:  {BOLD}source ~/.zshrc{RESET}\n")
    elif shell == "bash":
        click.echo(f"  Add this line to {CYAN}~/.bashrc{RESET}:\n")
        click.echo(f'    eval "$(_JSOS_COMPLETE=bash_source jsos)"\n')
        click.echo(f"  Then:  {BOLD}source ~/.bashrc{RESET}\n")
    elif shell == "fish":
        click.echo(f"  Add this line to {CYAN}~/.config/fish/config.fish{RESET}:\n")
        click.echo(f'    eval (env _JSOS_COMPLETE=fish_source jsos)\n')
        click.echo(f"  Then restart fish.\n")


if __name__ == "__main__":
    cli()
