---
title: "Decision Record: F10-A Execution Context Generation Policy"
version: v0.1
status: accepted
date: 2026-01-12
scope:
  - F10-A
related_decisions:
  - decision_record_F10A_Submit_Waiting_v0.2.md
depends_on:
  - decision_record_F10A_Submit_Waiting_v0.2.md
supersedes: null
---

# Decision Record: F10-A Execution Context Generation Policy

## 1. 結論（Decision）

F10-A フェーズにおける `execution_context` の生成方針は、以下のとおりとする。

- **GENERATED（answer.md が生成された場合）**
  - `execution_context.json` は生成しない
- **UNGENERATED（answer.md が生成されなかった場合）**
  - 原因説明・事実記録として `execution_context.json` を生成する

すなわち、

> `execution_context` は  
> **UNGENERATED 状態の説明責任を果たすための補助成果物**  
> として位置づける。

---

## 2. 背景（Background）

F10-A は「評価用成果物生成フェーズ」であり、以下が前提として確定している。

- 評価・正誤判断は行わない
- pytest は契約保証のみに限定される
- 完走（run を最後まで進めること）を最優先する

これに伴い、Submit Waiting の方針（Decision Record v0.2）において、

- submit が blue になるまで待機する
- タイムアウト時は UNGENERATED として扱う

という判断が確定した。

しかしその時点では、

- **UNGENERATED 時に何を成果物として残すか**
- **execution_context を常時生成すべきか否か**

が未整理のまま、実装と検証が進行していた。

---

## 3. 問題意識（Problem Statement）

現状の F10-A 実行では、1 問あたり以下のような多数の成果物が既に生成されている。

- raw HTML / text
- DOM 抽出関連ファイル
- submit_diagnostics.json
- 各種 verify / snapshot ファイル

この状態でさらに `execution_context` を **常時生成**すると、

- GENERATED / UNGENERATED の区別が曖昧になる
- 成果物量が過剰になり、読み手の負荷が増大する
- 「なぜこの execution_context が存在するのか」が不明瞭になる

という問題が顕在化した。

---

## 4. 採用しなかった案（Rejected Options）

### 案A：常時 execution_context を生成する

- GENERATED / UNGENERATED の分岐が不要になる利点はある
- しかし以下の理由で却下した
  - GENERATED 時は既存成果物で事実再構成が可能
  - execution_context の存在意義が希薄になる
  - F10-A 成果物の「軽量・機械的生成」という性質に反する

### 案B：execution_context を一切生成しない

- 成果物を最小化できる利点はある
- しかし以下の理由で却下した
  - UNGENERATED 時に「なぜ生成されなかったか」を説明できない
  - 事後分析・再現時に判断材料が不足する

---

## 5. 採用理由（Rationale）

本決定では、

- **GENERATED**
  - → answer.md および既存の補助成果物で十分
- **UNGENERATED**
  - → 状態説明用の追加メタ情報が必要

という役割分担を明確にした。

これにより、

- 成果物の意味づけが明確になる
- UNGENERATED のみが「例外的状態」として可視化される
- F10-A の「評価しない・加工しない」という原則を維持できる

---

## 6. 実装への影響（Implementation Notes）

- `execution_context.json` の生成条件は  
  **UNGENERATED 時のみ**とする
- GENERATED 時に execution_context を生成しないことは  
  **仕様上の正常系**であり、欠落ではない
- UNGENERATED 判定ロジック自体は、本 Decision Record のスコープ外とする
  - Submit Waiting / timeout / UI ack 判定は別 Decision Record に従う

---

## 7. 将来の見直し条件（Revisit Criteria）

以下の場合、本 Decision Record の見直しを検討する。

- F10-A 成果物の最小構成が再定義された場合
- GENERATED 時にも execution_context 相当の説明責任が求められた場合
- F10-B 以降の評価フェーズから、追加メタ情報の恒常的要求が発生した場合

---

## 8. 状態まとめ（One-liner）

> execution_context は  
> **UNGENERATED 状態を説明するためにのみ生成される補助成果物である。**
