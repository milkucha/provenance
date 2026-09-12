#!/usr/bin/env python3
r"""
Append a run summary to LAB_REPORT.md based on SIMULATION_LOG.md.

Reads SIMULATION_LOG.md from a worktree, extracts basic setup facts, auto-determines
the next run number, and creates a template entry in LAB_REPORT.md with:
- Header: ### Run N — YYYY-MM-DD — worktree `name`
- Setup facts filled in from SIMULATION_LOG
- Placeholders for qualitative sections

Usage:
  py scripts/lore/simulate_record_run.py "<main_repo_root>" "<worktree_path>"

The script reads from:
  - <worktree_path>/SIMULATION_LOG.md (for setup info and tally data)
  - <main_repo_root>/LAB_REPORT.md (to find the next run number and insert point)

It writes to:
  - <main_repo_root>/LAB_REPORT.md (appends the new run entry)

Example:
  py scripts/lore/simulate_record_run.py \
    "C:\Users\milkucha\Desktop\DEV\PROJECTS\AI\Prov" \
    "C:\Users\milkucha\Desktop\DEV\PROJECTS\AI\Prov\.worktrees\simulate-20260911-120000"
"""

import sys
import re
from pathlib import Path
from datetime import datetime


def find_next_run_number(lab_report_path):
    """Find the highest run number in LAB_REPORT.md and return next."""
    content = lab_report_path.read_text(encoding='utf-8')
    run_numbers = re.findall(r'^### Run (\d+) —', content, re.MULTILINE)
    if run_numbers:
        return int(run_numbers[-1]) + 1
    return 1


def extract_setup_from_simulation_log(simulation_log_path):
    """Extract setup info from SIMULATION_LOG.md."""
    content = simulation_log_path.read_text(encoding='utf-8')

    setup = {
        'participants': None,
        'pass_count': None,
        'context': None,
        'model': None,
        'worktree_name': None,
    }

    # Extract participants
    match = re.search(r'**Participants:** (.+?)(?:\n\n|$)', content)
    if match:
        setup['participants'] = match.group(1).strip()

    # Extract pass count
    match = re.search(r'**Passes:** (\d+)', content)
    if match:
        setup['pass_count'] = int(match.group(1))

    # Extract context
    match = re.search(r'**Context:** (.+?)(?:\n\n|$)', content)
    if match:
        ctx = match.group(1).strip()
        if ctx and ctx.lower() != 'random':
            setup['context'] = ctx

    # Extract model
    match = re.search(r'**Model:** (\w+)', content)
    if match:
        setup['model'] = match.group(1)

    return setup


def extract_tally_from_simulation_log(simulation_log_path):
    """Extract tally summary from SIMULATION_LOG.md."""
    content = simulation_log_path.read_text(encoding='utf-8')

    tally = {
        'deaths': 0,
        'births': 0,
        'criterion_moves': 0,
    }

    # Look for tally output section
    tally_match = re.search(
        r'## Tally\n(.*?)(?=\n## |$)',
        content,
        re.DOTALL
    )

    if tally_match:
        tally_text = tally_match.group(1)

        # Extract counts from tally lines
        deaths_match = re.search(r'Deaths:\s+(\d+)', tally_text)
        if deaths_match:
            tally['deaths'] = int(deaths_match.group(1))

        births_match = re.search(r'Births:\s+(\d+)', tally_text)
        if births_match:
            tally['births'] = int(births_match.group(1))

        criterion_match = re.search(r'Criterion moves:\s+(\d+)', tally_text)
        if criterion_match:
            tally['criterion_moves'] = int(criterion_match.group(1))

    return tally


def create_run_entry(run_num, date_str, worktree_name, setup, tally):
    """Create a new run entry for LAB_REPORT.md."""

    entry = f"### Run {run_num} — {date_str} — worktree `{worktree_name}`\n"

    # Setup section
    entry += "\n- **Setup:** "
    setup_parts = []

    if setup['participants']:
        setup_parts.append(setup['participants'])
    if setup['pass_count']:
        setup_parts.append(f"{setup['pass_count']} passes")
    if setup['context']:
        setup_parts.append(f"context: {setup['context']}")
    if setup['model']:
        setup_parts.append(f"model: {setup['model']}")

    entry += ", ".join(setup_parts) + "."

    # Tally summary
    entry += f" {tally['deaths']} death{'s' if tally['deaths'] != 1 else ''}, {tally['births']} birth{'s' if tally['births'] != 1 else ''}, {tally['criterion_moves']} criterion move{'s' if tally['criterion_moves'] != 1 else ''}."

    # Placeholder sections
    entry += "\n- **What worked:** \n- **What didn't move:** \n- **Implementation gaps:** \n- **Open questions:** \n- **Full record:** (path to SIMULATION_LOG.md in the worktree)"

    entry += "\n"

    return entry


def main():
    if len(sys.argv) != 3:
        print("Usage: py simulate_record_run.py <main_repo_root> <worktree_path>")
        sys.exit(1)

    main_repo = Path(sys.argv[1]).resolve()
    worktree = Path(sys.argv[2]).resolve()

    lab_report_path = main_repo / "LAB_REPORT.md"
    simulation_log_path = worktree / "SIMULATION_LOG.md"

    # Verify files exist
    if not simulation_log_path.exists():
        print(f"Error: {simulation_log_path} not found")
        sys.exit(1)

    if not lab_report_path.exists():
        print(f"Error: {lab_report_path} not found")
        sys.exit(1)

    # Get run number
    run_num = find_next_run_number(lab_report_path)

    # Get today's date
    date_str = datetime.now().strftime("%Y-%m-%d")

    # Get worktree name
    worktree_name = worktree.name

    # Extract info
    setup = extract_setup_from_simulation_log(simulation_log_path)
    tally = extract_tally_from_simulation_log(simulation_log_path)

    # Create entry
    entry = create_run_entry(run_num, date_str, worktree_name, setup, tally)

    # Append to LAB_REPORT before "## Open design questions"
    lab_content = lab_report_path.read_text(encoding='utf-8')

    # Find insertion point
    insert_pos = lab_content.find("## Open design questions")

    if insert_pos == -1:
        # No section found, append at end
        lab_content += "\n" + entry
    else:
        # Insert before the section
        lab_content = lab_content[:insert_pos] + entry + "\n" + lab_content[insert_pos:]

    # Write back
    lab_report_path.write_text(lab_content, encoding='utf-8')

    print(f"Run {run_num} entry appended to {lab_report_path}")
    print(f"Fill in the qualitative sections (What worked, What didn't move, Implementation gaps, Open questions) in LAB_REPORT.md manually.")
    print(f"Worktree path: {worktree}")


if __name__ == "__main__":
    main()
