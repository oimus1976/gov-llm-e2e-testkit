# Design_playwright_v0.1

最終更新日: 2025-12-07  
バージョン: v0.1  
対象プロジェクト: gov-llm-e2e-testkit  

---

## 1. 目的・スコープ

本ドキュメントは **自治体向け LLM サービスの E2E 自動テスト基盤（Python + Playwright）** のうち、  
「Playwright 利用設計」を定義する。  
（Qommons.AI を含むが、特定企業を公式に扱うものではない）

- Qommons.AI の UI 変更やモデル更新に対して **壊れにくいテストコード** を設計する
- インターネット環境／LGWAN 環境の両方で運用可能な **抽象化された Playwright アーキテクチャ** を示す
- テストコード作成者間での **記法・責務分担・ディレクトリ構成の共通認識** を提供する

本バージョン (v0.1) は **最小限の実装を開始するための初期設計** であり、  
将来的に v0.2 以降で詳細を拡張する前提とする。

---

## 2. テストレベルと Playwright の役割

本プロジェクトでは以下の 3 レベルのテストを定義する：

1. **Smoke Test**
   - 目的: 「Qommons.AI が起動し、基本的な QA が 1 件でも通るか」の確認
   - Playwright の役割:  
     - ブラウザ起動
     - ログイン／初期画面表示
     - 単一のシンプルな QA 実行
     - エラー時のスクリーンショット取得

2. **Basic RAG Test**
   - 目的: 条例ナレッジに対する基本的な QA 精度を **固定された少数パターン** で検証
   - Playwright の役割:  
     - 複数の質問を順に投げる
     - UI を通じて回答を取得し、テキストとして抽出
     - 期待回答との比較結果をログに出力（合否・差分要約）

3. **Advanced RAG Test**
   - 目的: 複雑なプロンプト・複数ターン対話・例外ケースを含んだ網羅的な検証
   - Playwright の役割:  
     - 複数ターンの対話シナリオを実行
     - 途中でのリトライ・エラー検知・時間制限の管理
     - ログ／スクリーンショット／HTML スナップショットの保存

---

## 3. アーキテクチャ概要

### 3.1 コンポーネント構成

本プロジェクトの Playwright 関連コンポーネントは以下のように構成する。

- **pytest ランナー**
  - テストケースのエントリポイント
  - 共通 fixtures (`browser`, `page`, `qommons_client` など) を提供

- **Playwright fixtures**
  - `browser`: ブラウザインスタンスのライフサイクル管理
  - `page`: テストごとのページインスタンス
  - `qommons_client`: Qommons.AI 特化の操作ヘルパ（後述）

- **Screen / Page Object レイヤ**
  - 画面単位の操作クラス（例: `LoginPage`, `ChatPage`）
  - UI ロケータ・操作手順をカプセル化

- **Config / Environment レイヤ**
  - `config.yaml` 等で URL・タイムアウト・環境種別（INTERNET/LGWAN）を管理
  - Playwright 起動オプション（ヘッドレス/ヘッドフル・ビューポートなど）を切り替え

- **テストデータレイヤ**
  - RAG テスト用の問合せ・期待結果を YAML/JSON で定義
  - テストケースはデータをパラメータとして受け取り、UI を通じて実行する

- **ログ・レポートレイヤ**
  - `logs/YYYYMMDD/ケースID.md` 形式で Markdown ログを保存
  - 必要に応じてスクリーンショット / HTML スナップショットも同ディレクトリに保存

### 3.2 ディレクトリ構成（Playwright 関連）

Startup Template v1.1 に従い、Playwright 関連ファイルは主に以下に配置する：

```text
qommons-ai-auto-test/
  ├── design/
  │     └── Design_qommons_playwright_v0.1.md   # 本書
  ├── tests/
  │     ├── conftest.py                         # 共通 fixtures
  │     ├── pages/                              # Screen/Page Object
  │     │     ├── login_page.py
  │     │     └── chat_page.py
  │     ├── smoke/
  │     │     └── test_smoke_qommons.py
  │     └── rag/
  │           ├── test_rag_basic_*.py
  │           └── test_rag_advanced_*.py
  ├── data/
  │     └── rag/
  │           ├── basic_cases.yaml
  │           └── advanced_cases.yaml
  ├── logs/
  │     └── 20251207/
  └── .github/
        └── workflows/
              └── e2e.yml
````

---

## 4. 環境設計（インターネット / LGWAN）

### 4.1 環境種別

本プロジェクトでは、以下の 2 種類の環境を想定する：

- **INTERNET 環境**

  - 外部インターネットに接続可能
  - CI（GitHub Actions）での自動実行が可能
- **LGWAN 環境**

  - 外部インターネットへの通信は禁止
  *- ommons.AI（LGWAN版）へのアクセスのみ許可
  - ログ・スクリーンショットは LGWAN 内部ストレージに保存

### 4.2 環境設定の切り替えポリシー

環境種別は **設定ファイル＋環境変数の両方** で切替可能とする：

- `config/env.yaml` に環境ごとの基本設定を定義
- `QOMMONS_ENV` 環境変数で `internet` / `lgwan` を指定
- Playwright 起動時に URL・タイムアウト・プロキシ設定を切り替える

### 4.3 LGWAN 制約への対応

- 外部 CDN やオンラインライブラリに依存するコードを生成しない
- Playwright の結果（ログ・スクショ・HTML）は **LGWAN 内部にのみ保存**
- GitHub などへのアップロードは、別途「持ち出しルール」に従う（本設計のスコープ外）

---

## 5. ロケータ設計ポリシー

### 5.1 基本方針

1. **locator ベースの記述を標準とし、XPath は禁止**
2. **`get_by_role` によるロールベース識別を最優先する**
3. `data-testid` 等のテスト専用属性が付与できる場合はそれを活用
4. テキストベース識別は最小限にとどめる（文言変更に弱いため）

### 5.2 推奨ロケータパターン

以下の優先順でロケータを選択する：

1. `page.get_by_role("button", name="送信")`
2. `page.get_by_label("質問")`
3. `page.get_by_placeholder("質問を入力")`
4. `page.locator("[data-testid='qommons-chat-input']")`
5. `page.locator("form >> input[name='question']")`

### 5.3 ロケータ管理

- ロケータは **Page Object 内に集約** し、テストケースからは直接 CSS セレクタ等に触れない
- 同じ UI 要素を複数テストで利用する場合は、必ず共通メソッド化する

```python
# 例: chat_page.py
class ChatPage:
    def __init__(self, page):
        self._page = page

    @property
    def input_box(self):
        return self._page.get_by_role("textbox", name="質問")

    @property
    def send_button(self):
        return self._page.get_by_role("button", name="送信")

    async def send_question(self, text: str):
        await self.input_box.fill(text)
        await self.send_button.click()
```

---

## 6. 待ちパターン・タイムアウト設計

### 6.1 待ちの基本指針

- 「固定スリープ (`time.sleep`)」は禁止
- 必ず Playwright の待ち機能を利用する：

  - `page.wait_for_selector(...)`
  - `locator.wait_for(...)`
  - `expect(locator).to_be_visible()`（pytest-playwright 拡張利用時）

### 6.2 典型パターン

1. **ページ読み込み完了待ち**

   ```python
   await page.goto(base_url)
   await page.wait_for_load_state("networkidle")
   ```

2. **回答の出力完了待ち**

   ```python
   answer_locator = page.get_by_test_id("qommons-answer")
   await answer_locator.wait_for(timeout=30_000)
   ```

3. **トースト／エラーメッセージの検出**

   ```python
   error_toast = page.get_by_role("alert")
   if await error_toast.is_visible():
       # ログ出力や fail を行う
       ...
   ```

### 6.3 タイムアウト設定

- デフォルトタイムアウトは `10〜30秒` を目安とし、環境ごとに `config/env.yaml` で調整可能とする
- 長時間処理が想定されるテストでは、テストケース単位でタイムアウトを延長する

---

## 7. テストデータ設計（YAML/JSON）

### 7.1 スキーマ例（YAML）

```yaml
# data/rag/basic_cases.yaml
cases:
  - id: "RAG_BASIC_001"
    title: "条例の正式名称を問う基本 QA"
    question: "○○町情報公開条例の正式名称を教えてください。"
    expected_keywords:
      - "○○町情報公開条例"
      - "平成"
    must_not_contain:
      - "別の自治体"
      - "仮の名称"
  - id: "RAG_BASIC_002"
    title: "施行年月日の確認"
    question: "○○町情報公開条例の施行日はいつですか？"
    expected_keywords:
      - "施行日"
      - "平成"
```

### 7.2 テストコード側の利用例

```python
import yaml
import pathlib

DATA_PATH = pathlib.Path("data/rag/basic_cases.yaml")

def load_basic_cases():
    with DATA_PATH.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)["cases"]
```

---

## 8. ログ・スクリーンショット設計

### 8.1 ログ保存場所

- `logs/YYYYMMDD/ケースID.md` に Markdown で保存
- 1 テストケース = 1 ファイル を基本単位とする

### 8.2 ログフォーマット（例）

```markdown
# Test Log — RAG_BASIC_001
実行日: 2025-12-07
環境: internet
ブラウザ: chromium

## 1. 概要
タイトル: 条例の正式名称を問う基本 QA
質問: ○○町情報公開条例の正式名称を教えてください。

## 2. 実際の回答
<ここに Qommons.AI の回答全文を貼り付け>

## 3. 判定結果
- 結果: PASS / FAIL
- 検出キーワード:
  - [x] ○○町情報公開条例
  - [x] 平成
- 禁止ワード:
  - [ ] 別の自治体
  - [ ] 仮の名称

## 4. メモ
- 差分や気づきがあれば記録
```

### 8.3 スクリーンショット

- ファイル名: `logs/YYYYMMDD/ケースID.png`
- 失敗時のみ必須取得、成功時は任意（CI でサイズを考慮）

---

## 9. CI (GitHub Actions) における Playwright 利用方針

> 詳細な `e2e.yml` の仕様は別設計書で定義するが、Playwright の観点からの前提のみ記載する。

- GitHub Actions 上で `pytest` + `playwright` を実行する
- `python -m playwright install` を事前に実行
- シークレット（URL・トークン等）は GitHub Secrets で管理し、
  **テストコード内にべた書きしない**
- LGWAN 実行は GitHub Actions とは別枠（手動実行）とし、本設計の CI は **INTERNET 環境用** とする

---

## 10. セキュリティ・プライバシー配慮

- テストコード・ログに **ID/PW/APIキーを記録してはならない**
- ログの中に個人情報や機密情報が含まれる場合は、
  ファイル名・保存先・マスキング方針を別途定める（次バージョンの課題）
- LGWAN 内のログを GitHub 等へ持ち出す場合は、組織の情報セキュリティポリシーに従う

---

## 11. 今後の拡張・課題（v0.2 以降）

- Page Object の標準インターフェース定義（`BasePage` 等）
- ログ自動生成ユーティリティ（Markdown テンプレート／差分ハイライト）
- Advanced RAG Test 用の対話シナリオ DSL 検討
- LGWAN 環境での実行手順書（手動実行・結果転記フロー）の整備
- e2e.yml の詳細設計（並列実行・ジョブ分割・失敗時のアーティファクト収集）

---

## 12. 本設計の位置づけ

本ドキュメントは、以下の文書群と連携して運用される：

- Startup Template v1.1（プロジェクト人格・行動規範）
- PROJECT_STATUS.md（現在地・Next Action 管理）
- test_plan（RAGテストポリシー）
- CI 設計書（e2e.yml の詳細）

Playwright やページ操作に関する**事実上の「唯一の参照元」**として扱い、
変更は必ず PENTA による検討を経て、バージョン番号を更新する。

---
