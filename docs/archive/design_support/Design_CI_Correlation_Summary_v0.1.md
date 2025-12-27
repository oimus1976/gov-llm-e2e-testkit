# Design_CI_Correlation_Summary_v0.1

This document defines the **normative presentation semantics**
for submit–probe correlation results in CI.

This document does NOT define:

- correlation algorithms
- submission behavior
- answer detection logic

It defines ONLY:

- how correlation states MUST be presented in CI
- how humans MUST interpret CI results

This document is a design-support artifact.
Implementation must strictly follow this document.

---

## 1. Purpose

The purpose of this document is to prevent **human misinterpretation**
of submit–probe correlation results in CI.

Specifically, this document ensures that:

- correlation is treated as a *state*, not a success/failure judgement
- WARN and INFO are not mistaken for test failures
- absence of observable evidence is not misclassified as system failure

---

## 2. Terminology

- Correlation State:
  An observable state describing the relationship between
  a submission (submit_id) and observed assistant responses.

- CI Result:
  A judgement label (PASS / WARN / INFO) used solely for
  human-facing CI presentation.

IMPORTANT:
Correlation State and CI Result are orthogonal concepts.

---

## 3. Correlation State × CI Result Mapping

| Correlation State | CI Result | Meaning |
|-------------------|-----------|---------|
| Established       | PASS      | An assistant response was observed and can be causally explained by this submission. |
| Not Established   | WARN      | An assistant response was observed, but causal correlation could not be established. |
| No Evidence       | INFO      | No observable assistant response related to this submission was detected. |
| Unassessed        | INFO      | Correlation assessment was intentionally skipped. |

### Binding Note（重要）

```markdown
The mapping above is **normative and binding**.
CI implementations MUST NOT reinterpret or extend these meanings.
```

---

## 4. Human Interpretation Rules

The following interpretations MUST be enforced:

- PASS means:
  - correlation was established
  - no further action is required

- WARN means:
  - this is NOT a failure
  - limited observability was encountered
  - investigation is optional and situational

- INFO means:
  - no judgement of correctness is implied
  - this does NOT indicate abnormal behavior

---

## 5. Explicit Non-Meanings

The following interpretations are explicitly prohibited:

- WARN does NOT mean test failure
- INFO does NOT indicate malfunction
- No Evidence does NOT imply AI did not attempt to answer
- Correlation results MUST NOT be used to infer internal AI state

---

## 6. CI Presentation Requirements

CI summaries MUST:

- explicitly display:
  - submit_id
  - correlation_state
  - CI result label

- include a short human-readable explanation
  corresponding to the correlation state

- avoid speculative language such as:
  - "likely"
  - "probably"
  - "may indicate"

---

## 7. Relationship to Other Documents

This document depends on:

- Design_submit_probe_correlation_v0.2

This document constrains:

- GitHub Actions CI summary presentation
- Human interpretation of CI outputs

This document does NOT override:

- PROJECT_GRAND_RULES
- Test Plan
- Answer Detection design

---

## 8. Versioning Policy

- This document follows semantic versioning.
- Changes to wording that affect interpretation
  MUST increment the minor version.
- CI implementations MUST track the version explicitly.

---

## 9. Summary

This document ensures that submit–probe correlation results
are presented in CI as **explanatory information**, not as
binary success/failure judgements.

By fixing presentation semantics at the design level,
this project prevents CI-induced misinterpretation
and supports long-term, stable E2E operation.

---
