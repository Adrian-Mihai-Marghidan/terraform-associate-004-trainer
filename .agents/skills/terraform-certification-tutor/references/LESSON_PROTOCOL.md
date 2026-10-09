# Lesson protocol

1. Name the lesson and its objective IDs. State one concrete learning outcome.
2. Explain the concept from first principles; define at most a few new terms.
3. Use one brief Azure DevOps comparison when it helps. Do not require Azure details.
4. Demonstrate a minimal example and explain the important lines.
5. Ask the learner to predict behavior and wait.
6. Give one command or implementation task. Let the learner run it.
7. Inspect actual results and compare with the prediction.
8. Introduce one harmless, reversible local mistake after the successful path.
9. Guide investigation, then let the learner repair it. Explain cause, diagnostic evidence, and fix.
10. Ask for a teach-back or a fresh independent variation. Avoid merely echoing the example.
11. Record evidence, assistance, gaps, and a delayed review.

For each implementation step explain purpose, execution, success signs, a likely failure, and a relevant production difference. Scale detail to the learner's response.

Do not run plan/apply/destroy in an employer checkout or replace the learner's own work.
Default Azure lifecycle practice to the Resource Group simulator lab. Verify the startup contract in `docs/SIMULATOR_INTEGRATION.md` before commands. Explain Terraform Core, the custom provider, and simulated storage separately.
Keep development validation in a disposable private copy. Do not apply the learner lab for them or award progress for agent checks.
When a required behavior is unsupported, name it, use official documentation or a clearly separate exercise, and record practical execution as pending. Do not silently fall back to terraform_data or real Azure.
Before using a file-writing provider, confine its output path to the exercise directory.
Before import, check that the provider/resource actually supports it.
Teach state inspection without editing state JSON by hand.
Teach HCP governance through documented scenarios if there is no live account.

Teach first, then use a few questions; do not start an exam during an ordinary lesson.
If the learner is tired or requests a shorter session, checkpoint the unfinished step and preserve it for next time.
