# Design_LoginPage_v0.3.2 — CSP-compatible login-success wait

Date: 2026-10-07  
State: proposed limited PageObject correction; separate from Draft PR #1  
Supersedes only the login-success waiting method in the implemented sync `LoginPage v0.3.1`; preserve `Design_LoginPage_v0.2.md`.

## 1. Purpose
Remove the reproducible Content Security Policy (CSP) `unsafe-eval` error from login-success detection without changing authentication, locator selection, timeouts or error evidence behavior.

## 2. Background and primary evidence
- Current `tests/pages/login_page.py` uses `page.wait_for_function("window.location.href.includes('/chat')", timeout=self.timeout)`.
- The first-party E2E CI run `37434783824`, job `112173829013`, failed in this exact call, with Playwright `EvalError` stating that JavaScript string evaluation violates `script-src` because `unsafe-eval` is not allowed. Local headed-login failure has **not** been independently diagnosed.
- Existing `ChatSelectPage.open_ai()` already uses `page.wait_for_url(re.compile(...), timeout=self.timeout)`; archived `docs/archive/debug/vscode_logs/2025-12-17_f4-login-wait.md` proposed a prior URL-wait switch but its tests were not run. Accept both `/chat` and `/chat/<id>` login destinations; avoid `/chatty` false positives.
- Governance: `PROJECT_GRAND_RULES v4.3`, `Debugging_Principles v0.2`, `Locator_Guide v0.2`, existing `Design_LoginPage_v0.2`. PageObject changes require PENTA impact review.

## 3. Requirements
- Keep `LoginPage.login()`, `open()`, field/button locators, `safe_*` calls, configuration, the `evidence_dir` error path, `self.timeout` and public method signatures unchanged.
- Replace only JavaScript string evaluation with Playwright's native `page.wait_for_url(re.compile(r"/chat(?:/|$|[?#])"), timeout=self.timeout)`; this does not inject or eval JavaScript. A successful return means URL matched, **not** that authentication or account permissions were independently verified.
- Do not change `BasePage`, smoke tests, CI workflow, `env.yaml` or secrets. No CSP bypass or new login fallback.
- Include self-contained offline tests with a fake page; do not execute live QommonsAI authentication in the offline suite.

## 4. Architecture / Flow
`LoginPage.login` -> safe_fill username/password -> safe_click button -> `wait_for_login_success` -> `page.wait_for_url` matching URL route segment `/chat` or `/chat/<id>` -> exit. If the wait raises, retain existing conditional `collect_evidence(evidence_dir, "login_failed")` and re-raise unchanged.

## 5. Exceptions
- Unsupported actual login destinations or authentication failures still raise/timeout; do not misstate those as CSP failures.
- An operator-authenticated DOM may contain private data. Offline tests use fictional URLs and do not persist browser content.
- Existing BasePage evidence capture is outside this minimal change; changing its behavior requires separate review.

## 6. Tests
- Verify menu URL, chat-id URL, trailing slash/query URLs match and lookalike routes do not.
- Verify `page.wait_for_url` invoked once with the configured timeout and that `wait_for_function` is never called.
- Verify timeouts/errors re-raise and existing optional evidence collection behavior.
- Re-run available existing tests/CI and distinguish CI result from offline checks.

## 7. Extension plan
Do not touch Private Knowledge upload selectors before capturing sanitized real registration DOM. After this change is independently reviewed/merged, update Draft PR #1 from main and retry login/Inspector with the approved synthetic sample only.

## PENTA impact review (five checks; pre-change)
1. **Scope / design:** URL transition already defines the implemented LoginPage success condition; use native URL wait, preserving its interface. The v0.2 design's async DOM example does not match existing v0.3.1 sync behavior; this change intentionally does not reinterpret that broader design.
2. **Regression:** `/chat` and `/chat/<id>` both accepted; unrelated routes rejected. Existing smoke and F4 call sites stay unchanged. Timeout and failure evidence preserved.
3. **Security / privacy:** No eval injection, credentials displayed, CSP weakening, DOM capture additions or network calls. Existing evidence capture risks are unchanged, not newly solved.
4. **Environment / operations:** Reuse the configured timeout and existing Playwright API; internet/LGWAN configuration and CI workflow untouched. Real site behavior may still differ.
5. **Verification / rollback:** Offline mock tests are required; CI smoke remains the functional gate. Revert one line and the `import re` if a regression is identified. No merge or deployment is authorized by this review alone.

**Review disposition:** Narrowly suitable for a Draft PR and validation. Do not claim PENTA's independent organizational sign-off or functional success without separate evidence.
