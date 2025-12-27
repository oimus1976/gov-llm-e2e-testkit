---
title: Golden_Ordinance_Set
project: gov-llm-e2e-testkit
asset_type: Golden Ordinance Set
version: v1.0
status: Frozen (Intellectual Property)
date: 2025-12-14
---

# Golden Ordinance Set（v1.0）

## 1. Purpose（位置づけ）

本ドキュメントは、
Qommons.AI / RAG / convert / validate / CI に共通して使用される
**対象条例10本を知的資産（Golden Ordinance Set）として固定・保管**する。

本セットは、
- RAG評価
- HTML→Markdown変換検証
- 構造異常耐性テスト
- 将来CIの基準入力

における **不変の基準集合**である。

---

## 2. Ordinance List（正式採用10本）

| # | 条例ID | 主な構造特徴 | 主目的 |
|---|---|---|---|
| 1 | k518RG00000059 | 単条・附則なし | 基準ライン |
| 2 | k518RG00000064 | 小規模・標準構造 | 基本RAG評価 |
| 3 | k518RG00000071 | 中規模・項あり | 階層参照精度 |
| 4 | k518RG00001144 | 大規模・項＋号多数 | 深階層検索 |
| 5 | k518RG00000092 | 欠番 | 構造異常耐性 |
| 6 | k518RG00000119 | 逆順 | 条番号混乱耐性 |
| 7 | k518RG00000400 | 附則大量 | 附則検索・時系列 |
| 8 | k518RG00000077 | 附則に条構造 | 階層混在 |
| 9 | k518RG00000097 | 表（colspan/rowspan） | convert_v2.8中核 |
|10 | k518RG00000022 | DOM複雑構造 | HTML崩壊耐性 |

---

## 3. Usage Policy（利用方針）

- 本セットは **削除・差替えを行わない**
- 新規条例追加は **別セット（v1.1+）として定義**
- 各フェーズ（F4 / v0.2 / CI）は
  **本セットから必要最小限を抽出して使用**

---

## 4. Relation to Question Sets

- 質問セットA / B / C は
  本 Golden Ordinance Set を **共通母集団**として利用する
- 本セット自体は質問内容に依存しない

---

## 5. Freeze Declaration（凍結宣言）

本条例セットは
**Golden Ordinance Set として凍結される。**

- 評価基準の揺れを防ぐ
- 再現性・比較可能性を担保する
- プロジェクト全体の基盤資産として保持する
