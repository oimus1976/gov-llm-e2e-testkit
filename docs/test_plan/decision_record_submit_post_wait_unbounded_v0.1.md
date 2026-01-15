---
title: Decision Record – Submit後の無制限待機ポリシー
id: decision_record_submit_post_wait_unbounded
version: v0.1
status: ACCEPTED
date: 2026-01-13
scope:
  - F8
  - F10-A
affected_components:
  - run_single_question.py
  - f8_orchestrator.py
  - run_question_set.py
keywords:
  - submit
  - ui_ack
  - UNGENERATED
  - non-fatal
  - unbounded-wait
---

## 1. 決定事項（Decision）

**submit が成立した後は、UI 応答（ui_ack / dom_extraction）を無制限に待機する。**  
submit 後に応答が観測できない場合でも、例外は送出せず run を継続する。

submit 後の状態は以下のいずれかとして記録される：

- **GENERATED**  
  - 回答本文（answer.md）が生成された
- **UNGENERATED**  
  - 回答本文は生成されなかったが、submit は成立している

いずれの場合も **run 全体は中断されない**。

---

## 2. 背景（Context / Motivation）

実行ログおよび一次情報から、以下の事実が確認された。

- submit ボタンが blue になり click された後でも、
  - `ui_ack=False`
  - `dom_extraction unavailable`
  が観測されるケースが **実運用で頻発**する
- ui_ack=False は UI の不整合や遅延を示すものであり、
  **submit 自体の失敗を意味しない**
- 従来の実装では、submit 後に一定時間で timeout → `SubmitConfirmationError`
  が送出され、run 全体が abort していた
- その結果、
  - 条例単位・質問単位で再現性のない中断
  - GENERATED / UNGENERATED の切り分け不能
  が発生していた

本プロジェクトの目的は **評価ではなく観測**であり、
「待った結果、生成されなかった」という事実自体が重要な成果物である。

---

## 3. 採用しなかった案（Rejected Alternatives）

### A. timeout を延長する案

- timeout を延ばしても、根本的に「待ち切る」保証がない
- 遅延が長い場合に同じ問題が再発する

### B. F10-A のみ無制限にする案

- submit 挙動は F10-A 固有ではない
- プロジェクト全体で一貫した原則を持たないと将来破綻する

### C. fatal_submit_error を orchestrator 側で握りつぶす案

- 例外の意味論が壊れる
- submit 後フェーズが「失敗扱い」になる構造自体が不適切

---

## 4. 実装上の指針（Implementation Policy）

### 4.1 submit 成立の定義

- submit ボタンが **blue 状態で click された時点**をもって submit 成立とする
- submit 成立は `submit_diagnostics.json` により一次証跡として必ず記録する

### 4.2 submit 後の挙動

- submit 後は **無制限待機フェーズ**に入る
- 以下を理由に例外を送出してはならない：
  - ui_ack が観測できない
  - dom_extraction が unavailable
- UNGENERATED は **正常な結果区分**であり run 失敗ではない

### 4.3 エラー扱いの禁止事項

- submit 後に `SubmitConfirmationError` を送出してはならない
- submit 後を理由に run_f8_collection を abort してはならない

---

## 5. 成果物への影響（Impact）

- run は条例数・質問数に関わらず **完走可能**になる
- UNGENERATED を含む実行結果が **構造的に説明可能**になる
- markdown-id / message-id の逆行検出が安定する
- 例規 HTML 変換プロジェクトへの引き渡し成果物として
  再現性・信頼性が向上する

---

## 6. 今後の検討事項（Open Questions）

- 無制限待機中にユーザーが中断した場合の記録方法
- 長時間待機（数時間以上）の区別・可視化
- 進捗ログの粒度・頻度

（※ 本 Decision Record では扱わない）

---

## 7. 決定の有効範囲

本 Decision は以下に適用される：

- F10-A
- F8
- 今後追加される submit を伴う全実行モード

**本 Decision を覆す場合は、新たな Decision Record を作成すること。**
