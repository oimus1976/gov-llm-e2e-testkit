---
template_name: DesignNote_TestToMain_Promotion
template_version: v0.1
template_purpose: >
  Capture and structure insights observed in test code
  before promoting them into formal design documents.
usage:
  - Copy this file into docs/design/
  - Rename the file to reflect a concrete topic
  - Do NOT treat this template itself as a design decision
---

# Design Note (Pre-Design): Test-to-Main Promotion

## 0. Positioning（重要）

この文書は **設計文書ではない**。

- 本テンプレートは  
  **テストコード中で得られた知見を、設計として昇格させるか検討するための思考補助**である
- 本テンプレート自体は  
  - PROJECT_STATUS を更新しない
  - CHANGELOG を更新しない
  - 実装を変更しない
- 設計判断が確定した場合のみ、  
  **別途 Design_*.md として起こす**

---

## 1. Purpose（このノートでやること）

- テスト中に観測された挙動・工夫・成立条件を記録する
- なぜそれが成立していたのかを **構造的に説明する**
- main 実装に昇格させる場合の論点を洗い出す

※ 採用・不採用の判断はここでは行わない

---

## 2. Observation（観測された事実）

※ 事実のみを書く  
※ 評価語（良い／速い／便利）は使わない

- 観測元：
  - テスト名／スクリプト名：
  - 実行条件（環境・前提）：
- 観測された挙動：
  - （例）UI 状態遷移を検知後、即座に次アクションが実行された
  - （例）固定 sleep を用いずに進行していた

---

## 3. Why It Worked（なぜ成立していたか）

※ 推測ではなく、構造として説明する

- どの状態を一次情報として扱っていたか
- どの前提が固定されていたか
- どの責務をテストコード側で肩代わりしていたか

---

## 4. Gap to Main Execution（main 実装との差分）

- main 側で一般化されている点：
- テスト側で省略されていた点：
- 両者の差が生む影響（事実ベース）：

---

## 5. Responsibility Mapping（昇格するならどこか）

※ 実装方法は書かない  
※ 「置き場所」だけを整理する

| 知見 | 想定される責務レイヤ | 理由 |
| ---- | ---- | ---- |
| <知見> | <想定される責務レイヤ> | <理由> |

---

## 6. Speed Regression Review（速度低下の観点洗い出し）

※ 実装せず、観点のみ列挙

- 状態遷移を時間待ちで代替していないか
- 同一条件を多重に確認していないか
- 将来フェーズの安全弁を先取りしていないか
- テスト専用の前提を main 側でも維持しようとしていないか

---

## 7. Non-Goals（このノートでやらないこと）

- 実装修正案の提示
- パフォーマンス改善の数値評価
- pytest / CI の再設計
- 採否判断の確定

---

## 8. Next Step（このノートの次）

- Adopt（設計文書として起こす）
- Defer（記録として残す）
- Reject（今回は扱わない）

※ 判断はフェーズ責務に従って行う
