# 🧪 E2E 相関サマリー — submit–probe v0.2

## 概要（Overview）

この CI 実行結果は、次の 2 つの事実関係について  
**「観測できたかどうか」**を要約したものです。

- UI からの送信（ChatPage.submit v0.6）
- 回答検知レイヤー（probe v0.2）による応答観測

### 判定の基本方針

> **相関（correlation）は「成功 / 失敗」ではなく「状態」です。**

⚠️ **WARN / INFO は CI 失敗を意味しません。**  
観測事実が限定的だった、または判断不能だった状態を  
**そのまま表示しているだけ**です。

---

## 相関結果（Correlation Result）

| 項目 | 値 |
| --- | --- |
| submit_id | `${SUBMIT_ID}` |
| chat_id | `${CHAT_ID}` |
| correlation_state | **${CORRELATION_STATE}** |
| CI 表示ラベル | **${CI_RESULT}** |

---

## 状態の意味（State Interpretation）

- **Established（PASS）**  
  回答が観測され、この送信と **説明可能な形で相関づけられました**。

- **Not Established（WARN）**  
  回答は存在する可能性がありますが、  
  この送信との **一意な相関を説明できませんでした**。

- **No Evidence（INFO）**  
  観測ウィンドウ内で、この送信に関連する回答は  
  **観測されませんでした**。

- **Unassessed（INFO）**  
  今回の実行では、相関判定を **意図的に行っていません**。

---

## この結果が「意味しないこと」

このサマリーは、次のことを **判断しません**。

- 回答内容の正しさ・品質
- AI の意図や内部状態
- 内部エラーや障害の有無
- なぜ回答が生成されなかったか

あくまで **観測できた事実のみ**を表示しています。

---

## 行動ガイド（Action Guidance）

| correlation_state | CI ラベル | 対応 | 補足 |
|------------------|----------|------|------|
| Established | PASS | 不要 | 相関は説明可能 |
| Not Established | WARN | 任意 | 相関が必要な場合のみ再実行 |
| No Evidence | INFO | 不要 | 連続発生時のみ調査 |
| Unassessed | INFO | 不要 | 想定どおり |

---

## 設計上の制約（重要）

この CI 表示は、以下の設計制約を **意図的に守っています**。

- ❌ 観測事実を超えた推測をしない
- ❌ 曖昧さを理由に CI を FAIL させない
- ❌ 内部実装や AI の状態を推定しない
- ✅ 相関は常に **状態（state）**として扱う
- ✅ PASS / WARN / INFO は **表示上の意味づけ**のみ

---

## 参考資料（References）

- Design_submit_probe_correlation_v0.2
- Design_CI_Correlation_Summary_v0.1
- Debugging_Principles_v0.2
- PROJECT_GRAND_RULES v4.x

---

## 補足情報（Optional Diagnostics）

<details>
<summary>観測されたシグナル（参考情報）</summary>

- REST GET /messages 観測: `${REST_OBSERVED}`
- GraphQL createData 観測: `${GRAPHQL_OBSERVED}`
- イベント時刻: `${EVENT_TIMESTAMPS}`

</details>
