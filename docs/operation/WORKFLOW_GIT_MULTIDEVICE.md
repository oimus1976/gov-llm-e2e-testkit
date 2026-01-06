---
title: 複数端末 Git 運用ルール（One Pager）
project: gov-llm-e2e-testkit
scope: multi-device git operation
version: v1.0
status: active
last_updated: 2026-01-XX
author: project owner
---

# 複数端末 Git 運用ルール（One Pager）

## 目的
複数端末（自宅PC・職場PC 等）で同一リポジトリを扱う際に、
**履歴破壊・作業消失・世界線分岐事故を防止**する。

本ルールは  
**「迷ったらこれを見る」最低限ルール集**である。

---

## 基本原則（最重要）

### 原則1：main は正本
- **main は常に正本**
- main への `force push` は **原則禁止**
- 例外は「履歴を書き換えることが合意された作業」のみ

---

### 原則2：複数端末＝必ず fetch から
別端末で作業を始めるときは、**最初に必ずこれ**。

```bash
git fetch origin
git status
git log --oneline -5
````

👉
「今、自分がどの世界線にいるか」を確認してから触る。

---

### 原則3：実行端末を分ける

* **実行・検証・本番 run**：原則 1 台に固定
* **設計・整理・ブリーフ作成**：どの端末でも可

生成物が出る作業を複数端末でやらない。

---

## ブランチ運用ルール

### ブランチ種別

| 種別           | 用途    | force push |
| ------------ | ----- | ---------- |
| main         | 正本    | ❌ 禁止       |
| rescue/*     | 退避・救出 | ⭕ 可        |
| wip/*        | 作業途中  | ⭕ 可        |
| experiment/* | 実験    | ⭕ 可        |

---

### 家PCで作業する場合（推奨）

```bash
git checkout -b wip/home-YYYYMMDD
```

* main を直接触らない
* 後で職場PCで merge / cherry-pick する

---

## 危険操作の扱い

### やってはいけない（確認なし）

* `git pull`（特に履歴が怪しいとき）
* `git reset --hard origin/main`
* main への `force push`

---

### 「まずいかも」と思った瞬間の対処（最重要）

```bash
git checkout -b rescue-YYYYMMDD
git push origin rescue-YYYYMMDD
```

👉
**考える前に履歴を GitHub に退避**する。

---

## 本番作業前チェック（30秒）

```bash
git status
git branch
git log --oneline -5
```

* ブランチは想定どおりか
* origin/main と一致しているか
* 直前のコミットは何か

---

## 典型的事故パターン（回避用メモ）

* force push 後に別端末で pull → 履歴分岐
* 家PCで commit したが push せず端末移動
* どの main が正か分からないまま reset

👉
**すべて rescue ブランチ戦術で回避可能**

---

## 本ルールの位置づけ

* 本ドキュメントは **運用ルール**
* 実装・設計仕様より **優先度が高い**
* 迷ったら「止まって fetch → rescue」

---

## 合言葉

> **「迷ったら fetch、ヤバいと思ったら rescue」**

---
