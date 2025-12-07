# 📄 **Locator_Guide_v0.2 — gov-llm-e2e-testkit**

最終更新: 2025-12-07  
バージョン: v0.2  
対象: gov-llm-e2e-testkit  
目的: UI 要素を Playwright から安定識別するための強化版ガイド

---

## 1. 本ガイドの目的

gov-llm-e2e-testkit では、UI の変化に強いロケータ設計が
**テスト成功率・長期運用性・CI安全性の中心的要素**になる。

v0.2 では、v0.1 を基礎にしつつ以下を強化する：

- name（文言）が変更された場合の fallback 戦略
- LGWAN の遅延を考慮した待ちパターンの明確化
- テキストベース識別の“最終手段化”
- aria-label / title の活用基準
- Page Object との整合性強化

---

## 2. ロケータの優先順位（v0.2 改訂版）

最上位から順に検討し、**下位はあくまで fallback**。

### 2.1 第1位：`get_by_role`（ロール＋name）

```python
page.get_by_role("button", name="送信")
page.get_by_role("textbox", name="質問")
```

#### ★ 長期運用の最強ロケータ

- class や内部 DOM が変わっても動きやすい
- LGWAN / INTERNET 両方で安定
- UI ライブラリの違いを吸収しやすい

---

### 2.2 第2位：ラベル連動型（`get_by_label`, `get_by_placeholder`）

```python
page.get_by_label("質問")
page.get_by_placeholder("キーワードを入力")
```

#### ★ 文言の安定性が高い場面で有効

- フォーム系に強い
- name変化が起きても label/placeholder が残る場合が多い

---

### 2.3 第3位：aria属性（`aria-label`, `title` など）

```python
page.locator("[aria-label='チャット入力']")
page.locator("[title='送信']")
```

#### ★ UI ライブラリ（Material UI、React系）で強力

- 日本語の label 文言が変わっても aria が維持されるケースが多い
- name 変動が予想される UI では必須の fallback

---

### 2.4 第4位：data-testid

```python
page.locator("[data-testid='chat-input']")
```

#### ★ アプリ側に付けられるなら最強クラス

- テスト専用で意味が変わらない
- i18n 影響なし
- LGWAN でも安定

---

### 2.5 第5位：CSS セレクタ（最小限）

```python
page.locator("input[name='question']")
```

利用許容条件：

- role / aria / label が存在しない
- id / name / stable-class のみ使用可
- nth-child や div の連鎖は不可

---

### 2.6 最終手段（fallback）：テキストベース（`has_text` / `get_by_text`）

**“Page Object 内でのみ許可”。テストケースで使うのは禁止。**

```python
page.get_by_role("button").filter(has_text="送")
```

**理由：**

- 日本語 UI では文言変更が多い
- モデルアップデートで wording が変わる
- 過剰マッチの危険がある

---

## 3. 文言変化に備えた fallback 戦略（v0.2 追加）

以下の複合ロケータを推奨：

### ✔ ロール + 部分一致

```python
page.get_by_role("button").filter(has_text=re.compile("送|投稿"))
```

### ✔ ロール + aria-label

```python
page.get_by_role("button", name=re.compile("送|投稿"))

page.locator("[aria-label='send']")
```

### ✔ ロール + placeholder（入力欄）

```python
page.get_by_role("textbox").filter(
    has=page.get_by_placeholder("質問")
)
```

→ **単独で弱いロケータは“組み合わせ”で強化する。**

---

## 4. Page Object におけるロケータ設計ルール

### 4.1 Locator は必ず Page Object に集約

```python
class ChatPage(BasePage):
    @property
    def input_box(self):
        return self.page.get_by_role("textbox", name="質問")

    @property
    def send_button(self):
        return self.page.get_by_role("button", name=re.compile("送|投稿"))
```

### 4.2 テストケースにロケータを絶対に書かない

- テストコードは **動作の呼び出しだけ**
- UI変更時は Page Object のみ修正すれば済む

### 4.3 文言バッファ運用（v0.2 追加）

UI 文言が頻繁に変わる場合：

```python
SEND_LABELS = ["送信", "送る", "投稿"]

def send_button(self):
    return self.page.get_by_role("button").filter(
        has_text=re.compile("|".join(SEND_LABELS))
    )
```

---

## 5. LGWAN 環境での特別ルール（v0.2 強化）

### ✔ デフォルトタイムアウト（INTERNET）

- 10,000 ms

### ✔ LGWAN 推奨

- 20,000〜30,000 ms
  （UIのロード遅延を想定）

### ✔ 関連記述を Playwright config にも反映

例：`config/env.yaml`

```yaml
timeout:
  internet: 10000
  lgwan: 30000
```

---

## 6. 禁止パターン（再掲＋強化）

- XPath
- nth-child, nth-of-type
- 動的 class
- div 連鎖（`div > div > span:nth-child(3)`）
- テストコードにロケータを書く
- 完全一致の get_by_text（破壊的リスク大）

---

## 7. 本ガイドの更新手順

1. UI変更を検出
2. PENTA で影響分析
3. 本ガイド更新
4. PROJECT_STATUS に影響範囲を記録
5. Design_playwright_v0.1 と整合性確認（必要なら改訂）

---

## 8. v0.3 以降の展望

- data-testid 命名規則
- Qommons UI（Material系）を踏まえた高度なロケータ例
- バックアップロケータ（multi-locator）の標準化
- Chat 状態の変化検知方式（loading, thinking 表示の検知）

---

## 9. まとめ

- v0.2 は「長期運用に耐えるロケータ設計」の最低ラインを満たす
- Page Object と連動することで、Smoke Test 〜 Advanced RAG まで安定して動作可能
- LGWAN を含む複数環境での実行を意識した強化版

---
