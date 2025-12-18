# CHANGELOG — gov-llm-e2e-testkit

全ドキュメント・設計書・仕様変更の履歴を記録する公式 CHANGELOG です。
本プロジェクトは Keep a Changelog に準拠し、バージョンは日付ベース＋プロジェクト内バージョンで管理します。

本ファイルは、本プロジェクトにおける
**設計・実装・運用上の意思決定の履歴**を記録する。

- バージョン番号は PROJECT_STATUS と同期する
- 単なるコード変更ログではなく、
  **「何が確定し、何が前提になったか」**を残す

---

## v0.6.4 (2025-12-17)

### Clarified
- F4 フェーズの責務を
  「RAG 前処理（HTML→Markdown）の是非を判断する」から
  **「他プロジェクトが判断に利用可能な試験データ（試金石）を提供する」**
  へ明確に是正。
- F4 v0.2 を、
  フェーズゴールを満たす **最初の完了マイルストーン**
  として位置づけを明文化。

### Changed
- Roadmap を v1.2 として更新。
  - F4 を「入力差分影響の観測・試験データ提供フェーズ」と再定義。
  - F6（LGWAN 対応）を
    サービス事業者提供待ちの **保留（Blocked）フェーズ**として明示。

### Notes
- 本更新は責務・位置づけの是正のみであり、
  既存のテスト基盤（F1–F3）および
  F4 v0.1 の評価基準・運用ルール自体は変更していない。

### Verified
- F4 v0.2 試金石データ（Raw / Execution Context / Derived Summary）について、
  JSON Schema Draft 2020-12 によるバリデーションを実施し、すべて VALID を確認。

### Completed
- F4 v0.2 を完了。
  試金石データ（Raw / Execution Context / Summary）を構造化し、
  他プロジェクトが判断材料として直接利用可能な形で提供可能とした。

### Added
- Web版 ↔ VS Code 往復運用ガイド v1.0r+ を公式運用ドキュメントとして追加。

---

## v0.6.3 (2025-12-17)

### 修正（Fixed）
- SPA 構成に適したログイン成功判定へ切り替え
  DOM や load イベント依存を廃し、URL 遷移（`/chat` を含むか）による readiness 判定を採用。
  - `page.wait_for_function(window.location.href.includes('/chat'))`
- 上記変更により、DOM 揺らぎや非同期ロード順序に起因する
  断続的な E2E 失敗を解消。

### 検証完了（Verified）
- F4（RAG 評価フェーズ v0.1）のテストが、設計どおり完走することを確認。
  - Case1：PASS
  - Case2：PASS
  - Case3：PASS または SKIP
    （回答取得不可時は SKIP とする設計どおりの挙動）
- `tests/f4` が以下すべての実行形態で ERROR / FAIL なく完了することを確認。
  - 単体実行
  - 連続実行
  - バッチ実行（`python -m pytest`）

### 判断・位置づけ（Decision）
- F4 v0.1 は以下の点において **設計目的を達成し、完了状態に到達**したと判断する。
  - HTML / Markdown ナレッジ差分を、誤解なく再現可能に観測できる
  - 手動運用前提の評価ルール・ログ仕様・責務分離が安定
- 自動集計、CI 統合、高度な意味評価は **v0.1 の非目標**とし、
  **F4 v0.2 以降の拡張課題**として切り出す。

### 次フェーズ（Next）
- F4 v0.2 として、以下の検討・設計に着手する。
  - 評価結果ログの機械集計
  - 差分指標の自動比較
  - CI への段階的統合可否の検討

※ 本リリースは E2E 基盤（F1–F3）および
   F4 v0.1 の運用ルールを変更するものではない。

### Clarified
- F4 フェーズの責務を整理し、
  本プロジェクトは「HTML→Markdown 変換の是非を判断する」のではなく、
  他プロジェクトが判断に利用可能な
  **RAG 入力差分の試金石データを提供すること**を目的とすることを明確化。
- F4 v0.2 を、
  F4 フェーズのゴールを満たす
  **最初の完了マイルストーン（試験データ提供段階）**
  として正式に位置づけ。
- F6（LGWAN 対応フェーズ）について、
  サービス事業者からの提供待ちであることを踏まえ、
  **着手不可の保留フェーズ（Blocked）**として明示。

---

## [v0.6.2] - 2025-12-16

### Clarified
- F4 RAG 評価フェーズにおける評価結果ログの説明責任を明確化
- 手動 profile / アカウント切替運用下での
  実行文脈（Execution Context）の位置づけを整理

### Changed
- Design_pytest_f4_results_writer を v0.1.2 として確定
  - `login_identity`（configured / observed）の構造と意味論を正式化
  - login_identity の取得・構築責務を pytest 実行層に明示的に分離
  - writer は記録専用とし、取得・推測・検証を行わないことを明文化
  - observed が取得できない場合を unverified として正当ケース化

### Notes
- 本更新は設計およびログ仕様の明確化のみであり、
  テスト基盤（F1–F3）および F4 の手動運用方針自体は変更していない
- 自動ログイン判定・アカウント切替・CI 統合は引き続き v0.1 系では非対象

### Implementation

- F4 評価結果 writer において、`execution_context` の記録方式を確定
  - pytest 実行層から渡された場合のみ、YAML frontmatter に記録
  - Execution セクションでの再掲を行わない実装に整理
- 上記変更に伴い、後方互換性を確認する pytest を実行し、
  既存 Case1 実行結果に影響がないことを確認


---

## v0.6.1 — F4運用ルール確定（v0.1.5）/ 手動評価フェーズ固定

**Date:** 2025-12-XX

### 🎯 概要

F4（RAG 評価フェーズ）における
**運用ルールを明文化・固定**し、
HTML vs Markdown 差分評価を「誤解なく再現可能」な状態に整理。

評価自体は引き続き v0.1 指標を使用し、
**運用のみを安定化**したリリース。

---

### ✅ Added（追加）

- **F4 RAG 評価フェーズ 運用ルール v0.1.5**
  - アカウント分離によるナレッジ管理を正式採用
  - Case 間でのナレッジ差し替えを行わない方針を明記
  - 質問文の一意化ルール（条例ID必須）を確定
- F4 結果ログの命名規約を固定
  - case_id / profile / timestamp 必須

---

### 🔧 Changed（変更）

- F4 における `profile` の位置づけを明確化
  - 実行ログ識別用メタデータとして利用
  - chat / ナレッジの自動切替用途では使用しない
- PROJECT_STATUS を v0.6.1 に更新
  - F4 運用ルール確定内容を正式反映

---

### 🚫 Out of Scope（意図的にやらないこと）

- ナレッジの自動アップロード／削除
- chat_name の自動切替
- CI への F4 統合
- 高度な意味的評価指標

※ いずれも v0.2 以降の検討事項とする。

---

### 📌 Impact（この変更で可能になったこと）

- HTML / Markdown 差分評価を
  **人手運用でも安全に再現可能**
- テスターが変わっても
  **同一手順で F4 を実行可能**
- 今後の自動化検討に向けた
  **確定した運用前提の獲得**

---

## v0.6.0 — RAG評価フェーズ正式開始 / フェーズ定義統一

**Date:** 2025-12-14

### 🎯 概要

E2E テスト基盤（F1–F3）を完全に凍結し、
**RAG 評価を目的としたテスト運用フェーズ（F4）へ正式移行**。

本バージョン以降、本プロジェクトは
「テスト基盤を作る」段階を終え、
**「テストで価値判断を行う」段階**に入る。

F4 では、HTML / Markdown 形式の差分が
RAG 回答に与える影響を、
**最小構成・差分評価のみ**で検証する。

---

### ✅ Added（追加）

- **RAG 評価基準 v0.1（正式決定）**

  - Evidence Hit Rate（条例由来語の出現）
  - Hallucination Rate（無根拠表現の抑制）
  - Answer Stability（再現性）
- Basic RAG Test 実装（Playwright / pytest）
- pytest-facing Answer Detection API v0.1r

  - page を受け取る低レベル API 境界を正式採用
- **F4 事前検証：部署境界プローブ（完了）**

  - 部署境界が RAG 検索境界として機能することを
    固有トークンによる 1 問テストで検証（OK）
- **Golden 資産の確定・凍結**

  - Golden Question Pool A（18 問）
  - Golden Ordinance Set（対象条例 10 本）
- **F4 用 最小 3 ケース評価設計の確定**

  - HTML / Markdown 差分検出に特化した最小構成
- RAG 評価・設計関連ドキュメント群

  - Design_rag_f4_eval_v0.1
  - Design_rag_f4_dept_boundary_probe_v0.1
  - Golden_Question_Pool_A_v1.1
  - Golden_Ordinance_Set_v1.0
- Markdown lint 設定（文書品質の安定化）

---

### 🔧 Changed（変更）

* **フェーズ定義を Roadmap v1.1 に完全統一**

  * Phase A / B / C 等の暫定呼称を廃止
  * F1–F7 のみを正式フェーズとする
* PROJECT_STATUS を v0.6.0 に更新

  * F1–F3 を「基盤フェーズ」として明示的に凍結
  * F4（RAG 評価フェーズ）を Current Phase として明文化
  * F4 が **Golden 資産を直接消費せず、最小 3 ケースで評価する**
    ことを明記
* RAG テストにおける判定モデルを三値化

  * PASS / FAIL / SKIPPED（Inconclusive）

---

### 🧠 Fixed（確定・凍結された判断）

* chat-id は推測対象ではなく **API 境界で明示的に受け取る事実**
* submit–probe 相関はアルゴリズムではなく **state**
* 「意味的に正しい」と「文字列的に一致」は別問題
* 高レベル API による page 隠蔽は採用しない
* Golden Question Pool / Ordinance Set は
  **上位基準資産として保持し、F4では消費しない**

これらは **設計判断として固定**され、
今後のフェーズで覆されることはない。

---

### 🚫 Out of Scope（意図的にやらないこと）

* 意味的同義語判定
* モデル間性能比較
* 高度な自然言語理解評価
* Golden 資産の改変・消費

※ いずれも v0.2 以降の検討事項とする。

---

### 📌 Impact（この変更で可能になったこと）

* HTML → Markdown 変換の **費用対効果を定量比較**できる
* 容量制約（20GB）下での RAG 最適化判断が可能
* 人手レビューに依存しない RAG QA が成立
* 差分評価・能力評価・将来 CI を
  **同一基盤・同一資産体系で段階的に拡張可能**

---

## [0.5.1] - 2025-12-14

### Added

- Basic RAG Test v0.1 requirements document (basic_rag_v0.1.md)

### Changed

- Clarified CI as foundation verification CI (Design_ci_e2e_v0.1.1)
- Explicitly separated E2E foundation phase and RAG QA phase in project status

### Docs

- Linked test_plan_v0.1.1 to Basic RAG Test requirements

---

## v0.5.0 — E2E 基盤確定 / RAG QA 自動化フェーズ開始

*2025-12-13*

### 🎉 Added / Finalized

- submit–probe 相関設計 v0.2 を基盤として正式確定
- CI 上での相関状態（Established / Not Established / No Evidence / Unassessed）の
  **誤解のない可視化（Presentation Semantics v0.1）を正式採用**
- GitHub Actions summary による
  **日本語 E2E Correlation Summary テンプレートを追加・運用開始**
- 英語版 summary との **設計差分ゼロ対照表**を追加
- Phase 1〜6（E2E 基盤構築フェーズ）を完了としてクローズ

### 🧱 Stabilized

- ChatPage.submit v0.6（UI 送信責務のみに限定）
- SubmitReceipt（submit_id / sent_at / ui_ack）定義の確定
- Answer Detection Layer（probe v0.2.1）
  - REST-only / GraphQL 非発火ケースを前提条件として包含
- PASS / WARN / INFO を
  **成否ではなく表示セマンティクスとして扱う CI 設計を固定**

### 🔁 Changed

- E2E workflow（GitHub Actions）を単発実行に復帰
  - Phase 5 の matrix 実験（capture_seconds 条件軸）は完了・撤去
- CI summary 出力を英語テンプレから日本語テンプレへ切り替え

### ⏸ Deferred

- RAG 系テスト（basic / advanced）
  - E2E 基盤確定を優先するため一時的に切り離し
  - 次フェーズ（RAG QA 自動化）で再接続予定

### 🚀 Next

- Design_playwright_v0.1 に基づく
  **Playwright を用いた RAG QA 自動化フェーズへ移行**
- Basic RAG Test の再導入とテストデータ設計の具体化

---

## v0.4.10 (2025-12-13)

### Added

- **submit–probe 相関設計 v0.2 を正式採用**
  - submit_id を一次相関キーとする設計を完全確定
  - 相関をアルゴリズムではなく「状態（state）」として定義
    - Established / Not Established / No Evidence / Unassessed
  - 相関状態とテスト結果（PASS / WARN / INFO）の写像ルールを明文化
  - GraphQL createData 非発火 / REST-only ケースを前提条件として包含
- **観測事実（Observation_submit_probe_correlation_v0.2）を固定**
  - 実行結果を一次情報として保存し、設計判断の唯一の根拠とした
- **CI / E2E 基盤安定化方針を明文化**
  - submit / probe / 相関を基盤レイヤとして確定
  - ask / RAG 系テストを一時的に Deferred として切り離し
- **CI Correlation Summary template v0.1 を追加**
  - submit–probe 相関結果を GitHub Actions summary 上で
    誤解なく可視化するための Markdown テンプレートを追加
  - 相関状態（Established / Not Established / No Evidence / Unassessed）を
    「状態（state）」として明示し、成功／失敗判定と分離
  - CI 表示ラベル（PASS / WARN / INFO）を
    presentation semantics として扱うことを固定
  - WARN / INFO を失敗と誤認しない設計原則を CI 出力に反映
  - FAIL を導入しない方針を維持

  File:
  - docs/ci/summary_template_submit_probe_v0.1.md

### Changed

- **PROJECT_STATUS を自己完結型ドキュメントに再構成**
  - 変更有無に関わらず、前バージョン内容を省略せず再掲
  - 最新版単体でプロジェクトの到達点・判断履歴が読める構成に変更
- **ChatPage.submit v0.6 を基盤 API として位置づけ**
  - UI送信のみの責務を担う API として確定
  - completion / semantic 判定は Answer Detection Layer に完全委譲

### Deferred

- **RAG 系テスト（basic / advanced）**
  - ask API は submit–probe 基盤の上位レイヤと位置づけ
  - 基盤安定化完了後に再接続予定（削除ではなく Deferred）

### Notes

- 本バージョンは **機能追加ではなく「設計・責務境界の確定」**が主目的
- 相関不能ケースを FAIL と誤認しない設計原則を正式固定

### CI

- FIX: Simplified e2e workflow to single smoke execution
- RAG tests are explicitly deferred to align with submit–probe correlation design
- Resolved pytest exit code 5 by removing redundant test invocations

---

## v0.4.9 (2025-12-13)

### Added

- Added Design_submit_probe_correlation_v0.2 as the authoritative correlation design
  - Integrated v0.1 and extended with explicit correlation states
  - Defined mapping from correlation states to test results (PASS / WARN / INFO)
  - Explicitly excluded FAIL semantics for unobservable or non-correlated cases
  - Clarified responsibility boundaries between submit and probe layers

### Changed

- submit–probe correlation design reference updated to v0.2 (supersedes v0.1)

---

## v0.4.8 (2025-12-13)

### Added

- Finalized submit–probe correlation design:
  - Introduced `submit_id` as the primary correlation key
  - Clearly separated submission responsibility from answer detection
  - Formally accepted REST-only and GraphQL-non-firing cases
  - Added observed facts appendix based on real execution logs

- Added design-support document:
  submit–probe correlation test perspective checklist (v0.1)
  - Formalized MUST / MUST NOT boundaries between
    ChatPage.submit v0.6 and Answer Detection Layer (probe v0.2)
  - Explicitly covered REST-only, GraphQL-non-firing,
    and correlation-inconclusive cases
  - Clarified that correlation failure must not be treated
    as submit or probe failure
  - Positioned strictly as a pre-implementation
    design review aid (no code / CI impact)

  File:
  - docs/design_support/Test_Perspective_submit_probe_correlation_v0.1.md

- Added formal design document for SubmitReceipt (v0.1)
  - Defined immutable return type for ChatPage.submit v0.6
  - Fixed submission responsibility boundary at the data-structure level
  - Explicitly excluded completion semantics, probe concepts,
    and REST/GraphQL results
  - Positioned as intentionally minimal and non-extensible
    design artifact to prevent responsibility leakage

  File:
  - docs/design_support/Design_SubmitReceipt_v0.1.md

- Added ChatPage.submit v0.6 (UI submission only)
  - Returns immutable SubmitReceipt (submit_id, sent_at, ui_ack, diagnostics)
  - Uses HTML form submit (requestSubmit with Enter fallback) to avoid button locator dependency
  - Explicitly excludes completion semantics, answer parsing, and REST/GraphQL access

### Changed

- PROJECT_STATUS updated to reflect completion of correlation design
- Next Action advanced to implementation readiness (test perspective definition)

### Notes

- No implementation or CI behavior changes in this version


---

## v0.4.7 (2025-12-13)

### Added

- Finalized `Design_ChatPage_submit_v0.6`:
  - Introduced submission-only API with explicit responsibility separation
  - Clarified boundary between UI submission and answer detection
  - Preserved legacy DOM-based `ask()` semantics in v0.5

### Changed

- PROJECT_STATUS updated to mark submission API design as completed
- Next Action advanced to submit_id ↔ probe correlation design

---

## v0.4.6 (2025-12-13)

### Changed

- Updated test plan doctrine document:
  - `test_plan_v0.1.md` → `test_plan_v0.1.1.md`
  - Clarified that test_plan is a **top-level doctrine document** defining
    test hierarchy, priorities, and responsibilities
  - Explicitly separated test system philosophy from executable test specifications
  - No changes to test structure, execution logic, or CI behavior

---

## v0.4.5 (2025-12-12)

### Added

- 正式 QA 仕様書を追加：`docs/test_plan/Test_plan_probe_v0.2.1.md`
  - Answer Detection Layer（probe v0.2.1）に対する完全なテスト計画を定義

### Changed

- PROJECT_STATUS を v0.4.5 に更新
  - probe v0.2.1 の実装が「設計書準拠の FIX 状態」であることを記録
  - Test Plan の追加と、Answer Detection Layer が QA 実行フェーズに入ったことを明記

- probe 用テスト計画を v0.2.1 → v0.2.2 に更新
- Test_plan_probe_v0.2.2.md を docs/test_plan/ 配下へ移動（構造整理のため）
- test_plan_v0.1.md を「E2E テスト体系における最上位仕様・思想文書」として位置づけを明確化

### Notes

- probe v0.2.1 は **まだ最終 QA 完了状態ではない**
  - 最終検証結果および評価は、後続リリースで追記予定

---

## v0.4.4 (2025-12-12)

### Added

- Answer Detection Layer に関する正式仕様を追加：
  - `Design_chat_answer_detection_v0.1.md`
  - `Design_probe_graphql_answer_detection_v0.1.md`
- `test_env_loader_matrix_v0.2` を追加し、Environment Layer（env_loader v0.2.3）の QA プロセスを体系化。

### Changed

- PROJECT_STATUS を v0.4.4 に更新し、
  **唯一の Next Action を env_loader（Design_env_v0.2.3 準拠のスキーマ整合レビュー）から
  probe v0.2（GraphQL createData 監視＋assistant 抽出）へ正式に切り替え。**
- Roadmap を再編し、以下の後続タスクを正式登録：
  - XHR/GraphQL フュージョン方式検証
  - ChatPage.ask v0.6 の刷新
  - CI 上での回答検知安定化

### Fixed

- env_loader v0.2.3 の以下が QA により設計仕様と完全一致することを確認：
  - MissingSecretError の拘束仕様
  - Schema Freeze Rule（構造不変性）
  - OS > .env の優先順位
  - ENV_PROFILE の正しい適用
  - recursive / list placeholder などの特殊ケース解決

### Notes
- Environment Layer（env_loader）は v0.2 系と完全互換であり、
  本バージョンでは **実装のレビューと設計書 v0.2.3 との整合確認のみを目的とした非破壊更新** である。

---

## **v0.4.3 (2025-12-10)**

### **Environment Layer Clarifying Update（Design_env_v0.2.3）**

#### Added

* Schema Integrity Rule（スキーマ不変ルール）を追加
* AI Prohibitions を拡張（key rename / schema drift 禁止を明文化）
* Annotated Diff セクションを設計書に追加し、文書追跡性を向上
* Minimal Binding Example を binding として固定化

#### Changed

* Non-functional Requirements に schema freeze を正式に組み込み
* env_loader と CI/LGWAN の責務境界をより明確化
* 日本語補助文と英語拘束文の対訳構造を正式に標準化（今後の設計書もこの形式へ統一可能）

#### Notes

* 本更新は **non-breaking（非破壊）** であり、runtime 挙動は v0.2 / v0.2.2 と完全互換
* 今後は env_loader の整合レビューに進む

---

## **v4.2 (2025-12-10)**

### **Governance Layer Update（重大更新）**

#### Added

* PROJECT_GRAND_RULES v4.2 を正式採用
* AI Compliance Rules v1.0（C2仕様）を導入
* Language Binding Rule（英語拘束／日本語補助）を新設
* Documentation Standards / QA / Prohibition Sections を整理・拡張

#### Changed

* 旧 v4.0 の AI行動規範を全面刷新し、拘束力を強化
* Rule Hierarchy の順序と拘束力を明確化
* PENTA 出動条件の厳格化

#### Notes

* 今後の設計書・CI・環境設定は **すべて v4.2 の拘束ルール下で生成される必要がある**。
* env_loader・CI の見直し（v0.3 準備）は次アクション。

---

## v0.4.0 (2025-12-10)

### Added
- PROJECT_GRAND_RULES v4.0 を全面更新
  - Debugging_Principles_v0.2 を統治層へ統合
  - PageObject 4層構造（Base / Login / ChatSelect / Chat）を正式採用
  - CI / env_loader / Secrets 運用規範を追加
  - デバッグ行動原則（観察優先・推測禁止・再発防止）を明文化

- ChatSelectPage v0.3 を正式に import 対応
  - test_smoke_llm での依存が解消し、構造が整合

### Changed
- PROJECT_STATUS を v0.4.0 へ更新
  - Next Action を「CI headless 安定化」に一本化
  - 最新成果・課題・リスクを再整理

### Notes
- 今後、PageObject 全体のバージョン統一（v0.6 系）へ移行予定
- CI での Smoke 成功率向上が最優先タスク

---

## v0.3.0 (2025-12-10)

### Added
- **ChatPage v0.5 を正式実装（DOM 完全対応版）**
  - 最新 DOM 解析に基づき、入力欄・送信ボタン・メッセージ要素のロケータを刷新。
  - 入力欄を `#message`、送信ボタンを `#chat-send-button` として安定化。
  - メッセージ取得ロケータを `message-item-N` / `markdown-N` 構造に準拠。
  - メッセージ数増加による応答検知方式（count-based wait）を採用し、UI揺らぎに強い方式を確立。

- **Design_ChatPage_v0.5.md を追加**
  - DOM 解析結果・ロケータ仕様・待機戦略・保守ポイントを正式文書化。
  - gov-llm-e2e-testkit におけるチャット画面自動化の標準仕様を定義。

### Changed
- **Smoke Test v0.3 の仕様をアップデート**
  - ChatPage v0.5 に合わせて応答取得方式を刷新。
  - 旧 data-testid ベースのロケータに依存しない構造へ変更。
  - Smoke Test が初めてフル成功する安定性を獲得。

- ChatSelectPage の役割を「遷移補助」から「任意利用モジュール」へ整理
  - ログイン後に自動で任意チャットへ遷移する UI 仕様を踏まえ、
    Smoke Test には必須でないことを明確化。

### Fixed
- **chat-input が DOM に存在しない問題を修正**
  - 旧ロケータ `data-testid="chat-input"` を完全廃止し、
    最新 DOM に基づく `#message` を採用。

- **送信ボタンのロケータ破損を修正**
  - `data-testid="chat-send-button"` 廃止に対応し、`#chat-send-button` へ移行。

### Notes
- ChatPage v0.5 は Qommons.AI（2025年12月時点）の DOM に完全準拠した安定版。
- UI 変更に強いロケータ構造（id・prefix-based search）を採用しており、
  CI / ローカル双方で動作が安定。
- 次ステップとしては ChatSelectPage v0.3.1 以降の整理、および
  マルチケース（RAG 強化テスト）の拡張が可能。

---

## v0.2.1 (2025-12-09)

### Added

- Design_env_v0.2.md を追加
  - env.yaml / .env / 環境変数の統合設計を正式化。
  - INTERNET / LGWAN / dev / ci プロファイルを .env で切り替える方式を定義。
  - MissingSecretError を用いた Secrets 不足時の標準エラー仕様を策定。

### Changed

- 環境設定レイヤの推奨運用を「OS環境変数方式」から
  「.env（dotenv）方式 + 環境変数」のハイブリッド方式へ変更。
- PROJECT_STATUS を v0.1.18 に更新し、Next Action を
  「env_loader v0.2 実装」へ切り替え。

### Notes

- 既存の環境変数ベースの運用はそのまま有効。
- 今後の OSS ユーザー向け Quick Start は `.env` ファイルを前提とする。
- env_loader v0.2 の実装完了後、CI / LGWAN 手順書と合わせて再度検証予定。

---

## v0.2.0 (2025-12-09)

### Added

- `docs/Debugging_Principles_v0.1.md` を追加
  - E2E / Python / SPA / CI に共通するデバッグ原則を体系化。

### Changed

- E2Eテスト基盤を Playwright Async → Sync へ移行し、安定動作を実現。
  - LoginPage（Sync版）を正式採用
  - conftest.py を Sync Playwright に書き換え
  - no_wait_after=True を標準化
  - headless=False を推奨デバッグモードに設定

### Fixed

- Async Playwright が pytest-asyncio(strict) と競合して停止する問題を解消。
- SPA ログインが navigation せずタイムアウトする問題を Sync版で安定回避。
- Smoke Test が安定して PASS することを確認。

### Notes

- 次版では ChatPage Sync 実装と RAG Basic Sync テストを予定。
- Debugging_Principles は v0.2 → v0.3 系でさらに強化（逆引き辞典・フローチャート）。

---

## v0.1.17 (2025-12-08)
### pytest Execution Layer v0.2
- ADD: conftest.py に `case_dirs` fixture を追加し、テストケース単位で evidence_dir を生成
- ADD: Smoke / Basic / Advanced の全テストを v0.2 構造に全面改修
- ADD: PageObject v0.2 の evidence_dir 機能と統合
- IMPROVE: test_smoke_llm を v0.2 仕様へ再設計（LoginPage / ChatPage v0.2 準拠）
- IMPROVE: basic_cases / advanced_cases のテスト構造を統一
- IMPROVE: advanced の multi-turn 処理を PageObject API に準拠する形に統一
- ADD: pytest 設計書の最新版 `Design_pytest_v0.2.md` を追加
- IMPROVE: latest エントリーポイント `Design_pytest.md` を統一フォーマットへ刷新

### Documentation
- IMPROVE: Design_BasePage.md / Design_ChatPage.md / Design_pytest.md を統一スタイルへ整理

---

## v0.1.16 (2025-12-09)

### Added
- Design_BasePage.md（最新版を参照する固定ファイル）を追加
- 設計書バージョニング方式（全バージョン保持＋latest ラッパー方式）を正式採用

### Changed
- Design_BasePage_v0.2.md を最新仕様として確定し、v0.1 を supersede
- PROJECT_STATUS.md に設計書管理ポリシーを反映

### Notes
- 今後の設計書（LoginPage / ChatPage / Playwright / CI / Logging など）も同じ方式に統一予定。

---

## v0.1.15 (2025-12-09)

### Added

* `test_smoke_llm.py`、`test_rag_basic_v0.1.py`、`test_rag_advanced_v0.1.py` に
  **log_writer v0.1 を正式統合**
* multi-turn advanced ログ仕様に基づく詳細ログ（details）生成を追加

### Changed

* `tests/conftest.py` を v0.1.15 仕様に書き換え（env_config tuple 化・timeout 正常化）
* Basic / Advanced 判定ロジックを設計書の通り統一

### Notes

* これにより E2E testkit の全レイヤが一貫し、
  CI artifacts も公式仕様どおりに整う v0.1 系の最終安定版となった。

---

## **[v0.1.14] - 2025-12-08**

### Added

- `log_writer.py v0.1` を実装

  - Design_log_writer_v0.1 の仕様に基づき

    - frontmatter 生成
    - Markdown セクション生成
    - Smoke / Basic / Advanced 切替
    - assets ディレクトリ生成
      をすべて実装。

### Changed

- PROJECT_STATUS を v0.1.14 に更新。
  - Next Action を「pytest への log_writer 統合」に変更。

### Notes

- これにより **ログ生成の最終要素が揃い、自動テスト基盤の全レイヤが接続可能となった**。

---

## [v0.1.13] - 2025-12-07

### Added

- Design_logging_v0.1.md を新規追加（標準ログフォーマットを定義）
  - frontmatter・基本構造・Basic/Advanced 差分・スクショ保存規約を含む

### Changed

- PROJECT_STATUS を v0.1.13 に更新
  - logging v0.1 の追加を反映
  - Next Action を「logger_v0.1 設計」に変更

---

## [v0.1.12] - 2025-12-07

### Added
- Responsibility_Map_v0.1.md を新規追加（全レイヤの責務境界を正式定義）
- Design_pytest_env_v0.1.md を追加（pytest Execution Layer の正式設計）
- conftest.py v0.1 の設計仕様を正式確立（browser/context/page生成・timeout適用・env_loader連携）

### Changed
- PROJECT_STATUS を v0.1.12 に更新
  - Responsibility Map / pytest Execution Layer 追加を反映
  - Next Action を「ロギング仕様 v0.1」に変更

---

## [v0.1.11] - 2025-12-07

### Added
- env_loader.py v0.1 を追加（env.yaml の正式ローダー）
- BasePage / pytest への env 連携を統一

### Changed
- PROJECT_STATUS を v0.1.11 に更新
  - env.yaml ローダー実装完了を反映
  - Next Action を「ロギング仕様 v0.1」策定に変更

---

## [v0.1.10] - 2025-12-07

### Added

- Design_env_v0.1.md（INTERNET/LGWAN 切替仕様の正式版）を追加

### Changed

- PROJECT_STATUS を v0.1.10 に更新
  - env.yaml 設計の完了を反映
  - Next Action を「env.yaml（実ファイル）生成」に変更

### Notes

- 本バージョンにより、INTERNET・LGWAN の環境統合レイヤが完成。
  gov-llm-e2e-testkit は次に env.yaml 実体生成フェーズへ移行する。


---

## [v0.1.9] - 2025-12-07

### Added

- **Design_ci_e2e_v0.1.md** を追加（INTERNET向け CI 設計の正式版）
- .github/workflows/e2e.yml の仕様を確定

### Changed

- PROJECT_STATUS を v0.1.9 に更新
  - Next Action を「CI（e2e.yml）v0.1 の実装」に変更

### Notes

- 本版により、gov-llm-e2e-testkit の E2E 自動化パイプラインの設計が完成。
  次は CI 実ファイル e2e.yml の GitHub 反映へ進む。

---

## [v0.1.8] - 2025-12-07

### Added

- **RAG Basic / Advanced pytest implementation v0.1** を追加
  - YAML → pytest のマッピング仕様（Design_RAG_Test_v0.1）に準拠
  - tests/rag/test_rag_basic_v0.1.py
  - tests/rag/test_rag_advanced_v0.1.py

### Changed

- PROJECT_STATUS.md を v0.1.8 に更新
  - Next Action を CI（e2e.yml）v0.1 設計へ変更
  - rag_basic / rag_advanced の物理フォルダを廃止し、data/rag/ 統合構造へ整合

### Notes

- v0.1.8 により RAG テストの **データ → 実装 → pytest 結合** が完了。
  CI レイヤに進むための準備が整った。

---

## [v0.1.7] - 2025-12-07

### Added

- **test_plan_v0.1** を新規追加
  - Smoke / Basic RAG / Advanced RAG の3層テスト体系を正式策定
  - basic/advanced YAML のスキーマを定義
  - INTERNET/LGWAN 実行ポリシーを明文化
  - CI（e2e.yml）の基本方針を規定
  - UI変動／モデル更新時の再テスト手順を定義
  → テスト基盤の“最上位仕様”が確立された

### Changed

- PROJECT_STATUS.md を v0.1.7 に更新
  - test_plan 完成を反映
  - Next Action を「RAG YAML スキーマ実体化」に変更
  - Backlog を整理

### Notes

- v0.1.7 は **E2Eテスト体系の全体像が初めて統合された重要マイルストーン** であり、
  RAG 設計・CI 設計へ進むための基盤が整った。

---

## [v0.1.6] - 2025-12-07

### Added

- **Design_LoginPage_v0.1** を新規追加
  - username / password / login ボタンのロケータ設計
  - login() / wait_for_login_success() など高レベルAPIを定義
  - BasePage / Locator_Guide_v0.2 に基づく UI変動耐性を確保
  - LGWAN timeout 対応を明示

### Changed

- PROJECT_STATUS.md を **v0.1.6** に更新
  - ChatPage / LoginPage 設計フェーズ完了を反映
  - Next Action を “BasePage 実装” に更新
  - Backlog と必須資料リストを整理

### Notes

- v0.1.6 により主要 Page Object（BasePage + ChatPage + LoginPage）の
  **設計段階がすべて完了し、実装フェーズへ移行可能**となった。

---

## [v0.1.5] - 2025-12-07

### Added

- **Design_BasePage_v0.1** を新規追加
  - Page Object 基底クラスの責務・構造を定義
  - locator factory / safe actions / LGWAN timeout / loading wait など
    共通インターフェースの仕様を確立
  - Locator_Guide_v0.2 と Design_playwright_v0.1 に正式準拠

### Changed

- PROJECT_STATUS.md を v0.1.5 に更新
  - BasePage 設計書の完成を反映
  - Next Action を「ChatPage 設計書 v0.1 作成」に更新
  - 参照文書体系を最新化

### Notes

- 本バージョン v0.1.5 により、Page Object 層の“基底構造”が確立され、
  ChatPage / LoginPage / Smoke Test へ進むための基盤が完成した。

---

## [v0.1.4] - 2025-12-07

### Added

- **ChatGPT Startup Workflow v3.0** を新規追加
  - PROJECT_GRAND_RULES v2.0 / Startup Template v3.0 と整合
  - /start 時のブートシーケンスを拡張（参照文書同期・Next Action 単一検証・LGWAN判定など）
  - 作業フェーズ（設計→実装→テスト→文書更新）を体系化
  - UI変動・モデル更新の検知フローを追加
  - LGWAN 実行モード（オフライン動作）の特別ルールを定義

### Changed

- PROJECT_STATUS.md を **v0.1.4** に更新
  - Startup Workflow v3.0 の導入を反映
  - 現在地／Backlog／Next Action を最新化
  - 必須資料に Workflow v3.0 を追加
- プロジェクト内部レイヤを再整理
  - 「設計（Design）／運転（Startup Template）／行動制御（Workflow）／実行（STATUS）」の4階層構造を明確化

### Notes

- 本バージョン v0.1.4 は、
  Startup Template（運転層）に加えて **Startup Workflow（行動制御層）が完成した最初の版** であり、
  プロジェクトが「設計駆動で破綻しない統制構造」を正式に獲得した重要バージョンである。

---

## [v0.1.3] - 2025-12-07

### Added

- **Startup Template v3.0（運転層統合版）** を新規作成
  - PROJECT_GRAND_RULES v3.0 と整合した行動規範を統合
  - Design_playwright_v0.1 / Locator_Guide_v0.2 への準拠を明文化
  - /start 時のブートシーケンスを再定義
- PROJECT_STATUS.md を v0.1.3 に更新
  - Startup Template v3.0 の運用開始を反映
  - 参照文書・Backlog・Next Action を最新化

### Changed

- 参照文書体系を最新版に整合
  - Startup Template → v3.0 に更新
  - STATUS / GRAND_RULES / Locator_Guide との依存関係を整理
- STATUS の「プロジェクト目的」「現在地」「未完了タスク」を刷新
- Next Action を **BasePage（Page Object 基底クラス）の作成**として再設定

### Notes

- 本バージョン v0.1.3 は、プロジェクトの「運転層（Startup Template）」が
  統治層（GRAND_RULES）と完全整合した、
  **初のフル統合バージョン**である。

---

## [v0.1.2] - 2025-12-07

### Added

- **Locator_Guide_v0.2.md（UI識別規範）** を新規作成
  - ロケータ優先順位を明確化（Role → Label → aria-label → data-testid → CSS）
  - LGWAN 遅延を考慮した timeout 推奨値を追加
  - 文言変動に強くする fallback パターンを追加
- PROJECT_STATUS.md を v0.1.2 に更新
  - UI識別規範作成完了を反映
  - Next Action を BasePage 作成へ変更
- Startup Template v1.1 の「参照文書」に Locator_Guide_v0.2 を追加

### Changed

- STATUS の「未完了タスク」「完了タスク」を最新版に更新
- プロジェクト参照文書体系を整備

---

## [v0.1.1] - 2025-12-07

### Changed

- プロジェクト名を **qommons-ai-auto-test → gov-llm-e2e-testkit** に正式変更
- Startup Template / PROJECT_STATUS / 各設計書の名称を一括更新
- ディレクトリ標準構成のプロジェクト名を差し替え

---

## [v0.1.0] - 2025-12-07

### Added

- プロジェクト初期セットアップ
  - Startup Template v1.1（行動規範、設計規範、運用ルール）
  - PROJECT_STATUS v0.1.0（最初の進行管理表）
  - Design_playwright_v0.1.md（Playwrightの基盤設計書）
- 基本ディレクトリ構成の定義
  - design/ tests/ data/ logs/ .github/workflows/

---

## 📎 運用ルール（再掲）

- すべての更新は PENTA による検討・整理後に実施する
- 設計書・ルール・STATUS の変更は必ず CHANGELOG に追記する
- バージョン番号は **プロジェクト全体の進行管理番号** であり、コードとは独立
- PROJECT_STATUS 更新と CHANGELOG 更新は必ずセット
- フェーズ遷移は CHANGELOG に必ず記録
- 重要な設計判断は「Fixed」として残す

---

### 次のアクション

1. この CHANGELOG v0.6.0 をコミット
2. PROJECT_STATUS v0.6.0 と同一コミットで push
3. F4（RAG 評価フェーズ）の実験ログ作成へ進行

---
