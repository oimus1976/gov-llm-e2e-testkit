# **PROJECT_GRAND_RULES v4.3**

*(English = Binding / Japanese = Non-binding Supplement)*
最終更新：2025-12-12

---

# **0. Language Binding Rule（英語拘束／日本語補助）**

**EN (binding):**
Only the **English text** of this document has *normative and binding force* over AI behavior.
AI must **never** use the Japanese text for inference, rule interpretation, or behavioral decisions.
Japanese text exists **solely for human understanding**.

**JA（補助・AI非参照）:**
本書で拘束力を持つのは英語部分のみ。
日本語部分は人間向け補足であり、AIは日本語を基に推論してはならない。

---

# **1. Purpose（目的）**

**EN (binding):**
This document defines the supreme governance rules for the **gov-llm-e2e-testkit** project.
Its purpose is:

1. Ensure consistency, reliability, and long-term maintainability.
2. Constrain AI behavior to prevent unintended actions.
3. Provide a clear hierarchy of rules and documents.
4. Guarantee reproducible development and CI stability across INTERNET and LGWAN.

**JA:**
本書はプロジェクトの最上位統治文書であり、AI行動の一貫性とCI安定性を保証する。

---

# **2. Rule Hierarchy（規範階層）**

**EN (binding):**
AI must always follow this hierarchy, in this order:

1. **PROJECT_GRAND_RULES (this document)**
2. **Debugging_Principles v0.2**
3. **Design Documents (Design_XXX.md)**
4. **PROJECT_STATUS**
5. **CHANGELOG**
6. **Test Code (source of expected behavior)**
7. All other information

Deviation from the hierarchy is strictly prohibited.

**JA:**
AIはこの順でルールを解釈し、逆転させてはならない。

---

# **3. AI Compliance Rules（AI行動準拠規範） v1.0（C2 完全準拠）**

## **3.1 Context Fidelity（文脈尊重義務）**

**EN (binding):**

AI must:

* Follow GRAND_RULES, Debugging_Principles, Design Documents, STATUS.
* Avoid independent reinterpretation.
* Not fill missing details unless explicitly provided.

## **3.2 Forbidden AI Behaviors（AI禁止行動）**

AI must **never**:

* Create or modify profiles not present in env.yaml.
* Modify env.yaml or e2e.yml without explicit human instruction.
* Make speculative assumptions.
* Propose code changes not described in design documents.
* Ignore STATUS and start unrelated tasks.
* Skip PENTA invocation when required.
* Debug without confirming primary evidence (code/DOM/logs/CI).

## **3.3 Debugging Principles Compliance**

AI must fully comply with Debugging_Principles v0.2:

* No speculation
* Verify primary evidence
* Enumerate hypotheses
* Ensure reproducibility

## **3.4 Evidence Obligation**

AI must require and use first-hand evidence when something is uncertain:

* Code
* Logs
* DOM
* CI output
* Screenshots

## **3.5 No Speculation（推測禁止）**

AI must not infer:

* Missing configuration values
* Undocumented behavior
* Implicit system constraints

## **3.6 No Silent Overrides（黙示的上書き禁止）**

AI may **not** modify:

* env.yaml
* e2e.yml
* Design Documents

unless explicitly requested.

## **3.7 Environmental Constraints**

* LGWAN: no external network calls
* CI: fallback only when Secrets are absent
* INTERNET: normal-speed assumptions

AI must never rewrite switching logic without instruction.

## **3.8 Profile Non-Creation Rule**

AI must not propose or generate nonexistent profiles:

✗ Example: auto-generating a “ci” profile
✓ AI may only use profiles explicitly defined by the user.

---

# **4. Documentation Standards（設計書規範）**

## **4.1 Versioning Policy**

* All Design Documents must use versioned filenames:
  *Design_X_v0.1.md → v0.2 → v0.3 …*
* Older versions must remain permanently stored.
* A `Design_X.md` alias may represent "latest."
* Breaking changes require MINOR version increment.
* Update flow is strictly:
  **Design → Implementation → CI → STATUS → CHANGELOG**

## **4.2 Document Structure**

All design docs must follow:

1. Purpose
2. Background
3. Requirements
4. Architecture / Flow
5. Exceptions
6. Tests
7. Extension Plan

## **4.3 Update Flow**

AI must not skip any element of the update chain.

---

# **5. Quality Assurance Principles（品質保証）**

## **5.1 Smoke Test Inviolability**

Smoke Test:

* Must always exist
* Must not be renamed or removed
* Must guarantee “at least one test runs” to avoid pytest exit-5

## **5.2 CI Exit-5 Prevention**

CI must always run ≥1 test.
If smoke is skipped, pipeline must fail explicitly.

## **5.3 SKIP_E2E Behavior**

* When SKIP_E2E is set,
  smoke test must still run minimal checks, not 0 tests.

## **5.4 Synthetic HTML Requirements**

* Synthetic HTML must always pass validation.
* Changes to synthetic suite require PENTA review.

---

# **6. File / Directory Structure（ファイル構成原則）**

```
/docs                → Design / Governance documents  
/tests               → Playwright + pytest tests  
/data                → RAG datasets  
/config              → Environment profiles  
/logs                → Test artifacts (Git-ignored)  
/scripts             → Human-invoked execution scripts (QA / verification entrypoints)  
.github/workflows    → CI definitions  
PROJECT_STATUS.md  
CHANGELOG.md  
README.md
```
### **scripts/ Directory Rule（Execution Scripts）**

**EN (binding):**

* `scripts/` contains **human-invoked execution entrypoints** used during QA or verification phases.
* Scripts under this directory:

  * Must **not** be executed automatically by CI or pytest.
  * May call functions from `src/`, but must **not** define reusable library APIs.
  * Must represent **formally designed assets**, not temporary experiments.
* `scripts/` is distinct from `sandbox/`, which is reserved for disposable or exploratory code.

**JA（補助）:**

* scripts/ は、人が明示的に実行する QA・検証用スクリプトの置き場。
* CI や pytest の自動実行対象にはならない。
* src の機能を呼び出すことはできるが、再利用前提の API は定義しない。
* 設計書を持つ正式資産のみを置く（sandbox とは明確に区別）。
---

# **7. Locator Principles（UI識別統一原則）**

* Must follow Locator_Guide_v0.2
* Test code must never contain raw locators
* PageObjects only
* No XPath
* Prefer roles over CSS

---

# **8. Environment Operation Rules（LGWAN / INTERNET）**

* INTERNET: fast, full-feature mode
* LGWAN: restricted, timeout-aware mode
* Switching must be controlled by env.yaml only

---

# **9. Prohibitions（禁止事項：AI＋人間）**

### **AI prohibited behaviors**

(Section 3.2 fully applies)

### **Human prohibited actions**

* Editing CI without design
* Releasing code without updating STATUS
* Running LGWAN tests without manual operational steps
* Removing synthetic HTML tests

---

# **10. Update Policy（更新手順の厳格化）**

* All updates require PENTA review if they impact:

  * env
  * CI
  * PageObjects
  * smoke test
* GRAND_RULES updates require explicit version tagging.

---

# **11. Position in Project Architecture（上下関係）**

Hierarchy:

1. **GRAND_RULES（本書）**
2. Startup Template（layer 2）
3. PROJECT_STATUS（layer 3）
4. Design Documents（layer 4）
5. Source Code（layer 5）
6. Tests（layer 6）

GRAND_RULES overrides all others.

---
