# Probe Waiting Condition — Completion Semantics 再検討 v0.1
**Type:** design_memo  
**Status:** Observation / Design Consideration (Non-normative)  
**Last Updated:** 2025-12-12

---

## 0. この文書の位置づけ

本メモは **probe v0.2.x における「待機条件（completion condition）」**を再検討するための
**設計メモ（design_memo）**である。

- 本文書は **設計書（Design_XXX）ではない**
- 仕様・実装を拘束しない
- 既存の Design_chat_answer_detection_v0.1 / Design_probe_graphql_answer_detection_v0.1 を
  **変更・否定しない**

目的は、今回の実測結果を踏まえ、
**「何をもって probe が完了したと判断すべきか」**を言語化することにある。

---

## 1. 背景

probe v0.2.1 / run_probe_once.py では、以下の方式を採用している。

- 送信後、一定時間（例：30 秒）イベントを監視
- 時間経過後に probe を終了
- GraphQL createData / REST /messages の観測有無に基づき status を決定

しかし実測により、以下の事象が確認された。

- 長文・構造化・制約付き質問において、
  **回答生成が完了する前にタイムアウトするケース**
- UI 上では生成が継続しているにも関わらず、
  probe は「no_graphql」として終了する

この結果、「時間による区切り」が
**回答検知・完了判定として不適切である可能性**が顕在化した。

---

## 2. 確認された一次情報（事実）

今回の実測から、以下は確定事実である。

- POST /messages は正常に発生している
- 回答生成は UI 上で継続している
- 一定時間内に以下が観測されない場合がある：
  - REST GET /messages
  - GraphQL createData
- 時間上限に達すると probe が終了するため、
  **生成完了後のイベントが観測されない**

重要なのは：

> **「イベントが出なかった」ことと  
> 「イベントが出る前に観測を打ち切った」ことは区別すべきである**

---

## 3. 問題点の整理（時間待ち方式）

時間ベースの待機方式には、以下の問題がある。

### 3.1 環境依存性

- 質問内容による生成時間のばらつき
- 回線・負荷・環境（INTERNET / LGWAN / CI）の差異

### 3.2 意味論の欠如

- 「30 秒」「60 秒」に意味的根拠がない
- 完了していない生成を「no_graphql」と誤判定するリスク

### 3.3 Answer Detection 設計との乖離

- Answer Detection Layer は
  **「意味的な収束点」を検出する層**
- 単なる時間経過は、意味的収束を表さない

---

## 4. 再検討すべき「完了」の定義

probe における「完了」とは、次のいずれかである可能性がある。

### 4.1 意味的完了候補（列挙）

以下は **候補であり、確定ではない**。

1. REST GET /messages において
   - assistant ロールの最終メッセージが取得できた
2. GraphQL messages query において
   - assistant ロールが確定状態で取得できた
3. GraphQL createData の streaming が終了したことを示すイベント
4. 複数経路（REST / GraphQL）の整合が取れた状態

### 4.2 非採用候補（明示）

以下は完了条件として不適切と考えられる。

- UI 上の DOM 文言変化
- ボタン状態（送信アイコン等）
- 単純な時間経過のみ

---

## 5. 改善方向性（暫定的）

現時点での妥当な方向性は以下と考えられる。

- **基本方針**
  - 時間待ちを主条件にしない
  - 意味的イベントを主条件とする
- **現実的制約**
  - 無限待機は不可
  - フォールバックとして時間上限は必要

これにより：

> **「意味的イベント待ち ＋ 時間上限」**
という二段構えが検討対象となる。

---

## 6. status 判定粒度の見直し案（参考）

現行の `no_graphql` だけでは、
状態の違いが表現しきれない可能性がある。

検討余地のある status 例：

- `timeout_before_completion`
- `completed_rest_only`
- `completed_with_graphql`
- `inconclusive`

※ 本節はアイデア列挙であり、仕様提案ではない。

---

## 7. 次の判断ポイント

本メモを踏まえ、次の判断が必要となる。

- probe v0.2.x の待機条件を
  - design_memo に留めるか
  - Design_probe_graphql_answer_detection_v0.2 として昇格させるか
- run_probe_once.py の改修に着手するか
- Answer Detection Layer v0.2 全体設計へ進むか

これらは、追加の実測結果および設計合意をもって決定される。

---

## 8. まとめ

- 時間待ち方式は、完了判定としてリスキーである
- 今回の実測は、そのリスクを一次情報で示した
- 「何を待つべきか」を定義しないまま実装を進めるべきではない
- 本メモは、その定義を行うための前段整理である
