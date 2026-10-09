# QommonsAI Private Knowledge synthetic one-file gate — operator runbook v0.1

Updated 2026-10-09. **NOT authorization to run the live upload.**

## Scope and risks
Only the committed synthetic sample data/knowledge_upload/synthetic.md and its byte-identical synthetic.txt may be used. This is an online test on an authorized isolated QommonsAI account only, never LGWAN, real municipal content, shared/organization drive, or an existing document.

**Selecting synthetic.txt may immediately upload to the server.** The behavior is not yet observed. No service duplicate/overwrite semantics are known, and there is no observed file-row selector for automated deduplication. **Do not run until the human has separately approved a one-file live upload.**

## Preflight after approval
- Confirm clean worktree and latest reviewed Draft PR #1 revision. Do not force update or discard local changes.
- Run the focused offline tests in docs/test_plan/Test_KnowledgeUploadProbe_v0.4.md and stop on failure.
- Confirm the test account, selected My Drive, and file inventory. If synthetic.txt already exists, or folder/pagination makes its absence uncertain, abort. No replacement/deletion.
- Keep credentials in existing .env/profile only. Never paste secret values, cookies, entire DOM, network body, or usernames into GitHub.

## Command — only after **separate explicit live-upload approval**

    .\.venv\Scripts\python.exe scripts/knowledge_upload_probe.py data/knowledge_upload/synthetic.md --synthetic --confirm-upload --execute-synthetic-upload

The script validates the unchanged sample, logs in, navigates My Drive, then pauses in Playwright Inspector **before** clicking the upload control. Operator visually inspects for an existing synthetic.txt, then resumes Inspector. If unsure, do not confirm.

PowerShell subsequently requests exact input:

    UPLOAD synthetic.txt

Any other answer or EOF cancels before file selection and creates no selection receipt. This phrase explicitly means: inspected the isolated test-account My Drive, found no same-name file in all relevant visible entries, and separately authorized selection knowing it may immediately upload. The check is a human attestation, NOT verified server-side collision protection.

After valid input, the code rechecks source/export bytes, opens observed upload menu via role locator, checks FileChooser input attributes, sets **one** synthetic.txt and writes a local JSON receipt with status selected_unverified and HTTP/list/search booleans false; then pauses for visual inspection. It does not auto-submit any other button, perform chat/search, delete, replace or retry. If unexpected behavior occurs **stop**, verify server state manually before any re-run.

Result interpretation: A receipt or FileChooser success means selected_unverified, NOT upload-success. Even after a one-file selection the CLI returns code 2 because HTTP acceptance, My Drive registration and searchability are not independently verified. Report these stages separately, with no raw private DOM/network content.

This runbook is a *future operation plan*, not a claim that live upload was performed or authorized by the present code-preparation approval.
