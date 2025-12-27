# 📘 **Design_env_v0.2.3 — Environment Layer Specification**

**Version:** v0.2.3
**Status:** Clarifying Update（non-breaking）
**Scope:** `config/env.yaml`, `.env*`, `src/env_loader.py`
**Upstream Documents:**

* PROJECT_GRAND_RULES v4.2
* Debugging_Principles v0.2
* Responsibility_Map v0.1
* Design_ci_e2e_v0.1
* Design_env_v0.2（superseded, backward-compatible）
* Startup Template v3.1

> **Note:**
> English text is binding (formal specification).
> Japanese text is non-binding explanatory commentary.

---

# --------------------------------------------

# 0. Annotated Diff (v0.2.2 → v0.2.3)

# --------------------------------------------

## **(English — Binding)**

Design_env_v0.2.3 introduces clarifications without changing runtime behavior:

1. **Structure Integrity Rule** added

   * Profile schemas (key sets) are immutable without a design-document update.
   * AI agents must not rename, add, or delete configuration keys.

2. **Expanded AI Prohibition List**

   * Explicit ban on schema drift.

3. **Traceability Improvement**

   * Introduced this Annotated Diff section.

4. **Minimal Binding Example added**

   * Prevents YAML misinterpretation by AI.

## **（日本語 — 非拘束）**

本改訂では挙動は一切変えず、次の4点を追加しました：

* **スキーマ不変ルール**
* **AIの key rename / 削除 / 追加 禁止を明文化**
* **差分セクションを追加**
* **AI誤読防止のため最小構成例を binding として固定**

---

# --------------------------------------------

# 1. Purpose

# --------------------------------------------

## **(English — Binding)**

The purpose of Design_env_v0.2.3 is to clarify schema integrity, strengthen AI-misbehavior prevention, and improve design-document traceability while remaining fully compatible with v0.2 and v0.2.2.

## **（日本語 — 非拘束）**

v0.2.3 の目的は、**スキーマの不変性の明確化・AI事故防止・文書追跡性の向上** です。

---

# --------------------------------------------

# 2. Background

# --------------------------------------------

## **(English — Binding)**

Design_env_v0.2 established profile-based configuration, secret loading, and placeholder resolution.
However, AI agents sometimes misinterpreted the schema and attempted unauthorized modifications.
This update fixes those ambiguities without altering behavior.

## **（日本語 — 非拘束）**

v0.2 までは動作は正常でしたが、AI が key の rename や profile 追加などを勝手に行う事故がありました。
v0.2.3 はその曖昧部分を埋めるための “安全性補強版” です。

---

# --------------------------------------------

# 3. Requirements

# --------------------------------------------

## 3.1 Functional Requirements

*(Identical to v0.2 / v0.2.2 — no behavioral changes)*

## **(English — Binding)**

The Environment Layer MUST:

1. Use `config/env.yaml` as the single source of truth.
2. Support multiple named profiles.
3. Load secrets from:

   * `.env`
   * `.env.<profile>`
   * `os.environ` (authoritative)
4. Resolve `${VARNAME}` using environment variables only.
5. Provide:

```python
def load_env(env_path: str = "env.yaml") -> Tuple[Dict[str, Any], Dict[str, Any]]
```

Returning `(profile_cfg, options)`.

## **（日本語 — 非拘束）**

機能要件は v0.2 と完全一致：
`env.yaml` が唯一の構成源で、`.env*` と環境変数を使って `${...}` を解決し、`load_env()` は `(profile設定, options)` を返します。

---

## 3.2 Non-Functional Requirements (with new clarifications)

## **(English — Binding)**

The Environment Layer MUST:

1. Remain backward-compatible with v0.2.
2. Follow GRAND_RULES v4.2 (No Speculation, No Silent Override).
3. Follow Debugging_Principles v0.2 (use primary evidence).
4. Remain decoupled from UI, PageObjects, and CI logic.

### **Structure Integrity Rule (NEW in v0.2.3)**

1. The schema (key set) of each profile and the `options` section is **immutable** unless explicitly modified in a design-document update.
2. AI agents MUST NOT rename, remove, or add configuration keys.
3. AI agents MUST NOT introduce new top-level sections or fields unless the change is approved in a new version of Design_env_x.x.
4. env_loader MUST NOT modify schema during runtime.

## **（日本語 — 非拘束）**

非機能要件は v0.2 と同一に加え：

### **スキーマ不変ルール（今回追加）**

* profile 配下の key は設計書改訂なしに変更禁止
* AI による rename / 削除 / 追加は禁止
* env_loader が実行時に key を書き換えることも禁止

---

# --------------------------------------------

# 4. Architecture & Flow

# --------------------------------------------

## 4.1 Responsibility Boundaries

## **(English — Binding)**

Environment Layer **is responsible for**:

* Profile definition
* Secret loading
* Placeholder resolution
* Returning typed config dicts

Environment Layer **is NOT responsible for**:

* Browser/page creation
* DOM/locator logic
* CI skip/fail logic
* Test orchestration

## **（日本語 — 非拘束）**

環境レイヤーは **設定の読み込み・加工** のみを担当し、
**テスト制御・CI判定・PageObjectロジックは関与外** です。

---

## 4.2 Profile Selection Flow

## **(English — Binding)**

Flow remains identical to v0.2:

1. Read `env.yaml`
2. Determine profile:

```
if ENV_PROFILE is set → use ENV_PROFILE
else → use env.yaml["profile"]
```

3. Validate profile existence
4. Load `.env` → `.env.<profile>` → environment variables
5. Resolve placeholders
6. Return `(profile_cfg, options)`

### **Schema Freeze Note (NEW)**

During resolution, `env_loader` MUST NOT alter the schema.

## **（日本語 — 非拘束）**

profile 選択フローは従来通り。
今回追加された注意点：
**env_loader は構造を書き換えてはならない（Schema Freeze）**

---

# --------------------------------------------

# 5. Error Handling

# --------------------------------------------

## **(English — Binding)**

* Invalid profile → `ValueError`
* Missing placeholder secret → `MissingSecretError`
* No silent defaults are allowed.
* No profile auto-fallback.

## **（日本語 — 非拘束）**

* プロファイルがなければ ValueError
* 環境変数がなければ MissingSecretError
* デフォルト補完は禁止
* 自動で別プロフィールに切り替える挙動も禁止

---

# --------------------------------------------

# 6. CI / LGWAN Behavior

# --------------------------------------------

## **(English — Binding)**

* Environment Layer does NOT detect CI.
* CI provides secrets via environment variables.
* Environment Layer must NOT create a “ci” profile automatically.
* LGWAN execution is just another profile selection.

## **（日本語 — 非拘束）**

CI も LGWAN も **検知しない**

* CI が env_loader を“変えようとしない”
* env_loader も CI を“特別扱いしない”
* LGWAN は単なる profile として扱う

---

# --------------------------------------------

# 7. Tests

# --------------------------------------------

## **(English — Binding)**

Tests MUST validate:

1. Correct profile selection
2. Correct placeholder resolution
3. Correct MissingSecretError messages
4. CI compatibility (no `.env*`)
5. **(NEW)** No schema drift:

   * No unexpected keys appear
   * No key renaming occurs

## **（日本語 — 非拘束）**

テストは以下も検証対象になりました：
**key が勝手に増減していないこと（スキーマ不変性テスト）**

---

# --------------------------------------------

# 8. AI Prohibitions (Expanded)

# --------------------------------------------

## **(English — Binding)**

AI agents MUST NOT:

1. Create, rename, or delete profiles.
2. Create, rename, or delete configuration keys.
3. Introduce fallback defaults for missing secrets.
4. Modify error-handling semantics.
5. Embed CI logic into env_loader.
6. Modify env.yaml or env_loader without a design-document update.
7. Infer or guess values not present in secrets or env.yaml.

## **（日本語 — 非拘束）**

AI 禁止行為の追加：

* profile の追加・名前変更・削除
* key の rename / 削除 / 追加
* 推測による値の補完
* エラー握りつぶし
* env_loader 内に CI ロジックを埋め込む行為
* 設計書改訂なしのコード変更

---

# --------------------------------------------

# 9. Minimal Binding Example (NEW)

# --------------------------------------------

## **(English — Binding)**

This example is normative. AI MUST NOT alter its schema:

```yaml
profile: "internet"

profiles:
  internet:
    url: "${QOMMONS_URL}"
    username: "${QOMMONS_USERNAME}"
    password: "${QOMMONS_PASSWORD}"

options:
  log_base_dir: "logs"
```

## **（日本語 — 非拘束）**

AI 誤読を防ぐため、この最小構成例を binding として固定します。
スキーマの書き換えは禁止。

---

# --------------------------------------------

# 10. Future Work (Non-binding)

# --------------------------------------------

## **(English — Binding)**

Future breaking features (v0.3+) require a new design document.

## **（日本語 — 非拘束）**

v0.3 以降の機能追加は、必ず専用設計書を作成してから実施します。

---
