# Continuity protocol

## Resume

Read `private/SESSION_HANDOFF.md`, `private/PROGRESS.json`, and `private/REVIEWS.json`.
Compare the handoff to dated evidence if they disagree.
State the last verified result, pending step, and next lesson in three sentences or fewer.
Use one due retrieval prompt when appropriate; continue the pending task afterward.
Missing records mean unassessed progress, not permission to invent history.
For simulator practice, recover `private/SIMULATOR_SETUP.json`, the learner lab path, provider source/version, and storage path. Source the terminal-local environment and repeat startup checks. Preserve both Terraform state and simulator storage; neither replaces the other.

## Checkpoint

Use the timezone recorded in private/PROGRESS.json for learner timestamps; Europe/Bucharest is the default when no preference is configured. A first setup with bootstrap --timezone records an explicit preference. Change an existing preference only when the learner asks. A shell or execution-environment timezone is not a preference change. Record any agent-environment timezone separately.
Record a session ID and date/time.
Update the objective evidence and separate independent/guided/agent-executed work.
Record observed gaps and schedule review dates; suggested intervals are 1, 3, 7, and 14 days, adjusted from performance.
Add a short session entry to `private/SESSION_HISTORY.json`.
Write the handoff last, with actual CLI version, remaining errors, next single action, and unanswered questions.
Include simulator readiness, the active lab/storage paths, the last actual learner command, and any unsupported or deferred behavior. Agent milestone evidence stays separate from learner objective evidence.
Re-read the small changed records for consistency.

Do not schedule an external reminder merely by setting a due review date; review dates are consulted when the learner returns.
Do not reset files at the start of a new session.
Do not claim Git backs up the ignored `private/` folder. Its persistence requires the learner's separate private backup.
