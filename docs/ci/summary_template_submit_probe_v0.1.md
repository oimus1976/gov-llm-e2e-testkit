# 🧪 E2E Correlation Summary — submit–probe v0.2

## Overview

This CI run reports the **observable correlation state** between:

- a UI submission executed by **ChatPage.submit v0.6**, and
- assistant responses observed by **Answer Detection Layer (probe v0.2)**.

Evaluation principle:

> **Correlation is a state, not a success/failure verdict.**

⚠️ **WARN / INFO do NOT indicate CI failure.**  
They represent *observable-but-non-conclusive* states by design.

---

## Correlation Result

| Item | Value |
| --- | --- |
| submit_id | `${SUBMIT_ID}` |
| chat_id | `${CHAT_ID}` |
| correlation_state | **${CORRELATION_STATE}** |
| ci_display_label | **${CI_RESULT}** |

---

## Action Guidance

| correlation_state | CI Label | Action Required | Notes |
|------------------|----------|-----------------|-------|
| Established | PASS | No | Correlation successfully explained |
| Not Established | WARN | Optional | Retry only if correlation is required |
| No Evidence | INFO | No | Investigate only if repeated |
| Unassessed | INFO | No | Expected for skipped executions |

---

## State Interpretation

- **Established (PASS)**  
  An assistant response was observed and can be **explainably correlated**
  to this submission based on observable facts.

- **Not Established (WARN)**  
  An assistant response may exist, but a **unique, explainable correlation**
  to this submission could not be formed.

- **No Evidence (INFO)**  
  No observable assistant response related to this submission
  was detected within the observation window.

- **Unassessed (INFO)**  
  Correlation assessment was intentionally skipped for this execution.

---

## What This Result Means

- This summary **does not judge correctness or quality** of the response.
- This summary **does not report probe execution errors**, if any.
- This summary reflects **only what could be observed**, nothing more.

The system explicitly does **not** infer:

- AI intent or internal decision-making
- internal service failures or causes
- reasons why a response may not have been generated

---

## Explicit Constraints (By Design)

The following constraints are intentional and binding:

- ❌ No speculative judgement beyond observable facts
- ❌ No FAIL due to missing or ambiguous evidence
- ❌ No inference of internal AI or service state
- ✅ Correlation is treated strictly as a **state**
- ✅ CI labels (PASS / WARN / INFO) are **presentation semantics only**

These constraints are defined to ensure
long-term CI stability and human interpretability.

---

## References

- Design_submit_probe_correlation_v0.2
- Design_CI_Correlation_Summary_v0.1
- Debugging_Principles_v0.2
- PROJECT_GRAND_RULES v4.x

---

## Appendix (Optional Diagnostics)

<details>
<summary>Observed Signals (Best-effort)</summary>

- REST GET /messages observed: `${REST_OBSERVED}`
- GraphQL createData observed: `${GRAPHQL_OBSERVED}`
- event timestamps: `${EVENT_TIMESTAMPS}`

</details>
