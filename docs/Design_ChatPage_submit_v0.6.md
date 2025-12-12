# 📘 **Design_ChatPage_submit_v0.6**

ChatPage **submit API** Design — Responsibility-Separated Version
**Version:** v0.6
**Status:** Design
**Last Updated:** 2025-12-13

---

## 0. Scope and Positioning（重要）

本書は **ChatPage.submit() API の設計のみ**を定義する。

* 本書は `Design_ChatPage_v0.5.md` を **置き換えない**
* 本書は **DOM ベースの回答検知・ストリーミング制御を定義しない**
* 本書は以下の責務分離を明確化する：

  * **UI 送信責務**（ChatPage.submit）
  * **意味的完了検知責務**（Answer Detection Layer / probe）

> **Design Principle**
> *Submission semantics and completion semantics must never be defined in the same layer.*

---

## 1. Background（背景）

従来の `ChatPage.ask()` は、以下を単一 API に内包していた：

* UI 入力・送信
* DOM 変化によるストリーミング検知
* 回答本文の抽出・完了判定

しかし実測の結果（2025-12）：

* GraphQL createData が発火しないケースが存在
* DOM 構造は不安定で、意味的完了点を保証できない
* REST `/messages` のみが最終回答の信頼可能な取得経路

このため **回答完了の意味論を UI レイヤから完全分離**する必要が生じた。

---

## 2. Purpose（目的）

`ChatPage.submit v0.6` の目的は **1つだけ**である。

> **ユーザー入力を Qommons UI に確実に送信し、
> その送信が UI に受理されたことを検証可能な形で返すこと。**

`submit()` は **回答を返さない**。
回答の取得・完了判定は **Answer Detection Layer（probe v0.2+）の責務**である。

---

## 3. Responsibility Boundary（責務境界）

### 3.1 ChatPage.submit が責任を持つもの

ChatPage.submit **MUST**：

* 入力欄にメッセージを投入する
* 送信操作を実行する
* UI が送信を受理したことを **最小限で検証**する
* 送信試行を一意に識別する ID を生成する
* UI 側の失敗時に証跡（evidence）を収集する

---

### 3.2 明示的に責任を持たないもの（重要）

ChatPage.submit **MUST NOT**：

* 回答完了を判定する
* ストリーミング状態を解釈する
* 回答本文を取得・返却する
* REST / GraphQL の差分を吸収する
* semantic completion を定義する

これらは **Answer Detection Layer（probe）専属責務**である。

---

## 4. API Definition

```python
def submit(
    self,
    message: str,
    *,
    evidence_dir: Optional[Path] = None,
) -> SubmitReceipt
```

* `submit()` は **blocking submission API**
* 完了条件は「送信受理」まで
* 回答取得は含まれない

---

## 5. SubmitReceipt Definition（重要）

```python
class SubmitReceipt:
    submit_id: str        # submit() 呼び出し単位の UUID（必須）
    sent_at: datetime     # UI 受理確認時刻
    ui_ack: bool          # UI 側で送信が受理されたか
    diagnostics: dict     # UI 観測情報・補助メタデータ
```

### Design Rules

* `submit_id` は **必ず ChatPage.submit 内で生成**
* `submit_id` は probe 側との **一次相関キー**
* message_id / conversation_id は **probe 側で補完**する

---

## 6. UI Acknowledgement Model（送信受理モデル）

### 6.1 成功条件（最小確認）

送信は、以下が **すべて成立した場合のみ成功**とみなす：

1. 送信操作が UI 例外なく完了する
2. 送信後、入力欄の value が空になる

この方式を採用する理由：

* DOM 構造依存を最小化できる
* XHR / GraphQL 実装変更に比較的強い
* v0.7 DOM 実証実装で一次情報として確認済み

---

## 7. Failure Model（失敗定義）

### 7.1 submit() が例外を投げる条件

* 入力欄が存在しない
* 送信ボタンが操作不能
* ページが破棄・遷移した
* 一定時間内に UI 受理兆候（入力欄クリア）が観測できない

### 7.2 明示的に失敗としないもの

* 回答が返らない
* 回答生成が遅い
* GraphQL createData が発火しない
* REST `/messages` にまだ反映されていない

---

## 8. Relation to Other Design Documents

### 8.1 Design_ChatPage_v0.5 との関係

* v0.5 の `ask()` は **DOM ベースの legacy / 観測用 API**
* 本書は **送信意味論のみを規定**
* 両者は **併存可能**であり、役割は直交する

---

### 8.2 ChatPage v0.7 実装との関係

* v0.7 は DOM 実証・デバッグ用実装
* submit v0.6 の正式 API ではない
* 実装知見は v0.6 設計の根拠として参照される

---

## 9. Migration Policy（移行方針）

* 既存の DOM-based `ask()` は当面維持
* 本番 E2E / CI / 長期運用では：

  * `ChatPage.submit v0.6`
  * `Answer Detection Layer v0.2+`
    を組み合わせる

---

## 10. Design Rationale（設計判断の根拠）

* UI レイヤは意味的完了点を保証できない
* 完了検知は **観測専用レイヤ**に集約すべき
* 送信 API は安定している必要がある
* 責務分離は将来の保守コストを最小化する

---

## 11. Out of Scope（非拘束）

* 非同期 submit API
* 再送制御・リトライ戦略
* submit_id の外部可視化
* バッチ送信

---

## 12. Summary

**ChatPage.submit v0.6** は、

* 回答を返さない
* 完了を判定しない
* UI 送信の成功のみを保証する

という **極小責務 API**である。

回答の意味論は
**Answer Detection Layer（probe）に完全委譲**される。

---
