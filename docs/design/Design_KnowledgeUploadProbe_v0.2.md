# Design_KnowledgeUploadProbe_v0.2

Date: 2026-10-06
State: Issue #2 implementation; live DOM observation pending
Previous: Design_KnowledgeUploadProbe_v0.1.md (retained)

Observed blocker: post-push E2E CI run `37434783824` shows site CSP rejecting the unchanged LoginPage string-based `wait_for_function`. Successful live login/Inspector observation is therefore not verified. Shared PageObject remediation requires the existing design/PENTA process; this isolated probe does not change it or bypass CSP. Use normal operator-authenticated browser observation to obtain the missing registration DOM.

## Purpose
Reuse `src.env_loader.load_env()` and the unchanged `tests.pages.login_page.LoginPage` for the Private Knowledge probe in Draft PR #1. GitHub Issue #2 is the scope authority.

## Background
The v0.1 probe hard-coded a public URL, required manual login, and selected a generic file input without evidence of its meaning. No live upload-screen DOM is available in the repository. ChatSelectPage selects a chat, not a knowledge registration screen; do not reuse it for registration navigation.

## Requirements
- Keep env.yaml, .env files, profile selection, secret precedence, LoginPage, BasePage, chat automation and CI unchanged. Call load_env without custom profile or fallback values.
- Fail on missing/invalid login configuration before launching a browser. Do not print credentials, resolved configuration, raw browser exceptions, DOM, or HTTP bodies.
- Restrict the CLI to the byte-exact checked-in synthetic sample, including when `--synthetic` is supplied. Keep Markdown canonical, with exclusive UTF-8 .txt export and no divergent overwrite.
- Provide `--inspect-ui` to log in automatically in a visible Playwright browser and pause in the Inspector for operator observation. Do not select a file, click an upload button, send a chat, or create a selected receipt in this mode.
- Until real DOM evidence exists, the upload path fails closed. Retain `--confirm-upload` as an explicit upload gate; it does not authorize unsupported automation.
- Do not create a PrivateKnowledgePage with guessed locators. Navigation/file selection are deferred until the operator observes and redacts the real UI.

## Architecture / flow
The script is an entrypoint only, delegating reusable code to `src.knowledge_upload_probe`. Direct script invocation adds the repository root to the import path and uses the repository as working directory, so existing relative env resolution remains deterministic. No environment values are changed.

`--inspect-ui`: synthetic sample validation -> load_env -> required-field validation -> byte-identical .txt preparation -> visible Chromium with configured page/browser timeouts -> LoginPage.open/login -> Playwright Inspector pause -> close browser -> exit 2 (upload automation pending).

Without inspection mode: require both synthetic/upload gates, validate the sample, report the unavailable upload implementation and exit 2 before browser or export side effects. Exit 2 also indicates missing settings/dependencies/browser/authentication; diagnostics must not expose secret values.

## Exceptions
Invalid UTF-8, empty/missing/non-Markdown input, modified sample, divergent .txt, missing fields, loader failures or login failures stop. No implicit CI dummy credentials or profile fallback. Close browser after login or Inspector failure. No screenshot/DOM/network dump is automatically saved because authenticated pages may contain private data.

## Tests
See `docs/test_plan/Test_KnowledgeUploadProbe_v0.2.md`. Preserve conversion/receipt/gate coverage from v0.1; replace the obsolete generic-input test with an assertion that unobserved upload is disabled. Add offline tests for exact-sample enforcement, loader delegation, fail-before-browser configuration validation, LoginPage call order, timeouts, cleanup and redacted failures. No live browser invocation from pytest/CI.

## Extension plan
Run the inspection procedure in `docs/operation/KnowledgeUpload_DOM_Observation_v0.1.md`. Only after actual navigation and upload DOM observation, add PrivateKnowledgePage, restore the final literal `UPLOAD` confirmation immediately before file selection, and independently record file selection, HTTP acceptance, list registration and searchability. Same-name replacement remains unverified. Ready/merge/main updates and real municipal uploads are outside this task.
