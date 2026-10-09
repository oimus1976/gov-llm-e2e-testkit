# Design_KnowledgeUploadProbe_v0.1

Date: 2026-10-06
State: implementation proposal; live QommonsAI UI verification pending

## Purpose
Prototype one explicit, synthetic-data-only upload of a locally retained Markdown knowledge record to QommonsAI Private Knowledge. This is an opt-in adjunct, not a replacement for F9-B's frozen knowledge-set test methodology. Do not call it from F8/F9, pytest E2E, or CI.

## Background
Existing ChatPage/login/answer capture automation does not document a Private Knowledge upload DOM. Do not infer navigation selectors, file naming collision behavior, folder behavior, or ingestion completion semantics. Past manual tests reported that Markdown syntax in a .txt file was interpreted as headings. Treat current behavior as unverified until live smoke-tested.

## Requirements
- Preserve original .md bytes; create sibling .txt only when absent or identical. Never silently overwrite.
- Only explicit operator invocation, `--confirm-upload`, and a final confirmation permits file input interaction.
- Require `--synthetic`; reject use on real municipal/internal documents in this proof-of-concept.
- Manual login and navigation to the target Private Knowledge upload form in a visible browser.
- Inspect UI to locate exactly one native `input[type=file]`; fail closed if zero or multiple. Do not guess labels or submit buttons.
- Selecting a file alone is **not** proof of server acceptance, indexing, searchability, or user access. Report `selected_unverified`; operator must verify the UI and a chat retrieval.
- No credentials in code, no network APIs, no chat sends, no auto delete/update. Screenshot/logs must not include sensitive data.

## Architecture / flow
Input: synthetic UTF-8 .md -> adjacent .txt (same text) -> manual browser login/navigation -> explicit file chooser selection -> local receipt JSON with status `selected_unverified`. Original Markdown remains source of truth. Separate QommonsAI copy is disposable.

## Exceptions
Missing/multiple file inputs: stop. Existing differing .txt: stop. Input not synthetic: stop. Operator closes browser: stop without claiming registration. Identical same-name uploads, nested folders, and ingestion latency: **not assumed**, separate live observations needed.

## Tests
Offline unit tests for deterministic no-overwrite conversion, argument constraints, single-input gate, and upload receipt. Real QommonsAI upload/login/search not executed by CI.

## Extension plan (not part of MVP)
After one observed live DOM/response trace, add a versioned PrivateKnowledgePage page object and explicit upload/index/search read-back checks. Only then decide whether to integrate with personal/municipal knowledge-routing policy. No silent routing of municipal data.
