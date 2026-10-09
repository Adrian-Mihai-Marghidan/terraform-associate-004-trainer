# Progress storage contract

The authoritative personal record is `private/PROGRESS.json`.
Version-controlled templates are empty defaults, not the learner's current status.
Initialize them with `python3 scripts/bootstrap_progress.py`.
For a new learner, `--timezone America/New_York` (or another IANA timezone) selects checkpoint times. Existing records and timezone preferences are preserved; bootstrap does not change an established preference.

Each objective records its status, exam understanding, practical execution, evidence, last assessment, and next review. Evidence identifies the command/output or learner explanation and whether assistance occurred.

Store repeated, guided, and independent attempts distinctly.
An unexecuted configuration has practical status `not-performed`.
A verified example run by Codex can prove example behavior, but not learner competence.
The same applies to building/testing the required Azure simulator. Store milestone logs under `private/development/`, never as objective mastery or independent learner execution.

At a checkpoint:

1. Record observations and a session ID.
2. Update objective records with evidence.
3. Update knowledge gaps and reviews.
4. Append the session summary to `private/SESSION_HISTORY.json`.
5. Write the handoff last, with unresolved errors and the next concrete action, then re-read the changed records for consistency.

If records disagree, retain dated raw evidence and mark the conflict pending reconciliation. Do not choose the more flattering status.
The learner's private backup carries personal continuity to another machine. A fresh Git clone only carries the course and templates.
