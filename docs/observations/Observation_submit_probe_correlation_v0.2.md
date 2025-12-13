# 📘 Observation_submit_probe_correlation_v0.2.md

**Title:** submit–probe correlation (REST-only Established case)
**Version:** v0.2
**Status:** Observation
**Observed At:** 2025-12-13
**Source:** gov-llm-e2e-testkit
**Related Designs:**

* Design_submit_probe_correlation_v0.2
* Design_probe_graphql_answer_detection_v0.2

---

## 1. Observation Purpose（観測目的）

本観測は、以下の事実を**一次情報として固定**することを目的とする。

* GraphQL createData が **発火しないケース**
* REST GET `/messages` により **assistant 応答が取得できるケース**
* 上記において
  **submit ↔ answer の相関が「成立（Established）」と判定されること**

本ドキュメントは **設計の正当性を検証するための観測記録**であり、
設計変更・最適化・将来予測は一切含まない。

---

## 2. Execution Context（実行条件）

* 実行スクリプト:
  `python -m scripts.run_probe_once --seconds 90`
* 利用テンプレート:
  `template_prepare_chat_v0_1.py`（ChatPage.submit v0.6 使用）
* Answer Detection Layer:
  probe v0.2.1
* UI 操作:

  * login
  * chat selection
  * submit（1回）

---

## 3. Console Output（一次ログ抜粋）

```text
[template] submit returned submit_id=c78b4d15-dae7-4737-8a72-df9e309507d8
[template] chat_id = 09644865-165a-4aa4-92f2-3519ef2aad0c
[run_probe_once] Probe finished.
```

---

## 4. summary.json（一次成果物）

```json
{
  "chat_id": "09644865-165a-4aa4-92f2-3519ef2aad0c",
  "status": "no_graphql",
  "correlation_state": "Established",
  "first_graphql_ts": null,
  "graphql_answer": null,
  "rest_answer": "...assistant response...",
  "has_post": true,
  "has_get": true,
  "has_graphql": false,
  "event_count": 8
}
```

---

## 5. Observed Facts（観測事実）

以下の事実が観測された。

1. UI submit により REST POST `/messages` が発生した
2. GraphQL createData は **発火しなかった**
3. REST GET `/messages` により assistant 応答が取得できた
4. probe summary において

   * `status = "no_graphql"`
   * `correlation_state = "Established"`
     が同時に記録された

---

## 6. Interpretation Boundary（解釈境界）

本観測から **言えること**：

* GraphQL 非発火であっても、
  REST 経路による assistant 応答が観測できる
* この場合、submit–answer の相関は
  **「Established」と判定され得る**

本観測から **言えないこと**：

* なぜ GraphQL が発火しなかったか
* AI が「答えようとしたが答えられなかった」かどうか
* サーバ内部状態・モデル挙動

---

## 7. Design Implication（設計への含意）

本観測は、以下の設計判断を**事実ベースで支持する**。

* submit–probe 相関は
  **GraphQL に依存してはならない**
* 相関状態（correlation_state）は
  probe 内部 status とは独立して定義されるべきである
* REST-only ケースを
  「失敗」と誤認しない設計は必須である

※ 本章は設計変更を提案するものではなく、
既存設計（v0.2）の前提条件を裏付けるものである。

---

## 8. Related Artifacts（関連成果物）

* logs/xhr_probe_20251213_151316/

  * graphql_probe.jsonl
  * summary.json

---

## 9. Conclusion（結論）

本観測により、

> **GraphQL 非発火・REST-only 応答という実環境の挙動においても、
> submit–answer 相関は「Established」として成立し得る**

という事実が、一次情報として確認・固定された。

---

### End of Observation

---
