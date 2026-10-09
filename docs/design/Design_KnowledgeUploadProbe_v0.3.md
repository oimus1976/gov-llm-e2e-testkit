# Design_KnowledgeUploadProbe_v0.3 — observed Private Knowledge controls

Date: 2026-10-09
State: Draft PR #1, implementation after operator DOM observation; real file upload NOT authorized
Supersedes: v0.2 only for registration navigation/control identification. Preserve v0.1/v0.2.

## 1. Purpose

Build the smallest evidence-grounded PrivateKnowledgePage for QommonsAI My Drive and an operator-invoked **read-only** control check. Keep live file selection disabled in the CLI pending a separate operator approval; keep all credentials and municipality data outside Git.

## 2. Background / primary evidence

Issue #2 comment `6073127818` records first-hand operator screenshots, exact copied outerHTML fragments and native Windows file chooser behavior on 2026-10-09.

Observed:
- Signed-in `/chat` -> Private Knowledge navigation -> My Drive URL `/private-knowledge/my-drive`.
- New button: `<button type="button" aria-haspopup="menu" aria-expanded="true" ...>...新規</button>`. Its Radix-generated ID is *not* a stable locator.
- Menu item: `<div role="menuitem"...>...ファイルをアップロード</div>`.
- File input: `<input accept=".txt,.pdf,.docx,.html,.csv,.pptx,.xlsx,.md,.mp3,.wav,.png,.jpg,.jpeg" multiple="" class="hidden" type="file">`.
- A distinct `input[type=file]` with `webkitdirectory` handles folder selection.
- Clicking the upload menu item opens the OS file chooser, which the operator canceled without selecting.

Unobserved: DOM for Private Knowledge left-navigation control, whether a direct URL visit works in automation, specific menu-to-input wiring, owner form, auto-upload-on-selection, HTTP acceptance, registration/list/index/search, duplicates.

## 3. Requirements

- Add `tests/pages/private_knowledge_page.py` only; preserve existing `LoginPage`, `BasePage`, `ChatSelectPage`, chat, environment/profile logic, CI and Smoke Test.
- Use the observed My Drive path for navigation **after login** (direct URL navigation is not a claim that the navigation menu's DOM was observed). Enforce same origin as the existing configured URL, fail on malformed/non-HTTPS base URL, wait for target URL.
- Use role/name: `get_by_role("button", name="新規", exact=True)` and `get_by_role("menuitem", name="ファイルをアップロード", exact=True)`; require exactly one of each. Never use dynamic Radix IDs or guessed XPath.
- Enumerate observed `input[type="file"]` nodes and require exactly one file input matching the exact observed accept list, `multiple`, and no `webkitdirectory` or `directory`. Fail closed for unexpected/ambiguous DOM. Do not assume a separate HTML registration form exists.
- Add `--check-observed-controls` as a read-only extension **requiring** `--synthetic --inspect-ui`: login -> My Drive -> click New only -> check menu and file input attributes -> Inspector pause. No click of upload menu item, file selection, HTTP upload, chat send, deletion or replacement; do not print raw DOM.
- Keep existing `--inspect-ui` default behavior unchanged and `--confirm-upload` failing closed.
- Prepare a separated `select_synthetic_file` method for a *future, separately authorized* call only. It is **not connected to the CLI**. Require literal operator confirmation `UPLOAD`, validate the exact bundled Markdown sample and matching byte-identical exported `.txt` before touching UI; use `expect_file_chooser` on the observed menu item, revalidate the actual chooser element's attributes, and call `set_files` on **one** synthetic `.txt` only. Return `selected_unverified` and never imply HTTP acceptance.
- No new `.env` / profile, raw screenshots, authenticated DOM dumps, credentials, or real municipality data.

## 4. Architecture / flow

Existing `scripts/knowledge_upload_probe.py` -> `src.knowledge_upload_probe.main()` -> `load_login_config()` -> optional export -> `inspect_ui(config, check_observed_controls=True)` -> existing `LoginPage` -> `PrivateKnowledgePage.open_my_drive()` -> `inspect_controls()` -> `page.pause()`.

The input is hidden, and clicking the menu item launches the OS chooser. The separated selection method uses Playwright `expect_file_chooser()` for the click-to-input relationship instead of guessing an onClick hook. This is an *untested implementation hypothesis* until authorized real observation. No CLI option calls the selection method in this version.

## 5. Exceptions / explicit stop

Missing or ambiguous menu controls; changed file input attributes; unexpected folder input; invalid URL; changed synthetic sample/target; missing literal confirmation; any browser exception: STOP without fallback. Inspect mode catches browser exceptions and prints only generic messages. `--inspect-ui` and `--check-observed-controls` exit code 2 remains the existing "upload not implemented" state even after successful observation.

## 6. Tests and PENTA-style impact review

Offline test matrix: `docs/test_plan/Test_KnowledgeUploadProbe_v0.3.md`. Include input-discrimination, uniqueness, same-origin My Drive URL, zero-file-selection read-only mode, missing confirmation, forged target, chooser mismatch, and a **mock-only** demonstration of one allowed `set_files`. Real HTTP requests never execute in tests.

Five impact dimensions (author assessment, **not independent PENTA approval**):
1. **PageObject boundaries**: new class owns only Private Knowledge UI. Existing PageObjects untouched.
2. **Security/data**: fixed sample bytes/path and independent confirmation guard before selecting; no raw secret output or live upload by CLI.
3. **Regression/CI**: old `--inspect-ui` and Smoke Test untouched, focused mocks added; new offline unit cases not automatically exercised by existing CI.
4. **DOM correctness**: role/name and exact copied attributes; direct My Drive URL and chooser linkage still live-unverified and must fail closed.
5. **Operations/governance**: explicit operator command and isolated pending approval; Draft PR #1 only; no Ready/merge/main update.

Review remains provisional until independent review and the separate authorization for live file selection.

## 7. Extension plan

Run the read-only command on an approved Windows test host, record whether My Drive and controls are found without file selection, and return only sanitized outcomes. After explicit human approval for selecting exactly the synthetic file, connect the guarded selection method via a separate reviewed CLI gate. Observe network acceptance, My Drive list registration and searchability independently; never modify existing entries to test duplicate behavior.
