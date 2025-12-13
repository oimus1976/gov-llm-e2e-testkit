# 📘 PROJECT_STATUS v0.5.1 — E2E 基盤確定（確認 CI 明文化）/ RAG QA 自動化フェーズ開始

**Last Updated:** 2025-12-13
**Maintainer:** Sumio Nishioka & ChatGPT (Architect Role)

---

## 1. Current Focus（現在の主眼）

本プロジェクトは、
**例規 HTML 変換プロジェクトにおける RAG 品質を
人手ではなく自動テストで担保する**ことを最終目的としている。

Phase 1〜6 では、その前提条件として、

* UI 送信
* 回答検知
* submit–probe 相関
* CI 上での誤解のない可視化

からなる **E2E テスト基盤の土台**を構築・確定した。

これらは **基盤確認 CI（Foundation CI）** として
Design_ci_e2e_v0.1.1 により正式に位置づけられた。

---

## 2. Completed（完了・ダイジェスト）

### ✅ E2E 基盤（Phase 1〜6）— 完全確定

* Environment Layer（env_loader v0.2.3）QA 完了・凍結
* ChatPage.submit v0.6

  * UI 送信責務のみに限定
  * submit_id / SubmitReceipt 定義確定
* Answer Detection Layer（probe v0.2.1）成立

  * REST-only / GraphQL 非発火ケースを包含
* submit–probe 相関設計 v0.2 正式採用

  * 相関を **アルゴリズムではなく状態（state）**として定義
* CI Correlation Summary Presentation Semantics v0.1 確定

  * PASS / WARN / INFO を表示意味論として整理
  * WARN / INFO を FAIL と誤認しない設計を保証
* GitHub Actions summary による
  **日本語 E2E 相関サマリーを正式採用**
* 英語版との設計差分ゼロ対照表を保存
* Phase 5（条件軸 × matrix 実験）は完了・撤去

👉 **CI 上で「次に何をすべきか」が即座に判断可能な状態を達成**

---

## 3. Deferred / Out of Scope（第1章で扱わなかった事項）

### ⏸ RAG 系テスト（basic / advanced）

* `test_rag_basic_*`
* `test_rag_advanced_*`

理由：

* RAG QA は **E2E 基盤が信用できることが前提**
* Phase 1〜6 では基盤確立を最優先とした

位置づけ：

なお、Deferred 状態は
「未完成」ではなく
**基盤確認 CI から RAG QA CI への段階遷移を前提とした設計上の判断**
である。


---

## 4. Next Action（第2章の開始）

### 🎯 Playwright を用いた RAG QA 自動化への移行

本プロジェクトの Next Action は明確である。

> **Design_playwright_v0.1 に基づき、
> Playwright を用いた RAG QA 自動化を本格的に開始する。**

具体的には：

* Smoke Test を「基盤確認 CI」から「QA エントリポイント」へ段階的に拡張
* Basic RAG Test の再導入

  * 固定ケース × YAML 定義による再現可能 QA
* Advanced RAG Test の設計検討

  * 複数ターン・例外系・時間制御
* RAG テストデータ設計（期待値・許容揺らぎ）の具体化
* LGWAN / INTERNET 両環境での実行整理

本フェーズでは、
**E2E 基盤は“触らない前提”**とし、
その上に QA ロジックを積み上げる。

---

## 5. Roadmap（第2章・概略）

### Phase B. RAG QA 自動化（Playwright）

* Basic RAG Test v0.1
* テストデータ（YAML）運用確立
* 判定基準（semantic / keyword / heuristic）の整理

### Phase C. 高度化・運用整理

* Advanced RAG Test
* 長時間・非同期揺らぎの扱い
* LGWAN 実行手順の文書化
* ログ・差分の可視化改善

---

## 6. Risks / Issues（引き続き意識すべき点）

* LLM 応答の非決定性
* AppSync / UI 変更によるロケータ揺らぎ
* RAG ナレッジ更新による期待値変動
* LGWAN 制約下でのログ持ち出し運用

※ いずれも **基盤ではなく QA レイヤ側で扱う課題**

---

## 7. Required References（主要参照）

* Design_playwright_v0.1
* Design_env_v0.2.3
* Design_submit_probe_correlation_v0.2
* Design_CI_Correlation_Summary_v0.1
* Debugging_Principles v0.2
* PROJECT_GRAND_RULES v4.2
* CHANGELOG

---

## 8. Version

### v0.5.1 — 基盤確認 CI の意味論確定 / Phase B 接続準備完了

Design_ci_e2e_v0.1.1 により、
CI は **E2E 基盤の成立性を確認するフェーズ**であることが明文化された。

本バージョン以降、
RAG QA（Basic / Advanced）は
基盤を変更せず、上位レイヤとして再接続される。


### v0.5.0 — E2E 基盤確定 / RAG QA 自動化フェーズ開始

Phase 1〜6 により
**E2E 基盤は完成・固定**。

本バージョン以降は、
この基盤の上で **RAG QA 自動化を主眼とする第2章**に入る。

---
