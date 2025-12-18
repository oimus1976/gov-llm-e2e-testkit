---
title: F4_RAG_Evaluation_Results
project: gov-llm-e2e-testkit
phase: F4 (RAG Evaluation)
version: v0.1
status: Template (Revised)
execution_order: HTML -> Markdown
date: YYYY-MM-DD
---

# F4 RAG 評価結果ログ（v0.1 / 改訂版）

## 0. 実験前提（固定・再掲）

- 実行順：**HTML → Markdown**
- 評価基準：RAG 評価基準 v0.1
  - Evidence Hit Rate
  - Hallucination Rate
  - Answer Stability
- Golden Question Pool / Golden Ordinance Set：**消費しない**
- 本ログは **差分観測のみ**を目的とする
  （良否・優劣の断定は行わない）

---

## 1. Case Information（固定）

| 項目 | 内容 |
|---|---|
| Case ID | Case-1 / Case-2 / Case-3 |
| 対象条例 | k518RGXXXXXXXX |
| ケース概要 | （例：目的条文の基本検索） |
| 使用質問 | （質問文をそのまま貼付） |
| Evidence語リスト | （3–8語・固定） |

---

## 2. Execution Log

### Run 1

---

#### HTML（Before）

- 実行日時：
- 実行条件：HTML
- chat_id / submit_id（取得できる場合）：

**Raw Answer（無加工）**

```text
（answer_text をそのまま貼る）
```

##### Evidence Hit（観測）

- Evidence語リスト： [ , , ]
- 出現語： [ , ]
- Hit Count： X
- Total： Y
- **Hit Rate： X / Y**

##### Hallucination Check（v0.1 定義）

- [ ] 根拠条文なしの断定表現
- [ ] 存在しない制度・義務の生成
- [ ] 条文にない数値・期限の生成

- 備考（事実のみ）：

##### Stability Note（Run 単位・観測）

- Evidence語の有無：
- 記述構成（段落 / 箇条書き 等）：

---

#### Markdown（After）

- 実行日時：
- 実行条件：Markdown
- chat_id / submit_id（取得できる場合）：

**Raw Answer（無加工）**

```text
（answer_text をそのまま貼る）
```

##### Evidence Hit（観測）

- Evidence語リスト： [ , , ]
- 出現語： [ , ]
- Hit Count： X
- Total： Y
- **Hit Rate： X / Y**

##### Hallucination Check（v0.1 定義）

- [ ] 根拠条文なしの断定表現
- [ ] 存在しない制度・義務の生成
- [ ] 条文にない数値・期限の生成

- 備考（事実のみ）：

##### Stability Note（Run 単位・観測）

- Evidence語の有無：
- 記述構成（段落 / 箇条書き 等）：

---

### Run 2
（Run 1 と同一フォーマット）

---

### Run 3
（Run 1 と同一フォーマット）

---

## 3. Stability Summary（Case 単位 / N=3）

| 観点 | HTML | Markdown |
|---|---|---|
| Evidence語の出現 | 安定 / 不安定 | 安定 / 不安定 |
| 記述構成 | 安定 / 不安定 | 安定 / 不安定 |
| 抜け・過剰生成 | なし / あり | なし / あり |

※ 「安定」とは **3 Run すべてで同一傾向**を示した場合のみ。

---

## 4. Case-level Difference Summary（差分観測）

- HTML 側の傾向（事実）：
- Markdown 側の傾向（事実）：
- 差分として観測できた点：
- v0.1 指標では判断不能な点：

---

## 5. 判定メモ（結論は書かない）

※ ここでは **良い / 悪い** を書かない
※ **「何が変わったか」のみを記述**

- Markdown 化によって増えた情報：
- Markdown 化によって減った情報：
- ノイズ耐性の変化：

---

## 6. Notes / Follow-up

- 再実行が必要な点：
- v0.2 で評価すべき観点：


---

## この改訂版で満たしていること（確認）

* ✅ Evidence Hit Rate が **数値として固定**
* ✅ Hallucination 判定が **v0.1 定義に限定**
* ✅ Stability が **Run → Case で因果接続**
* ✅ 観測と判断の分離
* ✅ 将来の CI / 自動集計を阻害しない

---
