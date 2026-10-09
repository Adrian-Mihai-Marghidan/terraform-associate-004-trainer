# Contributing

The primary goal is beginner Terraform Associate preparation. Improvements to public presentation, setup, and reliability should support that goal. Keep the Azure simulator independently maintained; propose provider changes in its own project.

For teaching changes, preserve the curriculum order, official objective IDs, one-concept/one-command approach, and separate exam/practical evidence. Explain unsupported simulator features rather than replacing required Azure lifecycle practice silently.

## Verify a change

From the mentor root on macOS or Linux/WSL2, with Python 3.9+ and Git:

```bash
python3 scripts/check_package.py
python3 -m unittest discover -s tests -v
```

Review the intended changes, stage the public files, then check their actual indexed content:

```bash
python3 scripts/check_public_files.py
git diff --cached --check
```

The public-file check rejects recognizable private/generated artifacts and personal home paths. It is a focused guard, not a complete secret scanner; inspect the staged content and commit metadata yourself.
For a Git-free source export, use `python3 scripts/check_public_files.py --filesystem` on that clean export, not a personal working directory containing ignored records/tools.

With the [compatible simulator and local setup](docs/COMPANION_SIMULATOR.md), maintainers can run:

```bash
python3 scripts/validate_simulator.py
python3 scripts/validate_local_labs.py
```

These use disposable private development labs and retain local evidence. Agent runs do not establish learner competence. For a changed learner lab, verify init, fmt, validate, and relevant lifecycle behavior in an isolated copy; never use somebody's personal state or store.
The included GitHub workflow checks the public Python/package layer; it does not certify the simulator, teaching experience, or Azure compatibility.

## Issues and pull requests

Describe the trigger, expected behavior, actual behavior, version/platform, and a minimal synthetic reproduction. State what was executed and what remains untested. For curriculum claims, link current official HashiCorp documentation and confirm Terraform 1.12 behavior.

Do not attach personal progress, private assessments/answer keys, employer material, credentials, Terraform state, saved plans, simulator databases, or raw logs. Use fictional names and only the output excerpt needed to reproduce the issue. Follow [SECURITY.md](SECURITY.md) for sensitive reports.

Use a public-appropriate Git author identity. Choose any GitHub private email locally before your first public commit; do not assume a global employer identity is suitable. See [GitHub commit email guidance](https://docs.github.com/en/account-and-profile/how-tos/email-preferences/setting-your-commit-email-address).

## License and assistance

Contributions to this mentor are made under [MIT](LICENSE). Keep dependency notices and third-party terms intact.
AI-assisted contributions are welcome. Review and test generated changes, describe material limitations, and take responsibility for the final result. Do not report checks that were only proposed.
