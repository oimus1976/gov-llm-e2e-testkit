---
title: Spec_F9-C_DOM_Scope_Rules_v0.2
version: v0.2
phase: F9-C
status: Final
last_updated: 2025-12-29
scope: Qommons.AI Chat UI Answer Extraction
---

# Spec_F9-C_DOM_Scope_Rules v0.2

**— F9-C（Extracted 正本化）DOM スコープ規則（確定版）—**

## 0. 本仕様の位置づけ

本仕様は **F9-C（Extracted 正本化）** の成果物として、  
チャット UI から **「回答として提示された DOM スコープ」**を安定的に特定し、  
**UI ノイズを機械的に除去**したうえで、**Raw / Extracted を同一 DOM スコープから生成**するための規則を定義する。

### 0.1 本プロジェクトの非目標（再確認）

- 回答の正誤・品質・意味評価は行わない
- ナレッジ形式（HTML/Markdown）の是非は扱わない（例規HTML変換プロジェクトの責務）

---

## 1. 用語

### 1.1 Answer DOM Scope

UI 上で「回答」として表示された領域に相当する DOM サブツリー（起点ノード＋子孫）を指す。

### 1.2 Answer (Raw)

- **UI 全体ダンプではない**
- **Answer DOM Scope** から取得した
- **HTML 非変換の Raw データ**
- HTML→Markdown 等の意味的変換は一切行わない
- DOM の構造・タグ・順序を保持する（ただし **UI ノイズ除去後**の DOM を対象とする：本仕様 §4）

### 1.3 Answer (Extracted)

- **評価入力の正本**
- **Answer DOM Scope** から取得した
- **HTML 非変換（＝HTML のまま）**
- Raw と同一の起点 DOM スコープ・同一のノイズ除去規則を共有する
- `VALID / INVALID` を必ず持ち、Metadata に明示的に記録する

> 注：Extracted が Raw の DOM サブツリーになるような別スコープ設計は **仕様として禁止**（§3.3）。

---

## 2. 出力ポリシー（Raw / Extracted）

### 2.1 生成の原則

- **Raw / Extracted は同一の Answer DOM Scope を共有する**
- **Raw / Extracted に対して意味的変換は一切行わない（HTML のまま）**
- **UI ノイズ除去は本プロジェクトの責務**として実施する（§4）

### 2.2 出力ルール

- Extracted が `VALID` の場合：Raw 出力は省略可能
- Extracted が `INVALID` の場合：Raw 出力は必須
- Raw 出力は debug profile のみに限定

---

## 3. DOM スコープ規則（スコープ設計）

### 3.1 起点 DOM の選定（Top-level）

「回答カード（message-received）」のうち、**回答として確定した対象**を Answer DOM Scope の起点とする。

- 優先：`div.message-received`（回答カード）
- 推奨：実装は「単一質問実行」で対象 message を特定できる前提（run_single_question 等）

#### 観測された実 DOM 例（一次情報）

```html
<div id="message-item-2" class="message-received last:mb-[30px]">
  ...
  <div>
    <div id="markdown-2" class="markdown">
      ...（回答本文）...
    </div>
  </div>
  ...
</div>
```

### 3.2 回答本文コンテナの特定（Inner scope anchor）

Answer DOM Scope の内部に、回答本文を内包するコンテナが存在する場合、**そのコンテナを「回答本文アンカー」として利用**してよい。

- 優先アンカー（観測済み）：
  - `div.markdown` かつ `id="markdown-N"` 形式（N は整数）
- アンカーが見つからない場合：
  - 起点 DOM（message-received）配下から **本仕様 §4 のノイズ除去**を適用し、残存ノード群を Answer とみなす

> 重要：アンカーの有無により「別スコープ」になるのではなく、**どちらの場合も Answer DOM Scope は同一**であること。
> アンカーは「抽出の便宜上の参照点」であり、Raw/Extracted の差を作る道具にしない。

### 3.3 禁止事項：Extracted を Raw のサブツリーにする設計

- Extracted だけ別のより小さい DOM（例：`div.markdown` のみ）を採用し、  
  Raw はカード全体、というような **スコープ差分の仕様化は禁止**
- 理由：
  - 比較不能・検証不能になりやすい
  - UI 変更耐性が落ちる
  - 実装者が迷う（「どこまでが回答か」を二重定義するため）

---

## 4. UI ノイズ除去規則（機械的ルール）

本仕様の「ノイズ」は、**回答本文の意味評価ではなく**、
「回答カードの UI 構成要素として付随する操作部品・装飾部品」を指す。

### 4.1 除去の原則

- ノイズ除去は **意味判断しない**
- **タグ / role / aria / class** のいずれかで **機械的に列挙**し、該当ノードを除去する
- 除去は「ノード単位」：該当ノードとその子孫を除去対象とする

### 4.2 タグベース除去（確定）

以下のタグは **回答の内容そのものを表す目的ではなく UI 構成要素となりやすい**ため除去する。

- `svg`（アイコン・装飾）
- `button`（操作 UI：コピー、音声、メニュー等）
- `form`（入力 UI）
- `textarea`（入力 UI）
- `nav`（ナビゲーション領域）
- `aside`（補助領域）

> 補足：`svg` は「カードの一部」ではあるが、回答内容として不要であり、
> 吹き出しレイアウト等まで含める議論に発展しやすい。
> 本仕様では **svg を明示的に除去**して線を引く。

### 4.3 role / aria ベース除去（補助・確定）

以下に該当するノードは除去する。

- `role="button"`
- `aria-label` が操作を示すもの（例：`コピー`, `Read text aloud` 等）
  - ※具体列挙は実装側の定数として保持してよい（例：`["コピー", "Read text aloud"]`）

### 4.4 class ベース除去（補助・確定）

以下の目的語が class に含まれる要素は除去する（部分一致可）。

- `copy`（copy UI）
- `audio`（音声 UI）
- `menu`（メニュー UI）
- `sr-only`（スクリーンリーダー補助テキスト：本文ではない）

> 注：class は UI 実装変更で揺れるため、**タグ除去が主**、class/aria/role は補助とする。
> ただし「実装者が迷わない」ことが目的なので、補助規則も明示する。

---

## 5. 抽出手順（規範アルゴリズム）

### 5.1 入力

- Playwright で取得した DOM（HTML）
- 対象メッセージの起点ノード（message-received）

### 5.2 手順

1. 起点 DOM（Answer DOM Scope）を特定する（§3.1）
2. 起点 DOM 配下に回答本文アンカー（`div.markdown` 等）があれば参照点として取得する（§3.2）
3. Answer DOM Scope（起点 DOM 配下）へ **ノイズ除去（§4）**を適用する
4. ノイズ除去後の DOM を **HTML 非変換**でシリアライズする
5. それを
   - Answer (Raw) として保存（条件付き：§2.2）
   - Answer (Extracted) として保存（常に）
6. Extracted に `VALID / INVALID` を付与し、Metadata に明示する

---

## 6. 検証ケース（観測＋想定）

### 6.1 観測済み：回答本文が `div.markdown` に存在

- 起点：`div.message-received`
- 本文アンカー：`div#markdown-N.markdown`
- ノイズ：`svg`（AI アイコン）、操作 `button`（コピー/音声）など

### 6.2 想定：code block + copy UI が混在

以下のような構造でも、`pre/code` は保持し、`button` は除去される。

#### 想定 DOM 断片（一次情報）

```html
<div id="markdown-99" class="markdown">
  <p>以下は設定例です。</p>
  <pre class="code-block"><code>print("hello")</code></pre>
  <button class="copy-button" aria-label="コピー" role="button">Copy</button>
  <p>このコードを実行してください。</p>
</div>
```

#### 本仕様の判定

- `pre`, `code`, `p`：保持
- `button`：除去（§4.2）
- 生成される Raw / Extracted は **同一スコープ・同一内容**（§2.1）

---

## 7. 互換性と改訂方針

- 本仕様は **観測された DOM 構造**に基づく
- 将来、未観測の UI（例：accordion / details / button化リンク等）が出現した場合は、  
  **観測一次情報（DOM 断片）を根拠に** v0.3 として改訂する
- 「想定だけ」で v0.2 を膨らませない

---

## 8. 付録：実 DOM（観測断片）

### 8.1 AI アイコン svg（除去対象）

```html
<div>
  <svg xmlns="http://www.w3.org/2000/svg" width="30" height="30" ...>
    ...
  </svg>
</div>
```

### 8.2 回答本文アンカー（保持対象）

```html
<div id="markdown-2" class="markdown">
  <p>...</p>
  <h1>...</h1>
  <hr />
  <ul>...</ul>
</div>
```

### 8.3 操作 UI（除去対象：button）

```html
<button type="button" aria-label="Read text aloud">...</button>
<button type="button">コピー</button>
```

---
