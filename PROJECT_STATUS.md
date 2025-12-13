# 📘 PROJECT_STATUS v0.4.10 — submit–probe Correlation v0.2 + RAG Tests Deferred

**Last Updated:** 2025-12-13  
**Maintainer:** Sumio Nishioka & ChatGPT (Architect Role)

---

## 1. Current Focus（現在の主眼）

### ⭐ Answer Detection Layer（probe v0.2 系）の QA を完了し、

**ChatPage.submit v0.6 と submit–probe 相関設計（v0.2）を基盤として、  
E2E テスト基盤の安定化フェーズへ移行する。**

- Environment Layer は完了済み・凍結
- Answer Detection Layer は設計・実装・QA が一巡
- submit / probe / 相関の責務境界は設計として確定
- ask / RAG 系テストは一時的に切り離し、基盤安定化を優先する

---

## 2. Completed（完了）

### ✅ Environment Layer（env_loader v0.2.3）— 完全 QA 完了

- Design_env_v0.2.3 と実装の完全一致を確認
- test_env_loader_matrix_v0.2 による一次情報 QA を保存
- Schema Freeze / MissingSecretError / precedence 等を実証
- **完成モジュールとしてクローズ**

---

### ✅ Answer Detection Layer — QA 完了（probe v0.2）

- Design_chat_answer_detection_v0.1 成立
- Design_probe_graphql_answer_detection_v0.2 成立
- probe v0.2.1 実装完了
- Test_plan_probe_v0.2.2 に基づく実行テストを完了
- **REST-only / GraphQL 非発火ケースを含めて成立確認**

補足：

- test_plan_v0.1.1 を  
  **「E2E テスト体系の最上位仕様・思想文書」**として正式確定

---

### ✅ ChatPage.submit v0.6 — Submission API 設計・実装完了

- ChatPage.submit v0.6 を **UI送信のみの責務**として設計・実装
- submit 呼び出し単位ごとに `submit_id` を生成
- SubmitReceipt（immutable）を返却
- UI 受理確認は `ui_ack`（入力欄クリア）で最小化
- 送信操作は **HTML form submit（requestSubmit → Enter fallback）** を採用
  - 送信ボタン locator 依存を排除し安定化
- completion 判定・回答取得・REST/GraphQL 参照は **MUST NOT**
- sync Smoke にて submit() 1回呼び出し・SubmitReceipt 返却を確認

検証スクリプト：

- `scripts/smoke_submit_v0_6.py`

---

### ✅ SubmitReceipt 定義確定（ChatPage.submit v0.6）

- ChatPage.submit が返却する **唯一のデータ構造**
- 構成要素：
  - submit_id
  - sent_at
  - ui_ack
  - diagnostics
- 回答完了・probe・REST/GraphQL 概念を明示的に排除
- submit と Answer Detection Layer 間の責務リークを型レベルで防止
- **意図的に最小・拡張非前提**の設計装置として確定

設計書：

- `docs/design_support/Design_SubmitReceipt_v0.1.md`

---

### ✅ submit_id ↔ Answer Detection（probe）相関設計 完了（v0.2 正式採用）

- ChatPage.submit が発行する `submit_id` を **一次相関キー**として採用
- UI 送信責務（submit）と回答観測・完了判定責務（probe）を明確分離
- GraphQL createData 非発火 / REST-only ケースを **前提条件として包含**
- 観測事実（logs/ に基づく一次情報）を **Appendix（Observed Facts）として固定**
- 相関を **アルゴリズムではなく「状態（state）」として定義**
- 相関状態：
  - Established
  - Not Established
  - No Evidence
  - Unassessed
- 相関状態とテスト結果（PASS / WARN / INFO）の写像ルールを正式化
- 相関不能ケースを **FAIL と誤認しない設計原則**を明文化
- v0.2 は **v0.1 を完全に包含する上位互換・完全統合版**

設計書：

- `docs/Design_submit_probe_correlation_v0.2.md`

---

### ✅ submit–probe 相関 テスト観点チェックリスト v0.1

- submit / probe の責務境界を検証するための設計補助文書
- MUST / MUST NOT をテスト観点として明文化
- REST-only / GraphQL 非発火 / 相関不能ケースを
  **失敗と誤認しない原則**を固定
- 実装・CI・pytest 仕様は含めない

配置先：

- `docs/design_support/Test_Perspective_submit_probe_correlation_v0.1.md`

---

### ✅ 観測事実（Observation）固定

- submit → probe 実行結果を **観測事実として 1 ファイルに固定**
- correlation_state = Established / no_graphql の実例を保存
- 設計・判断の唯一の根拠として使用

配置先：

- `docs/observations/Observation_submit_probe_correlation_v0.2.md`

---

## 3. Deferred / Out of Scope（一時的に切り離した事項）

### ⏸ RAG 系テスト（basic / advanced）

- `test_rag_basic_v0_1.py`
- `test_rag_advanced_v0_1.py`

理由：

- ask API は submit / probe / 相関設計の上位レイヤであり、
  現フェーズの責務対象ではない
- 現時点では **UI送信成立と相関状態の観測**を最優先とする
- セマンティック正しさ・内容評価は次フェーズで再導入する

位置づけ：

- **削除ではなく Deferred**
- submit–probe–CI 基盤安定後に再接続予定

---

## 4. Next Action（唯一の次アクション）

### 🎯 A. CI 上での submit–probe 相関状態の安定可視化

目的：

1. probe 出力（summary / result）に相関状態を明示
2. PASS / WARN / INFO の CI 表示整理
3. 判定ロジックの肥大化・意味論侵入を防止

制約：

- 相関アルゴリズムの高度化は行わない
- FAIL 導入は次フェーズ以降

---

## 5. Roadmap（後続フェーズ）

### 🔰 B. CI 上での回答検知安定化

- GitHub Actions 上の揺らぎ吸収
- timeout / 遅延差分の整理
- completion semantics の CI 観点での形式化

### 🔰 C. Answer Detection v0.3（将来）

- signature-based 構造検証
- AppSync 変更耐性の強化
- 長期保守を見据えた検知方式の抽象化

### README の全面整理

- README の整理は基盤設計完全収束後に実施
- 現時点では PROJECT_STATUS / CHANGELOG を正とする

---

## 6. Risks / Issues（リスク・課題）

- GraphQL スキーマ変更への依存
- assistant.value prefix 揺らぎ
- REST / GraphQL の非同期性
- AppSync アップデートによる非互換リスク

※ すべて probe v0.2 系で一次情報として把握済み

---

## 7. Required References（参照資料）

- Design_env_v0.2.3
- PROJECT_GRAND_RULES v4.2
- Debugging_Principles v0.2
- Responsibility_Map_v0.1
- Startup Template v3.1
- Design_chat_answer_detection_v0.1
- Design_probe_graphql_answer_detection_v0.2
- Design_submit_probe_correlation_v0.2
- test_plan_v0.1.1
- CHANGELOG

---

## 8. Version

### v0.4.10 — submit–probe 基盤確定 / RAG Tests Deferred

submit / probe / 相関（v0.2）を
**基盤として完全確定**。

RAG / ask 系テストを一時切り離し、
E2E 基盤安定化を最優先とする運用方針を明文化した版。
