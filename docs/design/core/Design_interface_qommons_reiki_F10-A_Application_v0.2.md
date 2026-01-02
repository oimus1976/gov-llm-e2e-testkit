---
version: v0.2
status: confirmed
role: interface_application
based_on: Design_interface_qommons_reiki_v0.1r+
supersedes: Design_interface_qommons_reiki_F10-A_Application (v0.1)
location: docs/design/core/
---

# Design Interface Application for F10-A

## (Test Automation → reiki-rag-converter)

## 1. 本文書の位置づけ

本書は、  
**成果物インターフェース定義 v0.1r+** に対する  
テスト自動化プロジェクト側の **F10-A フェーズにおける適用内容**を  
合意事項として明文化した返答文書である。

- インターフェース定義そのものは変更しない
- 契約条件を追加・拡張しない
- F10-A における成果物構成および運用上の解釈を確定する

本書は **設計正本ではなく、適用・合意の記録**である。

---

## 2. 適用対象インターフェース

- 成果物インターフェース定義：v0.1r+
- status：FIX

本書は、同定義に記載された  
原則・責務境界・禁止事項・品質要件をすべて前提として受け入れる。

---

## 3. F10-A 成果物の実体構成

### 3.1 出力ディレクトリ（実行単位）

```text
out/
└─ <run_id>/                      # 例: 20260102_1530_golden10x18
├─ answer/
│  ├─ <ordinance_id>/
│  │   └─ answer.md
│  └─ ...
├─ manifest.yaml
├─ execution_meta.yaml
└─ README.md
````

- `<run_id>` は `timestamp + short label` により一意に識別される
- 同一条件で再実行した場合は、run_id を分けて保存する

---

## 4. answer.md の性質と構造（正本）

### 4.1 性質

- Qommons.AI UI に表示された内容を **改変せず記録**した一次観測データ
- 正誤・良否・優劣・改善示唆などの **評価・解釈を一切含まない**
- **本成果物群における正本は各 answer.md** である

### 4.2 構造（質問単位）

```md
## Question
（質問原文）

## Answer (Raw)
（UI 表示そのままの回答全文）

## Citations (As Displayed)
（UI 表示準拠。存在しない場合も必ず空セクションを出力）
````

---

## 5. manifest.yaml（補助索引）

### 5.1 位置づけ

manifest.yaml は、
複数の answer.md を **機械可読に束ねるための補助的な索引**であり、
**正本ではない**。

- 評価・解釈・判定を一切含まない
- answer.md の内容を再構成・要約・加工しない

### 5.2 スキーマ

```yaml
schema_version: manifest_v0.1
based_on_interface: v0.1r+
kind: manifest

run_id: 20260102_1530_golden10x18
executed_at: 2026-01-02T15:30:00+09:00

sets:
  ordinance_set: Golden_Ordinance_Set_v1.0
  question_pool: Golden_Question_Pool_A_v1.1

entries:
  - ordinance_id: k518RG00000059
    question_id: Q1
    file: answer/k518RG00000059/Q1.md
```

- schema_version は成果物IFとは独立した **manifest_v0.1**
- IF との関係は `based_on_interface` で参照する

---

## 6. execution_meta.yaml の役割

- 実行日
- 使用 question.csv のパス
- 使用 Golden Ordinance Set
- 実行アカウント識別子
- 非評価宣言

※ 評価・Gate 判定の根拠としては使用しない。

---

## 7. README.md の役割

- 本成果物が **評価前の一次観測データ**であること
- 評価・判断は **reiki-rag-converter 側の責務**であること
- 引き渡し用データセットであること

---

## 8. 適合確認サマリー

本 F10-A 成果物は、
成果物インターフェース定義 v0.1r+ に適合しており、
評価・設計判断は reiki-rag-converter 側で安全に実施可能である。

---
