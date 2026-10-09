# Design_KnowledgeUploadProbe_v0.5 — one-file live evidence and completion boundary

Date: 2026-10-09
State: Draft PR #1; retrospective evidence update only. **No new authorization to upload, delete, replace, retry, send chat, mark Ready or merge.**
Predecessor: `Design_KnowledgeUploadProbe_v0.4.md` (preserved, describes the *pre-execution* gate).

## 1. Purpose
Record the authorized **one-time synthetic file registration** and subsequent manual retrieval without turning operator-reported results into HTTP-level or automated E2E claims. Set the review boundary of the existing one-file MVP. No production code or behavior change is requested by this document.

## 2. Background and evidence
- Branch at documentation baseline: `feature/private-knowledge-upload-mvp`, HEAD `7837d8c96b5247bbcefb09ac6dc6859e831e6d2b`, base main `12706627e74c9e942a1f5598345bd635a7a243ea`; at baseline PR #1 was OPEN/Draft and 17 ahead / 0 behind.
- Observed DOM: [Issue #2 comment 6073127818](https://github.com/oimus1976/gov-llm-e2e-testkit/issues/2#issuecomment-6073127818). Read-only control probe PASS was operator-reported; see comment 6073651368.
- Windows focused offline pytest on four files was re-run after v0.7.37 correction; operator reported `[100%]` and `$LASTEXITCODE=0`. **Exact individual test count is unknown**. [Comment 6076752013](https://github.com/oimus1976/gov-llm-e2e-testkit/issues/2#issuecomment-6076752013).
- After separately approved one-file selection, operator entered the exact `UPLOAD synthetic.txt` phrase. Playwright FileChooser reported `selected_unverified`; a local-only `synthetic.selection-20261009T081657879642Z.json` selection receipt was produced. My Drive displayed `synthetic.txt`. [Comment 6077190221](https://github.com/oimus1976/gov-llm-e2e-testkit/issues/2#issuecomment-6077190221).
- After F5 reload the item remained; UI state progressed `学習中` -> `学習済み`. [Comment 6077224107](https://github.com/oimus1976/gov-llm-e2e-testkit/issues/2#issuecomment-6077224107).
- Human opened Private Knowledge chat, selected only `synthetic.txt`, switched Web search OFF and asked for the sample code **without putting the answer in the question**. Response included the expected `SYNTHETIC-KNOWLEDGE-0001` and filename. This is **one manual retrieval/answer PASS**, not a Playwright search E2E. [Comment 6078368762](https://github.com/oimus1976/gov-llm-e2e-testkit/issues/2#issuecomment-6078368762).
- Existing GitHub E2E/Smoke run [37882053878](https://github.com/oimus1976/gov-llm-e2e-testkit/actions/runs/37882053878) completed successfully at baseline HEAD. It does **not** execute the new focused unit test suite.

## 3. Requirements and authority boundary
- Retain the **only** bundled synthetic Markdown source and a byte-identical UTF-8 TXT export. Keep local receipt out of GitHub/Drive. Do not ingest municipal records, credentials, authenticated DOM or response bodies.
- Preserve existing human-run CLI gate and `selected_unverified` receipt semantics. Observed My Drive persistence and manual answer are documented separately; **do not retroactively turn receipt HTTP/server/search booleans to true**.
- `synthetic.txt` now exists on the test account by operator report. The previous runbook's precondition "no same-name file" is no longer satisfied. **No additional upload or retry is authorized**.
- Existing `LoginPage`, `env_loader`, CI workflow, chat PageObjects and source code are unchanged by this evidence update.
- An automated search/answer E2E is a separately scoped future task that first requires observing the actual knowledge-selection/chat DOM. Human approval remains required before any automated live chat submission.

## 4. Architecture / evidence flow
`synthetic.md` -> exact `synthetic.txt` -> separately authorized Playwright FileChooser selection -> **local `selected_unverified` record** -> human My Drive listing/F5/state observation -> **manual** Private Knowledge selection and question -> exact sample-code answer.

Evidence strength increases through direct operator UI observation, but no HTTP response status, server-side collision handling or backend index implementation was independently inspected.

## 5. Exceptions and unknowns
- HTTP acceptance code, backend index implementation/state, link clickability of the reported source citation, same-name replacement behavior, other formats, multiple files, and full search automation remain **unknown**.
- File selection may have immediate side effects. On uncertainty, **never auto-retry**. A same-name item exists; prior manual absence attestation applies only to the original authorized one-time operation.
- `$LASTEXITCODE=0` supports the operator's focused test report; it is not independent remote execution proof or an exact per-test count.
- The old v0.4 and prior docs remain as historical preflight snapshots, not statements of current authorization.

## 6. Tests and review checkpoint
- The focused Windows suite previously used `test_knowledge_upload_gated.py`, `test_private_knowledge_page.py`, `test_knowledge_upload_probe.py`, `test_login_wait_csp.py` (operator PASS report after regression fix). No test was executed by this documentation update.
- GitHub CI baseline run: success for existing Smoke only. New focused tests are **not** established as CI-covered.
- Draft review should check the exact-byte gate, fail-closed flag parsing, operator duplicate check (not automatic deduplication), FileChooser input identity, exception/redaction, no automatic retry, local-only receipt, and correctness of evidence labeling.
- PENTA perspectives: scope remains one-file; evidence stages are disjoint; user interaction authority is explicit; unknown duplicate semantics are a safety risk; no new test infrastructure is required for this retrospective update. This is **not** independent acceptance or a Ready/merge authorization.

## 7. Extension plan / acceptance decision
1. Finish PR review and correct only substantiated defects.
2. Decide whether the **one-file registration MVP** can be accepted on existing operator evidence. Do not silently expand acceptance to HTTP forensics or automated retrieval.
3. If a recurring automated retrieval regression test is desired, create a separate design/task after observing the knowledge selection UI, reuse already registered `synthetic.txt`, and separately authorize actual chat transmission.
4. Keep PR #1 Draft until human decides Ready/merge; never update main from this retrospective documentation step.
