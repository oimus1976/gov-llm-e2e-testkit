# Design_KnowledgeUploadProbe_v0.4 — synthetic one-file selection gate

Date: 2026-10-09
State: Draft PR #1; **code/test preparation authorized, live file selection and upload not authorized**.
Preserve v0.1–v0.3 design history.
Scope: Issue #2; DOM evidence comments 6073127818 and read-only PASS comment 6073651368.

## 1. Purpose
Prepare a controlled operator-driven path for selection of **exactly one** bundled synthetic TXT file in QommonsAI Private Knowledge My Drive, after separate human approval. Do not execute this live path or claim upload/registration/search success during code preparation.

## 2. Background and evidence
The operator reported live read-only control check PASS on Windows, Draft head 255756f and focused offline tests exit 0. Current PrivateKnowledgePage.select_synthetic_file validates byte-exact synthetic Markdown, matching exported TXT, literal UPLOAD, observed menu/input attributes and FileChooser element. The live FileChooser-to-input linkage and auto-upload-on-selection behavior are unverified. File-list row DOM, same-name collisions and replacement semantics have not been observed.

## 3. Requirements
- Preserve current login/environment/profile resolution, default inspection, read-only check mode, existing PageObjects, Smoke Test and CI.
- Keep --confirm-upload **alone** failing closed. Add --execute-synthetic-upload; only accept with --synthetic AND --confirm-upload, not with --inspect-ui/--check-observed-controls. Missing/contradictory flags stop before any file export, browser or login.
- A future **separately approved** operator run uses LoginPage then PrivateKnowledgePage.open_my_drive and pauses in Inspector **before selection**, to allow human inspection of My Drive and manual check for an existing synthetic.txt, including any relevant folders/pagination. Stop on doubt. Do not invent file-list selectors or claim automatic dedupe.
- After resuming, terminal asks for exact phrase UPLOAD synthetic.txt. Anything else, including EOF, stops before upload-menu click or FileChooser selection. This explicitly attests that no same-name item was found in an isolated test drive and user authorizes possible instant upload of this specific synthetic content. Human observation is NOT proof server-side replacement is impossible.
- Revalidate both sample Markdown and exact TXT bytes immediately before UI action. Reuse select_synthetic_file with literal UPLOAD, one FileChooser and one set_files call.
- After set_files, write existing local receipt with status selected_unverified and all HTTP/list/search booleans false. Pause browser for human visual confirmation only; do not automatically send chat, search, retry, replace, delete or submit other UI.
- On failure after possible set_files, state is unknown: never auto-retry. Browser/Playwright exceptions are redacted, no secret, DOM, cookie or response-body dumps. A completed live selection still exits 2 (server/list/search unverified) rather than claiming success.
- Do not perform actual live selection in this code-change approval. Draft PR #1 only; no main/Ready/merge and no municipal data.

## 4. Architecture / flow
Human CLI -> validate_sample -> load_login_config -> prepare_txt -> upload_synthetic_one -> existing LoginPage -> PrivateKnowledgePage.open_my_drive -> page.pause (manual same-name check) -> exact terminal phrase -> existing select_synthetic_file(..., confirmation="UPLOAD") -> write_receipt -> page.pause (observe only) -> exit code 2.

## 5. Exceptions
Changed sample, conflicting export, unavailable settings/login, missing/ambiguous file input or menu, unexpected folder FileChooser, or absent confirmation: STOP. Avoid claiming the absence of duplicates from unobserved list DOM. Avoid idempotent retry on uncertain network state.

## 6. Tests and preliminary review
Mock-only offline tests: invalid flag combinations no effects; old --confirm-upload remains blocked; cancel/EOF before file selection; exact phrase invokes guarded PageObject once; exceptions redacted and browser closed; receipt does not claim HTTP/server/search success. Existing focused tests and CI Smoke Test remain unchanged. No tests actually contact QommonsAI.

PENTA-style impact self-assessment (**not independent sign-off**):
1. DOM: observed menu/button/input controls reused; list selectors unknown.
2. Data: only byte-identical bundled synthetic data; no secrets.
3. Effects: separate live human authorization required; chooser selection may trigger upload.
4. Regression: original inspection commands unchanged, mocked offline tests, CI unchanged.
5. Governance: Draft only; design -> implementation -> CI -> status/changelog, independent review pending.

## 7. Extension plan
Obtain explicit new authorization before any real file selection. Run focused Windows tests, inspect My Drive for synthetic.txt before selecting. Record file selection, HTTP acceptance, My Drive listing and search independently; do not retry if server state is uncertain.
