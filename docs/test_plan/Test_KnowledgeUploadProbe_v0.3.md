# Test_KnowledgeUploadProbe_v0.3 (2026-10-09)

Scope: Issue #2 / Draft PR #1; observed DOM from Issue #2 comment `6073127818`.

## Offline / no external request

```powershell
.\.venv\Scripts\python.exe -m pytest tests/unit/test_private_knowledge_page.py tests/unit/test_knowledge_upload_probe.py tests/unit/test_login_wait_csp.py -q
```

**Tests written (not a claim of execution):**
- Exact observed My Drive path after login using configured HTTPS origin; reject invalid origin without navigation.
- Role-based New button and upload menu item have count=1; absence/ambiguity stops.
- Distinguish selected file input from folder-selection `webkitdirectory` input, exact `accept`, `multiple`, and absence of directory flags; changed/multiple matches stop.
- `inspect_controls()` clicks **only** New, reads DOM attributes, never invokes menu-item click, chooser, file selection or HTTP.
- `--check-observed-controls` requires `--synthetic --inspect-ui`; existing `--inspect-ui` and `--confirm-upload` boundary unchanged.
- No real file selection is exposed through CLI; mock-only `select_synthetic_file` tests assert missing literal `UPLOAD`/wrong bytes -> zero UI effects; a folder chooser -> no `set_files`; an exact chooser -> **one mocked** `.txt` selection returning `selected_unverified`.
- Existing synthetic conversion, login config, CSP URL wait and receipt semantics remain covered by prior offline tests.

## Live verification gate (NOT part of the above)

```powershell
.\.venv\Scripts\python.exe scripts/knowledge_upload_probe.py data/knowledge_upload/synthetic.md --synthetic --inspect-ui --check-observed-controls
```

Requires an authorized operator on an internet-connected Windows test PC and locally configured secrets (GitHub Actions Secrets do not propagate). This option may **navigate to My Drive and click the New menu**, but is read-only and must not select a file. A successful read-only check prints a control-confirmation message, then pauses in the Inspector and ultimately returns exit code `2` because upload is deliberately disabled.

**STOP** on missing/ambiguous controls or different file-input attributes. Never switch to guessed selectors. The URL direct-navigation assumption and real Playwright file-chooser linkage remain unverified until observed.

The next live gate, **only with new human authorization**, is selecting exactly one byte-identical synthetic `.txt` while separately assessing immediate HTTP upload, server acceptance, registration and search. No real data, replacement, deletion, Ready or merge is within scope.
