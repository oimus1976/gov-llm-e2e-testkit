# 📘 **Design_probe_graphql_answer_detection_v0.2**

**Project:** gov-llm-e2e-testkit
**Layer:** Answer Detection / Probe
**Status:** Formal Design
**Version:** v0.2
**Last Updated:** 2025-12-12

---

## 1. Purpose

This document defines the **formal completion semantics and waiting conditions**
for `probe v0.2.x` in the Answer Detection Layer.

The purpose is to replace **time-based probe termination** with
**semantic completion detection**, while preserving safety through bounded waiting.

---

## 2. Background

In `probe v0.2.1`, probe termination was driven primarily by a **fixed time window**
after `POST /messages`.

Empirical observation showed that:

* Long, structured prompts may still be generating responses
  when the time window expires.
* In such cases, probe termination incorrectly reports
  `no_graphql` or incomplete states.

This revealed that **time alone is not a valid completion signal**.

---

## 3. Design Principles

The following principles are binding for probe v0.2.x:

1. **Semantic completion must be detected explicitly**
2. **Time is a fallback, not a primary condition**
3. **REST is the canonical answer source**
4. **GraphQL is auxiliary and non-mandatory**
5. **DOM/UI state must not be used**

---

## 4. Completion Semantics

### 4.1 Primary Completion Event (Authoritative)

Probe completion is achieved when:

* `REST GET /messages` returns
* an `assistant` role message
* with non-empty content
* associated with the current `chat_id`

This event represents **authoritative answer completion**.

---

### 4.2 Secondary Completion Event (Verification Path)

As a secondary, non-mandatory path, probe may also observe:

* `GraphQL messages query`
* returning an `assistant` role message
* matching the REST content

This path exists solely for **cross-verification** and diagnostics.

---

### 4.3 Optional Streaming Signal (Non-binding)

If observed, `GraphQL createData` streaming events:

* may be recorded
* must not be required
* must not be used as the sole completion condition

---

## 5. Waiting Strategy

Probe execution follows this strategy:

1. Initiate observation after `POST /messages`
2. Enter a waiting loop
3. On each iteration:

   * Check Primary Completion Event
   * Else check Secondary Completion Event
4. If either is satisfied:

   * Mark probe as completed
   * Exit loop
5. If neither is satisfied and time limit is reached:

   * Exit with timeout status

**Time limits exist only to prevent infinite waiting.**

---

## 6. Status Classification

Probe result status MUST distinguish completion from non-completion.

Indicative status values include:

* `completed_rest_only`
* `completed_with_graphql`
* `completed_graphql_secondary`
* `timeout_before_completion`
* `inconclusive`

Exact naming is implementation-defined but **semantic distinction is mandatory**.

---

## 7. Scope and Non-Scope

### 7.1 In Scope

* Probe waiting conditions
* Completion semantics
* Status classification

### 7.2 Out of Scope

* ChatPage.ask behavior
* XHR interception mechanisms
* UI state detection
* CI execution policy

---

## 8. Compatibility

This design:

* Is backward-compatible with v0.2.1 logging formats
* Does not require changes to:

  * env_loader
  * CI workflows
  * PageObject design

---

## 9. Rationale Summary

* The failure mode was **premature termination**, not missing events
* Semantic completion aligns with Answer Detection Layer goals
* REST provides the canonical answer boundary
* GraphQL enhances observability but must not gate completion

---

## 10. Next Steps

Following this design, the next permitted actions are:

1. Implement waiting logic changes in `run_probe_once.py`
2. Update Test Plan to include long-generation cases
3. Reflect semantic completion in Answer Detection Layer v0.2

---

## Version

**v0.2 — Semantic Completion Detection Introduced**

---
