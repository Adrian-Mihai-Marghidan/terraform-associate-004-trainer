# Project specification

## Goal

Prepare a learner who wants Terraform taught from zero for Associate 004.
Certification is the primary outcome. Practical exercises reinforce tested concepts; optional engineering projects do not delay the exam path.

Secondary goals are a maintainable GitHub portfolio project and reuse by other learners. Public material must explain the architecture, supported behavior, setup, tests, and limitations without publishing personal progress or implying certification. Keep professional background and individual preferences in private continuity records. Use familiar comparisons when helpful, without assuming Terraform competence.

## What the agent consists of

Codex supplies reasoning and conversation. `AGENTS.md` sets persistent project behavior, one repository skill supplies repeatable teaching workflows, Markdown describes the course, and local JSON/Markdown records retain verified progress.

The independently maintained sibling `../terraform-azure-simulator` supplies a custom Terraform provider backed by persistent local JSON storage. It is required for Azure lifecycle practice.
No standalone LLM application, continuously running agent, database server, Azure account, authentication, or paid cloud infrastructure is needed.
A new session reads repository records; it cannot recover omitted conversations automatically.

## Required modes

| Mode | Required behavior |
| --- | --- |
| Teach | Explain one concept, introduce terms, map the objective, demonstrate briefly. |
| Practice | State a small task and success signs; let the learner implement and execute. |
| Troubleshoot | Inspect actual code/output, propose an investigation, explain cause and repair. |
| Review | Retrieve a previously learned idea using a changed example; schedule another review. |
| Assess | Use original unambiguous items and source-grounded explanations; record assistance. |
| Timed exam | Freeze items/key before answers, withhold hints, time the attempt, score after submission. |
| Resume | Read the handoff and evidence; continue unfinished work without guessing competence. |
| Checkpoint | Update progress, gaps, reviews, session history, and the next explicit action. |

## Teaching contract

Explain what is being built, why it matters, how it works, how to run and verify it, a common failure, and the relevant production difference. Keep this to the current step rather than repeating a large template after every sentence.

Start with lesson 00.1. A gentle baseline may follow foundations or be requested; it is not a 30-question prerequisite and does not authorize skipping topics.
Increase depth when the learner demonstrates understanding. A hint-assisted answer is practice, not an independent assessment.

For CLI objectives, require learner execution and explanation before marking independent practical competence. For conceptual objectives, scenario reasoning can establish exam readiness without live cloud access. Keep any unperformed account-based exercise labeled unperformed.

## Scope boundaries

Core scope: official objective IDs 1a through 8d, with certification-specific coverage of dependencies, custom conditions, sensitive data, Vault concepts, ephemeral values, write-only arguments, and HCP integration.

Required practical environment: the Azure simulator, using the actual HashiCorp Terraform CLI for evaluation, dependencies, plans, state, refresh, and lifecycle processing. A distinct custom provider performs local simulated Azure operations. Simulator development is development-agent work, never a learner prerequisite.

Extensions: Terraform tests/mocks, deeper CI/CD engineering, advanced Azure, GitOps, and provider engineering study. Offer these after core study or on request; they are not implicit exam prerequisites.

Default Azure lifecycle practice begins with a simulated Resource Group. Built-in resource labs supplement selected language concepts without replacing this requirement.
Simulator infrastructure JSON and Terraform state remain separate so external changes produce meaningful refresh and drift exercises.
Only supported behavior may be taught as executed. Unsupported topics use explicit separate exercises or official documentation; remote backends, import, Vault, and HCP behavior cannot be inferred from this provider.
See [SIMULATOR_INTEGRATION.md](SIMULATOR_INTEGRATION.md) for startup, supported schema, boundaries, and resumption.

## Acceptance criteria

1. A fresh Codex session observes the repo instructions and can invoke the skill.
2. All 37 objectives have a lesson and an explicit assessment status.
3. The first simulator configuration completes init, validate, plan, apply, a repeated unchanged plan, state inspection, and destroy on the learner's laptop.
4. A checkpoint and a fresh session preserve actual progress and unfinished work.
5. Original question generation supports all published question formats and excludes repeats or assisted items from readiness evidence.
6. No score is called an official pass prediction or certified result.
7. State/plans and personal records remain out of public commits, while provider lock files remain eligible for commits.
8. Deferred checks and future exercises are visible.
9. A separate disposable agent lab verifies provider installation, Resource Group creation, no-op planning, tag update, out-of-band drift detection, and destruction in persistent local storage. This establishes implementation behavior, not learner competence.
10. A public checkout supports repository checks without private records or local toolchains. Azure lifecycle setup explicitly requires the separately distributed simulator; its source/release, licensing, and tested platform must be identifiable before publication.
11. Public portfolio claims distinguish implemented infrastructure, curriculum coverage, future exercises, AI assistance, and independently demonstrated learner skills.

Items requiring Codex or Terraform on the user's machine remain acceptance checks, not completed claims.
