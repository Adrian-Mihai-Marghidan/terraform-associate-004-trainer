# Assessment rules

## Two separate measurements

1. **Exam understanding:** the learner explains a concept and answers original scenarios independently.
2. **Practical competence:** the learner personally implements, runs, verifies, and troubleshoots the relevant behavior.

Do not mark either from an assistant explanation, copied code, a CV, a repeated item, or an agent-executed example.
Track practical execution separately as not-performed, guided, or independent.
For service concepts such as HCP governance, conceptual understanding can support exam readiness while live exercise status remains not-performed.

## Assessment records

Record item ID, objective ID(s), Terraform version context, original stem/options, chosen answer, correct answer, rationale, supporting official URL, first-seen date, attempt date, whether help was given, and result.

Each item must be checkable against documentation. Verify the key before presenting it.
For version-sensitive wording, use 1.12 behavior. State needed assumptions in the stem.
Reject ambiguous items; remove them from the denominator and record why. Never improvise a changed answer key after seeing the learner's response.

Use true/false, choose-one, and choose-N formats.
In choose-N questions, explicitly state N. Use exact-set scoring for this practice tool; this is a declared practice rule, not a claim about proprietary official grading.
Explain every option after submission; cite a relevant official source.

## Timed mode

Use an original practice set across all eight domains. Default to 50 questions and 60 minutes as a training setting, not a claim about official question count or weighting.
Freeze the items and key into `private/assessments/` before the attempt. The key is withheld conversationally; a local file is not an access-control mechanism.
No hints or mid-exam solutions. Record start/end times supplied by the learner or observed in the session; do not pretend chat implements a reliable proctor or automatic timer.
If interrupted, retain answers and elapsed time, and label the result interrupted.
An item becomes "seen" as soon as it is presented, even when unanswered.
Equivalent scenarios with superficial word changes count as repeats.

Do not use leaked exam questions or claim original generated questions are official questions.
Official sample questions can introduce format but should not be counted as unseen readiness evidence.
No fixed distribution is described as HashiCorp's exam weighting.

## Suggested readiness heuristic

The following is our practice criterion; it is not an official pass mark or pass guarantee.

- Every objective is at least independently assessed; no unaddressed critical misconception remains.
- Three distinct, uninterrupted, closed-book, 60-minute practice attempts score at least 85% each.
- Each domain scores at least 80% across the combined attempts, with at least 10 distinct scored items per domain before assigning a domain confidence label.
- Repeated or assisted items contribute to review only. Exclude them from unseen scores.
- The learner can explain recurring mistakes and basic CLI behavior, rather than recalling answer letters.
- Re-check exam version and current official exam logistics before booking.

If the sample is too small, say "insufficient evidence" instead of producing a confident readiness percentage.
Track practice results separately from any actual certification result.

## Objective statuses

`not-started`, `introduced`, `practiced`, `independent`, `review-due`, `verified`.
An objective becomes verified only after an independent assessment and a successful delayed review.
Keep dated evidence and the practical execution flag; status alone does not authorize a CV claim.
