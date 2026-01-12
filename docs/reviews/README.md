---
title: Review Operations Guide
version: v0.1
status: active
category: operations
scope: Qommons.AI Test Automation
related:
  - docs/templates/reviews/Review_Template_v0.1.md
  - docs/protocol/Prompt_Codex_Review_Generation_v0.1.md
  - Protocol_Web_VSCode_Roundtrip_v1.1.md
  - PROJECT_STATUS.md
  - CHANGELOG.md
---

## 1. このディレクトリの目的

`docs/reviews/` は、  
**実装結果そのものではなく、実装に対する「判断と根拠」を残すための場所**である。

ここに保存されるレビュー文書は、以下を目的とする。

- なぜこの変更を「OK」と判断したのかを後から追えるようにする
- Codex の自己申告（一次情報）と、人間の裁定を分離して記録する
- 設計として固定した判断と、保留した判断を明確に区別する

**コードの正しさを保証する場所ではない。  
保証対象は「判断の履歴」である。**

---

## 2. レビュー文書の位置づけ

- レビュー文書は **成果物（artifact）** である
- チャットログは成果物ではない
- レビュー文書が存在しない判断は、原則として「非固定」とみなす

---

## 3. レビュー文書を作成する条件（必須）

以下のいずれかに該当する場合、**レビュー文書を必ず作成する**。

### 3.1 設計・Protocol・運用ルールに影響する変更

- Protocol の解釈が関わる変更
- pytest 実行条件・責務境界に関わる変更
- 「今後もこの挙動でいく」と判断する必要がある変更

### 3.2 Codex の判断を採用・却下する必要がある場合

- Codex が設計判断めいた決定を含んでいる
- Web 側で「OK / NG / 条件付きOK」を明示した場合

### 3.3 挙動が一見すると自明でない場合

- UI 状態遷移
- timeout / retry / wait 条件
- 例外処理・フォールバック
- テストが「通った理由」を説明しないと不安な場合

---

## 4. レビューを省略できる条件（例外）

以下の場合、**レビュー文書を省略してよい**。

- typo 修正
- コメント修正
- 明らかな dead code 削除
- 設計・挙動に一切影響しない機械的変更

ただし、省略した場合でも：

- PROJECT_STATUS / CHANGELOG 更新が必要かは別途判断する
- 迷ったら **省略しない** を原則とする

---

## 5. レビュー文書の作成手順

### 5.1 テンプレートの使用（必須）

- テンプレートは以下を正本とする

```text
docs/templates/reviews/Review_Template_v0.1.md
```

- テンプレートを **直接編集してはならない**
- 必ずコピーして、新しいレビュー文書を作成する

### 5.2 Codex による生成

- Codex には以下のプロンプトを使用する

```text
docs/protocol/Prompt_Codex_Review_Generation_v0.1.md
```

- Codex は：
- テンプレ構造を厳密に保持する
- 事実情報のみを Section 3 に記載する
- 不明な点は "UNKNOWN" と明示する

### 5.3 Web による裁定

- Reviewer 判断・Web 裁定（Section 6–7）は Web 側で記載する
- Codex が推測で記載した内容は採用しない
- 裁定後、この文書が「判断の正本」となる

---

## 6. ファイル命名規則

```text
Review_<YYYYMMDD>_<context>.md
```

例：

- `Review_20260112_submit_timeout.md`
- `Review_20260115_protocol_pytest_rule.md`

---

## 7. git 運用ルール

- レビュー文書は必ず Git 管理する
- 保存後は以下を必ず実施する

```bash
git add docs/reviews/Review_YYYYMMDD_<context>.md
git commit -m "review: document decision for <context>"
git push
```

- 判断が設計や運用に影響する場合：

  - PROJECT_STATUS.md
  - CHANGELOG.md
    の更新要否を必ず検討する

---

## 8. 注意事項

- レビュー文書は「万能」ではない
- 後から見たときに：

  - 判断根拠が追える
  - 保留点が分かる
  - 再レビュー条件が分かる
    ことを重視する

**「とりあえずOKにした」判断を、
後で自分が説明できる状態にしておくための仕組みである。**

---

## 9. 改訂ルール

- 現行バージョンは **v0.1**
- 運用で破綻が確認された場合のみ改訂する
- 改訂時は：
  - バージョンを更新する
  - CHANGELOG に理由を記載する

---
