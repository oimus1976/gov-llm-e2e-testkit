# Test_KnowledgeUploadProbe_v0.5 — observed results vs unrun checks (2026-10-09)

Scope: Issue #2 / Draft PR #1, synthetic `synthetic.txt` one-file MVP. This is a retrospective evidence record and follow-on review plan; **not authorization to re-upload or send another chat**. Test plan v0.4 and earlier versions remain preserved.

## 1. Executed / reported evidence

| Stage | Evidence | Result and limitation |
| --- | --- | --- |
| Synthetic source / gate | Existing committed sample and v0.4 unit cases; GitHub code reviewed | Byte-exact sample required; no arbitrary business file path |
| DOM/navigation read-only check | Issue #2 comments [6073127818](https://github.com/oimus1976/gov-llm-e2e-testkit/issues/2#issuecomment-6073127818), [6073651368](https://github.com/oimus1976/gov-llm-e2e-testkit/issues/2#issuecomment-6073651368) | Operator-reported live `Read-only check PASS`; no file selected in this check |
| Windows regression tests | [6076752013](https://github.com/oimus1976/gov-llm-e2e-testkit/issues/2#issuecomment-6076752013) | Focused four-file pytest operator report `[100%]` and exit 0 after v0.7.37 fix; individual pass count not captured |
| Single-file selection | [6077190221](https://github.com/oimus1976/gov-llm-e2e-testkit/issues/2#issuecomment-6077190221) | Separately authorized `UPLOAD synthetic.txt`, Playwright `selected_unverified`; local receipt retained only on test PC |
| My Drive list / persistence | [6077190221](https://github.com/oimus1976/gov-llm-e2e-testkit/issues/2#issuecomment-6077190221), [6077224107](https://github.com/oimus1976/gov-llm-e2e-testkit/issues/2#issuecomment-6077224107) | Operator saw filename; persisted after F5 |
| Learning UI | [6077224107](https://github.com/oimus1976/gov-llm-e2e-testkit/issues/2#issuecomment-6077224107) | Operator saw `学習中` -> `学習済み`; not backend inspection |
| Private Knowledge answer | [6078368762](https://github.com/oimus1976/gov-llm-e2e-testkit/issues/2#issuecomment-6078368762) | Manual only; single `synthetic.txt` selected, Web OFF, answer not supplied in question, returned exact `SYNTHETIC-KNOWLEDGE-0001` |
| Existing GitHub Actions | [run 37882053878](https://github.com/oimus1976/gov-llm-e2e-testkit/actions/runs/37882053878) | Completed/success for **existing Smoke**; does not establish focused unit suite CI coverage |

## 2. Not executed / cannot claim
- HTTP status / upload request body acceptance, backend index implementation, duplicate-name or replacement behavior.
- Automated browser selection of the already-registered knowledge in chat, automatic chat question/answer check, citation link clickability.
- Other file types, multi-file cases, full Windows/browser regression suite or repeatability of a second upload.
- Independent re-execution of operator's Windows tests by this documentation update.

## 3. Acceptance criteria — avoid expanding MVP implicitly
- **One-file registration MVP evidence available:** synthetic file selected via the controlled Playwright gate, human-observed listing persisted after reload and learning UI completed, manual targeted question answered correctly. This is an *evidence statement*, not human PR acceptance.
- **Not yet established:** server HTTP-level proof and automated search/answer regression. These require separate explicit scope and evidence, not a second upload.
- Retain the observed risk: `synthetic.txt` is already present, so v0.4's no-duplicate preflight condition now fails. **Do not run the original live upload command again**.

## 4. Next review and regression checks
1. Inspect current PR HEAD, code and versioned design; assess module responsibility, operator authorization boundaries, input/chooser uniqueness, failure handling, secrets and no auto-retry.
2. If code changes become necessary, run focused offline Windows tests with recorded summary, `git diff --check`, then inspect CI run separately. A successful Smoke run must not be reported as new-unit-suite coverage.
3. If separately approved later, design a **read existing knowledge only** retrieval/answer automation from *observed* DOM; perform no upload, replacement, deletion or chat send by default.

Historic pre-execution instructions remain in v0.4; execution requires new separate human authorization. PR #1 remains Draft until human decision.
