# Test_KnowledgeUploadProbe_v0.4 (2026-10-09)

Target: Issue #2 / Draft PR #1. Latest observed DOM is documented in Design_KnowledgeUploadProbe_v0.3.md; the read-only Windows check was operator-reported PASS.

## Offline tests (safe to run now)

PowerShell from repository root:

    .\.venv\Scripts\python.exe -m pytest tests/unit/test_knowledge_upload_gated.py tests/unit/test_private_knowledge_page.py tests/unit/test_knowledge_upload_probe.py tests/unit/test_login_wait_csp.py -q

These tests mock Playwright and MUST NEVER select a file or issue a request to QommonsAI.

Cases: 
- Reject --execute-synthetic-upload unless --synthetic and --confirm-upload are present.
- Reject mutually exclusive inspection + upload flag combinations before config, browser, or export.
- Preserve old --confirm-upload-only fail-closed path.
- Reject arbitrary/altered sample even with explicit flags.
- Exact live handler is invoked at most once from the explicit CLI path in a mock.
- Operator cancel/EOF -> zero upload action, zero receipt; actual FileChooser never invoked.
- Exact UPLOAD synthetic.txt token -> only one mocked PageObject selection and local selected_unverified receipt; login/My Drive and two Inspector pauses happen.
- UI failure -> no retry, browser closed; no false receipt claim.
- Sensitive exception text is not printed.
- Existing conversion, input uniqueness, directory rejection, read-only behavior and CSP login tests retain coverage.

## Real test (NOT authorized yet)

Only after independent human approval of exactly one synthetic.txt upload on the approved test account, follow docs/operation/KnowledgeUpload_Synthetic_OneFile_Gate_v0.1.md. Do NOT execute a live selection from CI or pytest.

Expected evidence stages:
1. operator visually attests My Drive has NO same-name synthetic.txt; absence not automation-proven.
2. Playwright FileChooser set_files succeeds for exact sample -> selected_unverified.
3. HTTP accepted (only with independent network evidence, not inferred from step 2).
4. My Drive file listing updated (operator visual observation, separate from HTTP acceptance).
5. Search/indexing reflects sample (later, separate, no chat send without approval).

Server duplicate/replace semantics unknown; no retry if any stage is ambiguous. On uncertain same-name presence abort before console phrase.

CI: existing Smoke Test remains unchanged. Status/CHANGELOG must not assert these new unit tests PASS unless executed on Windows and output reviewed.
