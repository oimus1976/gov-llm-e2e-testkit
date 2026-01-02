---
version: F10-A
status: confirmed
role: interface_application
based_on: Design_interface_qommons_reiki_v0.1r+
location: docs/design/core/
---

# Design Interface Application for F10-A

## (gov-llm → reiki-rag-converter)

## 1. 本文書の位置づけ

本書は、  
**「成果物インターフェース定義 v0.1r+」に対する  
Qommons.AI テスト自動化プロジェクト側の  
F10-A フェーズにおける適用内容・確認事項をまとめた返答文書**である。

- インターフェース定義そのものを変更しない
- 新たな契約条件を追加しない
- F10-A における **具体的な成果物構成と運用解釈を明示**する

本書は **設計正本ではなく、適用・合意の記録**である。

---

## 2. 適用対象インターフェース

- 対象文書：成果物インターフェース定義 v0.1r+
- status：FIX
- scope：
  - from: Qommons.AI test automation project
  - to: reiki-rag-converter project

本書は、上記インターフェース定義の  
**原則・責務境界・禁止事項・品質要件をすべて前提条件として受け入れる**。

---

## 3. F10-A 成果物の実体構成

### 3.1 出力ディレクトリ（実行単位）

```text
out/
└─ <run_id>/            # 例: 20260102_1530_golden10x18
├─ answer/
│  ├─ <ordinance_id>/
│  │   └─ answer.md
│  └─ ...
├─ execution_meta.yaml
└─ README.md
```

- `<run_id>` は  
  `timestamp + short label` により一意に識別される
- 同一条件で再実行した場合は、run_id を分けて保存する

---

## 4. answer.md の性質と構造

### 4.1 性質

- Qommons.AI UI に表示された内容を **改変せず記録**した一次観測データ
- 正誤・良否・優劣・改善示唆などの **評価・解釈を一切含まない**
- 評価・判断は **reiki-rag-converter 側の責務**とする

### 4.2 構造（質問単位）

```md
## Question
（質問原文そのまま）

## Answer (Raw)
（Qommons.AI UI に表示された回答全文）

## Citations (As Displayed)
（UI 表示準拠。存在しない場合も必ずセクションを出力し、空で記録）
````

---

## 5. execution_meta.yaml の役割

`execution_meta.yaml` は、
**個々の answer.md に共通する実行条件を横断的に記録する補助メタ情報**である。

記録内容：

- 実行日
- 使用 question.csv のパス
- 使用 Golden Ordinance Set（v1.0）
- 実行アカウント識別子
- 「評価を行っていない」旨の宣言

※ 本ファイルは評価・Gate 判定の根拠として用いない。

---

## 6. README.md の役割

README.md には以下のみを明記する。

- 本成果物は **内容評価を行っていない一次観測データ**であること
- 評価・判断・Gate は **reiki-rag-converter 側で行われる**こと
- 本成果物が **引き渡し用データセット**であること

---

## 7. インターフェース定義との適合確認

F10-A 成果物は、
成果物インターフェース定義 v0.1r+ における以下の要件を満たす。

- 評価・解釈・判定を一切含まない
- 回答・引用が UI 表示と一致している
- 実行条件が再現可能な粒度で記録されている
- reiki-rag-converter 側が独自基準で判断可能な情報が欠落していない

---

## 8. 最終確認サマリー

> 本 F10-A 成果物は、
> 成果物インターフェース定義 v0.1r+ に適合した
> 評価前の一次観測データであり、
> 設計判断および Gate 判定は
> reiki-rag-converter 側で安全に実施可能である。

---
