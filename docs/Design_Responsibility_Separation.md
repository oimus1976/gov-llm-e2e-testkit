# Design — Responsibility Separation

*(CI / Implementation / Experiment)*

## 目的

本ドキュメントは、本プロジェクトにおける

- CI（可視化・評価）
- 実装（安定動作）
- 実験（検証・試行）

の **責務分離原則**を明文化し、  
一時的な検証や改善が **本番コードを汚染しない**ことを保証する。

---

## 基本原則（要約）

> **実装は安定を、CI は可視化を、実験は一時性を担う。**  
> それぞれの責務を混ぜない。

---

## レイヤ構成

```
[ Experiment Layer ]

* 一時検証
* 条件分岐
* 破棄前提

[ CI / Presentation Layer ]

* 結果の可視化
* 解釈・ラベル付け
* 人間向け出力

[ Implementation Layer ]

* 本番ロジック
* 安定挙動
* 再現性
```

---

## 1. Implementation Layer（実装層）

### 役割

- 安定した動作を提供する
- 観測結果を **事実として記録**する
- 表示・評価・実験判断を行わない

### 対象例

- `probe_v0_2.py`
- PageObject（LoginPage / ChatPage）
- Core test logic

### ルール

- 実験用 if 文を直接入れない
- CI 表示の都合で挙動を変えない
- 一時的な変更は原則禁止

---

## 2. CI / Presentation Layer（CI・表示層）

### 役割

- 実行結果を **人間が誤解なく判断できる形**に整形する
- PASS / WARN / INFO は **表示上の意味付け**のみ

### 対象例

- GitHub Actions workflow
- `$GITHUB_STEP_SUMMARY`
- summary Markdown

### ルール

- ロジックは「解釈」に限定する
- 実装層の挙動を上書きしない
- 表示変更は CI 側で完結させる

---

## 3. Experiment Layer（実験層）

### 役割

- 仮説検証
- 意図的な状態作成（Not Established / No Evidence 等）
- 破棄前提の試行

### 手段

- 環境変数
- CI 条件分岐
- 一時スクリプト

### ルール

- 本番コードに恒久的に残さない
- `git restore` 可能な範囲に留める
- 実験終了後は必ず除去する

---

## 実例（今回のケース）

### ❌ NG

- `probe_v0_2.py` に直接 Not Established を強制するロジックを残す

### ✅ OK

- 環境変数で実験的に挙動を切り替える
- CI summary 側で解釈・表示を行う
- 実装層は元に戻す

---

## 判断に迷ったときのチェック

- [ ] これは安定動作か？
- [ ] それとも表示・解釈か？
- [ ] それとも一時的な検証か？

**2つ以上にまたがるなら、設計が混ざっている。**

---

## 本ドキュメントの位置づけ

- 本書は設計規約であり、実装強制ではない
- ただし、長期的な保守性を優先する判断指針とする
- 新しいパターンが出たら随時追記する

---

*Last updated: v0.1 (initial draft)*
