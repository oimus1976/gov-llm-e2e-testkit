# Private Knowledge probe test plan v0.2

Scope: Issue #2, Draft PR #1 only. Offline unit tests do not execute the script, browser or QommonsAI.

- Preserve UTF-8 byte-identical conversion, idempotence, divergent export rejection, invalid/empty input, operator flags and honest selection-receipt coverage.
- Replace v0.1's generic-input test: upload is disabled without observed DOM, regardless of flags, with no export/browser/receipt side effects.
- Reject arbitrary files even with `--synthetic`, and reject a changed bundled sample.
- Verify direct load_env delegation, required fields, no fallback/mutation, and redaction of secret-bearing errors.
- Mock Playwright/LoginPage to verify configured timeouts, open/login/pause order, no selection/navigation guesses and cleanup after failure.
- Inspect-mode CLI returns pending status and never writes a selection receipt or claims HTTP/list/search success.

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests/unit -p test_knowledge_upload_probe.py -v
.\.venv\Scripts\python.exe -m pytest tests/unit tests/diagnostic tests/f9 tests/f4/test_f4_case1_writer.py::test_write_f4_result_execution_context_records -o cache_dir=out/pytest-cache --basetemp=out/pytest-issue2-offline
```

Results (2026-10-06): unittest 13 PASS; focused offline pytest 36 PASS plus 2 subtests. Initial broader collection required bs4; after dependency setup, the broader run had 34 PASS and 6 setup errors (temp-directory access and browser executable path). The focused command above resolved the temp path and includes all offline cases from that run. Four browser-dependent cases remain unverified and are excluded from the offline command. No existing tests were removed.

Live verification follows `docs/operation/KnowledgeUpload_DOM_Observation_v0.1.md`. Chromium reached the login screen with the unchanged LoginPage, but login completion failed with `Error`; cause is undetermined and registration DOM was not observed. Do not equate this with bad credentials or a locator mismatch without more evidence. No upload occurred. Without successful authentication/real DOM, registration navigation and file selection remain unimplemented. Existing env, PageObjects, CI, smoke and synthetic HTML suites are unchanged; no PageObject locators are introduced.

Post-push E2E CI run `37434783824` failed in unchanged LoginPage.wait_for_login_success because string JavaScript evaluation violated site CSP. The offline PASS results do not establish functional live login. Shared PageObject remediation needs its design/PENTA review; it is outside the implemented probe boundary. The separate local failure is not independently diagnosed as CSP.
