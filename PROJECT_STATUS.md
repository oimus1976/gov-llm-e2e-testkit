# 📘 PROJECT_STATUS v0.4.8 — submit–probe Correlation Design Completed

**Last Updated:** 2025-12-13  
**Maintainer:** Sumio Nishioka & ChatGPT (Architect Role)

---

## 1. Current Focus（現在の主眼）

### ⭐ Answer Detection Layer（probe v0.2 系）の QA を完了し、  
**ChatPage.ask v0.6 設計フェーズへ正式に移行する。**

- Environment Layer は完了済み・凍結
- Answer Detection Layer は設計・実装・QA が一巡
- 本プロジェクトの主軸を **PageObject API（ask）の刷新**へ移す

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

### ✅ ChatPage.submit v0.6 — Submission API 設計完了（New）

- UI 送信責務のみを担う Submission API として設計を確定
- 回答完了・意味論・差異吸収は Answer Detection Layer に完全委譲
- Design_ChatPage_v0.5（DOM-based ask）との責務分離を明文化
- 実装・CI 変更は未着手（設計フェーズ完了）

---

### ✅ submit_id ↔ Answer Detection（probe）相関設計 完了（New）

- ChatPage.submit が発行する `submit_id` を一次相関キーとする設計を確定
- UI 送信責務（submit）と回答観測・完了判定責務（probe）の境界を正式定義
- GraphQL createData 非発火 / REST-only ケースを前提条件として包含
- 観測事実（logs/ に基づく一次情報）を Appendix A（Observed Facts）として固定
- 実装・CI 変更は未着手（設計フェーズ完了を宣言）

---

### ✅ submit–probe 相関 テスト観点チェックリスト v0.1 確定（New）

- ChatPage.submit v0.6 と Answer Detection Layer（probe v0.2）の
  責務境界を検証する **設計補助・実装前レビュー用チェックリスト**を正式確定
- submit_id を一次相関キーとする設計について、
  MUST / MUST NOT をテスト観点として明文化
- REST-only / GraphQL 非発火 / 相関不能ケースを
  「失敗」と誤認しない判定原則を固定
- 実装・CI・pytest 仕様は一切含めず、
  **設計レビュー専用文書**として位置づけを明確化

配置先：
- docs/design_support/Test_Perspective_submit_probe_correlation_v0.1.md

---

## 3. Next Action（唯一の次アクション）

### 🎯 A. submit_id ↔ probe 相関の実装準備（テスト観点定義）

目的：

1. Design_submit_probe_correlation_v0.1 に基づく実装前チェック観点の明文化
2. submit / probe 双方の MUST / MUST NOT をテスト可能な形に落とす
3. REST-only / GraphQL 非発火ケースを含む期待挙動の固定

位置づけ：

- 本フェーズは **設計補助・テスト観点整理に限定**
- 実装・CI 変更は次フェーズ以降

---

## 4. Roadmap（後続フェーズ）

### 🔰 B. CI 上での回答検知安定化

- GitHub Actions 上の揺らぎ吸収
- timeout / 遅延差分の整理
- completion semantics の CI 観点での形式化

### 🔰 C. Answer Detection v0.3（将来）

- signature-based 構造検証
- AppSync 変更耐性の強化
- 長期保守を見据えた検知方式の抽象化

### READMEの全面整理

- README の全面整理は ChatPage.submit v0.6 設計完了後に実施する
  （現時点では PROJECT_STATUS / CHANGELOG を正とする）


---

## 5. Risks / Issues（リスク・課題）

- GraphQL スキーマ変更への依存
- assistant.value prefix 揺らぎ
- REST / GraphQL の非同期性
- AppSync アップデートによる非互換リスク

※ いずれも probe v0.2 系で一次情報として把握済み

---

## 6. Required References（参照資料）

- Design_env_v0.2.3
- PROJECT_GRAND_RULES v4.2
- Debugging_Principles v0.2
- Responsibility_Map_v0.1
- Design_ci_e2e_v0.1
- Startup Template v3.1
- Design_chat_answer_detection_v0.1
- Design_probe_graphql_answer_detection_v0.2
- test_plan_v0.1.1
- CHANGELOG

---

## 7. Version

### v0.4.8 — submit–probe Correlation Design Completed

submit_id を一次相関キーとする
ChatPage.submit ↔ Answer Detection（probe）の相関設計を確定。

観測事実を Appendix として固定し、
相関不能ケースを「失敗」と誤認しない設計を正式化した版。

### v0.4.7 — ChatPage.submit v0.6 Design Completed

ChatPage.submit v0.6 の設計完了を宣言し、  
UI 送信責務と回答検知責務の分離を正式確定した版。

Next Action を  
submit_id ↔ Answer Detection（probe）相関設計へ進めた。

### v0.4.6 — Answer Detection QA Completed

Answer Detection Layer（probe v0.2 系）の QA 完了を宣言し、  
ChatPage.submit v0.6 設計フェーズへ移行した版。
