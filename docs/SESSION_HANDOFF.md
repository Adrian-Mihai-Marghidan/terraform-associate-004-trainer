# Session handoff contract

Actual continuity lives in `private/SESSION_HANDOFF.md`.

At a lesson checkpoint or the user's "checkpoint" request, record:
- date/time and timezone;
- active lesson and objective IDs;
- actual CLI version or "not checked";
- simulator implementation/setup, provider source/version, active learner lab/store/state paths, and last actual learner command;
- last verified observation and evidence path;
- work still unexecuted or unfinished;
- any unresolved error;
- next single action;
- due reviews and unanswered questions.

At resumption, read the handoff and progress before asking the learner to restate history.
Never substitute conversational memory for recorded results.
The default handoff starts with lesson 00.1 and no completed objectives.
Recover the required simulator before Azure lifecycle practice. Keep development acceptance evidence separate from learner results and preserve the existing private backup of records plus associated state/storage.
