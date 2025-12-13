# 📄 日英 Summary 対照表（設計差分ゼロ確認）

## 目的  

* 日本語版が **英語設計を一切逸脱していない**ことを保証する
* 将来の修正時に「どこを触ってはいけないか」を明確にする

---

## 1️⃣ 全体方針の一致確認

| 観点      | 英語版                    | 日本語版         | 差分     |
| ------- | ---------------------- | ------------ | ------ |
| 判定軸     | Correlation is a state | 相関は「状態」      | ❌ 差分なし |
| 成否判定    | Not success/failure    | 成功/失敗ではない    | ❌      |
| 推測禁止    | Observable facts only  | 観測事実のみ       | ❌      |
| FAIL 回避 | WARN/INFO allowed      | WARN/INFO 明示 | ❌      |

---

## 2️⃣ コア用語・状態名の一致

| 項目                | 英語版                 | 日本語版                | 差分 |
| ----------------- | ------------------- | ------------------- | -- |
| correlation_state | correlation_state   | correlation_state   | ❌  |
| Established       | Established         | Established         | ❌  |
| Not Established   | Not Established     | Not Established     | ❌  |
| No Evidence       | No Evidence         | No Evidence         | ❌  |
| Unassessed        | Unassessed          | Unassessed          | ❌  |
| CI labels         | PASS/WARN/INFO      | PASS/WARN/INFO      | ❌  |
| Identifiers       | submit_id / chat_id | submit_id / chat_id | ❌  |

👉 **翻訳・言い換え一切なし**

---

## 3️⃣ 状態説明（State Interpretation）の対応

### Established

| 英語版                    | 日本語版      | 差分 |
| ---------------------- | --------- | -- |
| explainably correlated | 説明可能な形で相関 | ❌  |

### Not Established

| 英語版                            | 日本語版         | 差分 |
| ------------------------------ | ------------ | -- |
| cannot form unique correlation | 一意な相関を説明できない | ❌  |
| based on observable facts      | 観測事実から説明できない | ❌  |

※ 日本語版は **明示的に「観測事実」を補足**
→ **意味の限定であり、拡張ではない**

---

### No Evidence

| 英語版                             | 日本語版           | 差分 |
| ------------------------------- | -------------- | -- |
| no observable response detected | 観測されなかった       | ❌  |
| no inference on generation      | 生成されなかったとは限らない | ❌  |

👉 **誤解防止の補足のみ（意味拡張なし）**

---

## 4️⃣ What This Result Means / 意味しないこと

| 英語版                        | 日本語版   | 差分 |
| -------------------------- | ------ | -- |
| does not judge correctness | 判断しない  | ❌  |
| does not infer intent      | 推定しない  | ❌  |
| observable facts only      | 観測事実のみ | ❌  |

---

## 5️⃣ Action Guidance の一致

| 状態              | 英語版                     | 日本語版    | 差分 |
| --------------- | ----------------------- | ------- | -- |
| Established     | No action               | 不要      | ❌  |
| Not Established | Optional retry          | 任意      | ❌  |
| No Evidence     | Investigate if repeated | 連続時のみ調査 | ❌  |
| Unassessed      | Expected                | 想定どおり   | ❌  |

---

## 6️⃣ 設計制約（Explicit Constraints）

| 制約                     | 英語版 | 日本語版 | 差分 |
| ---------------------- | --- | ---- | -- |
| No speculation         | 明示  | 明示   | ❌  |
| No FAIL on ambiguity   | 明示  | 明示   | ❌  |
| State-based evaluation | 明示  | 明示   | ❌  |

---

## 7️⃣ 差分総括（重要）

### 差分の性質

* ❌ 意味論の変更：なし
* ❌ 判定基準の追加・削除：なし
* ❌ 用語変更：なし
* ✅ 誤解防止の補足：あり（日本語のみ）

### 判定

> **日本語版 summary は、
> 英語版 summary の「意味論を完全保存した表現違い」である**

---

## 8️⃣ 将来修正時のルール（明文化）

- 英語版は「設計原典」とする
- 日本語版は「運用表示」とする
- 相関状態・用語・判定基準は英語版に従う
- 日本語版での変更は、必ず本対照表を更新する

---

## 最終評価（設計保証）

> この対照表により、
> 日本語 summary 正式版は
> **設計差分ゼロであることが保証された**。

---
