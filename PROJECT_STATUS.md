# 📘 **PROJECT_STATUS v0.4.4 — Answer Detection Specs Integrated + Priority Queue Reform**

**Last Updated:** 2025-12-12
**Maintainer:** Sumio Nishioka & ChatGPT (Architect Role)

---

## **1. Current Focus（現在の主眼）**

### ⭐ **Environment Layer（Design_env_v0.2.3）整合レビューを最優先タスクとして維持しつつ、

回答検知方式（Answer Detection Layer）の正式設計を統合し、次フェーズの実装へ備える。**

本フェーズでは次を確認済み：

* スキーマ不変性（Schema Freeze Rule）
* AI Prohibition（key rename 禁止／暗黙 fallback 禁止）
* /messages と GraphQL createData の「回答最終化」の構造把握
* 回答検知方式の v0.1 設計が完成し、次段階に遷移可能であること

---

## **2. Completed（完了）**

### ✅ **Design_env_v0.2.3（Clarifying Update）の正式採用**

※ v0.4.3 から変更なし

### 🔰 **【追加】回答検知方式（Answer Detection）設計書の正式採用**

以下 2 点を新規に docs/ へ登録：

* **Design_chat_answer_detection_v0.1.md**
* **Design_probe_graphql_answer_detection_v0.1.md**

これにより：

* assistant メッセージの収束点
* GraphQL createData の value からの「最終回答抽出」
* /messages（REST）との二重検証ルート

が正式に仕様化された。

---

## **3. Next Action（唯一の次アクション）**

### 🎯 **A. Environment Layer（env_loader） — スキーマ整合レビュー（v0.2.3 準拠）**

既に v0.4.3 で設定された最優先タスクであり、変更しない。

対応内容：

1. Schema Freeze（構造不変）の実コード検証
2. MissingSecretError のメッセージ仕様統一
3. 暗黙の fallback/profile 自動生成の禁止
4. CI 非干渉の保証
5. 設計書 v0.2.3 の拘束ルールとの完全一致を確認

※ **Next Action は常に 1 つのため、優先度最高のこのタスクを保持する。**

---

## **4. Next Next Action（次の主要タスク）**

### 🟦 **B. probe v0.2 — GraphQL createData 監視 ＋ assistant テキスト抽出（実装フェーズ）**

目的：

* GraphQL createData のストリームを sandbox でリアルタイム観測
* assistant# prefix を持つ value を抽出
* /messages（REST）の assistant.content と整合性を検証
* 回答検知ロジックの v0.2 を実装し、最終確定方式を二重化する

---

## **5. Roadmap（後続フェーズ）**

### 🔰 **C. XHR/GraphQL フュージョン方式の検証**

* ベストエフォートではなく **最終回答を確実に取得する方式** の設計
* REST（/messages）と GraphQL（createData）の差異と同期点の明文化

### 🔰 **D. ChatPage.ask v0.6 — 回答検知の刷新案**

* DOM 依存方式（案B）から離脱
* XHR/GraphQL ハイブリッド検知
* テスト基盤での誤判定ゼロ化

### 🔰 **E. CI 上での回答検知安定化**

* GitHub Actions 上の実行差分を吸収
* タイムアウト／ランダム遅延の対策
* 収束条件の formalization（形式化）

---

## **6. Risks / Issues（リスク・課題）**

（v0.4.3 の内容を維持しつつ Answer Detection 特有の追加リスクを補足）

### ⚠ GraphQL スキーマ変更への脆弱性

回答検知ロジックが AppSync の内部構造に依存するため、監視が必要。

### ⚠ assistant.value の prefix フォーマットに揺らぎがある可能性

sandbox v0.1 から判明したため、v0.2 で対策する。

---

## **7. Required References（参照すべき資料）**

* **Design_env_v0.2.3（最新仕様）** 
* **PROJECT_GRAND_RULES v4.2**（AI拘束規範） 
* **Debugging_Principles v0.2**（推測禁止・一次情報確認） 
* **Responsibility_Map v0.1**（env_loader の責務境界）
* **Design_ci_e2e_v0.1**（CI の非依存性確認）
* Startup Template v3.1（運転層）
* CHANGELOG（v0.2.1 → v4.2 履歴確認） 

* Design_chat_answer_detection_v0.1.md
* Design_probe_graphql_answer_detection_v0.1.md

---

## **8. Version**

### **v0.4.4 — Answer Detection Integration + Priority Queue Edition**

Next Action を維持しながら回答検知フェーズを正式統合し、
Next Next Action／Roadmap を正しく整列させた版。

---
