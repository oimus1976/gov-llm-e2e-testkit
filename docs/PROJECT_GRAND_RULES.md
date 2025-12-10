# PROJECT_GRAND_RULES v4.0  

gov-llm-e2e-testkit（E2E 自動テスト基盤プロジェクト）統治文書

最終更新：2025-12-10  
本ファイルはプロジェクト階層の **第1層＝統治層（Governance Layer）** を構成し、  
ChatGPT を開発メンバーとして長期運用するための **不変に近い最高ルール（憲法）** である。

参照元：
- PROJECT_GRAND_RULES v3.0
- Debugging_Principles_v0.2
- Design_* 一式（BasePage / LoginPage / ChatPage / env / pytest / logging / ci_e2e）

本 v4.0 は上記を統合し、**デバッグ原則・PageObject 4層構造・CI/env 運用** を正式に組み込む
メジャーアップデートである。

---

## 1. 目的（Purpose）

1. gov-llm-e2e-testkit の設計・実装・検証を  
   **一貫性・透明性・再現性のある形で維持**する。  

2. ChatGPT がプロジェクトの “公式アーキテクト兼レビュワー兼デバッガ” として  
   **正しく・安全に・再現可能に** 振る舞うための行動基準を定める。  

3. OSS プロジェクトとしての **説明可能性・バージョン管理の厳格性・CI 安定性** を保証する。  

4. LGWAN / INTERNET の二重環境でも破綻しない **長期運用基盤** を形成する。  

5. PENTA 方式による多角検討と、Debugging_Principles に基づく  
   **「推測ではなく観察に基づくデバッグ」** を徹底する。  

---

## 2. 基本原則（Core Principles）

### 2.1 設計駆動（Design-Driven Development）

- **「設計書なくして実装なし」** を原則とする。  
- 設計 → 実装 → テスト（ローカル）→ CI → STATUS 更新 → CHANGELOG 追記 の順序は不変。  
- 設計書（Design_*）の変更は必ず理由・影響範囲を PROJECT_STATUS / CHANGELOG に記録する。  
- **PageObject・Locator_Guide・test_plan・env 設計** は常に整合していなければならない。  
- PageObject は基本的に以下の 4 層構造を前提とする：
  - BasePage（共通操作 / ログ・証跡）  
  - LoginPage（ログイン）  
  - ChatSelectPage（チャット一覧からの選択）  
  - ChatPage（チャット画面での入出力）  

### 2.2 品質保証・CI 原則（Quality & CI Principles）

- CI は生命線であり、その破壊（設定削除・ Smoke 無効化・雑な一時対処）は禁止。  
- Smoke Test（`tests/test_smoke_llm.py`）の削除・改名・無効化は禁止。  
- pytest の「テスト件数 0 → exit 5」状態を発生させない構造を維持する。  
  - Smoke は必ず 1 件以上のテストを実行すること。  
- GitHub Actions 上では、少なくとも以下を前提とする：
  - Python 3.10 系  
  - `pytest`, `pytest-asyncio`, `pytest-playwright`, `playwright`, `python-dotenv`, `PyYAML`  
  - `python -m playwright install --with-deps` の実行  
  - `PYTHONPATH` に `src/` を追加して `src.*` import を安定化  
- CI でのテスト実行順序は原則として：
  1. Smoke Test（LLM ログイン ～ 1 メッセージ送受信）  
  2. RAG Basic  
  3. RAG Advanced  
- **CI が赤になった場合は、まずログ・エラーメッセージ・差分を観察し、  
  設定・コード・環境のどこに原因があるかを Debugging_Principles に従って特定する。**  

### 2.3 デバッグ原則（Debugging Principles）※ v4.0 新設

- **Debugging_Principles_v0.2 は本 GRAND_RULES の下位規範として常に有効**。  
- ChatGPT はデバッグやトラブルシュートに関する回答を行う際、  
  暗黙的に Debugging_Principles_v0.2 を参照・遵守するものとする。  

特に以下を必須とする：

1. **観察優先**  
   - まずコード・ログ・DOM・CI ログなど **一次情報を確認** する。  
   - 一次情報を見ずに「多分こうだろう」と結論づけることを禁止。  

2. **仮説は必ず「根拠付き」で提示**  
   - 「こうかもしれない」だけでなく、  
     「この行のこの挙動と、このログのこのメッセージからこう推測できる」  
     という形で説明する。  

3. **修正は再発防止策とセット**  
   - 単にエラーが消えるパッチではなく、  
     「なぜ起きたか」「今後どう防ぐか」「どのテストで守るか」を必ずセットで提示。  

4. **局所最適の禁止**  
   - 一時的に通すためだけの `import 削除` や `assert 削除` は禁止。  
   - 影響範囲を把握し、全体最適（設計・CI・将来の拡張）を優先する。  

5. **検証の義務**  
   - 新しい修正案（特に PageObject / CI / env 周り）を提示する際は、  
     可能な範囲で **「簡易検証スクリプト」「テストの観点」** を提示し、  
     ユーザー側で再現確認しやすいようにする。  

### 2.4 UI識別統一（Locator Consistency）

- すべての UI 操作は `docs/Locator_Guide_v0.2.md` に従う。  
- locator は **PageObject にのみ定義し、テストケースに直接書かない**。  
- XPath と `nth-child` 指定は禁止。  
- Primarily:
  - `get_by_role` / `get_by_label` / 安定した属性（id, name）を優先  
  - `data-testid` の利用は **実 DOM に存在するものに限る**（妄想で作らない）。  
- UI 変動への追従は PageObject のみ修正し、  
  テストケース・設計書・ci_e2e 設計との整合を保つ。  

### 2.5 透明性（Transparency）

- CHANGELOG は必ず更新する。  
- すべての実装・設計変更の理由を説明可能に保つ。  
- PROJECT_STATUS は唯一の「現在地」として常に最新に保つ。  
- 「ChatGPT が提案した修正」がマージされる場合は、  
  その旨を STATUS / CHANGELOG に明示しておくことが望ましい。  

### 2.6 後方互換性（Backward Compatibility）

- バージョンアップは互換性維持を前提とする。  
- Breaking Change は PENTA 審査必須。  
- STATUS に理由・影響範囲・ロールバック方法を明記する。  

### 2.7 LGWAN運用原則（LGWAN Compliance）

- LGWAN 環境では外部通信禁止を前提としたコード生成を行う。  
- ログ持ち出し・スクリーンショットの取り扱いは LGWAN セキュリティポリシーに従う。  
- INTERNET 版と LGWAN 版の設定差異は `env.yaml` と `.env` / OS 環境変数で管理する。  
- LGWAN 固有の URL / 認証情報は GitHub に記載しない。  

### 2.8 単一タスク原則（Single-Action Rule）

- Next Action は **常に 1 つ**。  
- 並列アクションは禁止。  
- PROJECT_STATUS の Next Action は ChatGPT の判断基準の根幹であり、  
  これに反する提案を行わない。  

---

## 3. ファイル構成原則（Directory Principles）

プロジェクトは以下構造に従う：

```text
/docs                 → 設計書・統治文書（Design_*.md, Locator_Guide_*.md, PROJECT_GRAND_RULES.md, Roadmap 等）
/tests                → Playwright / pytest テストコード
  ├─ pages/           → PageObject (BasePage, LoginPage, ChatSelectPage, ChatPage)
  └─ rag/             → RAG 検証用テスト群
/data                 → RAG テストデータ（YAML / JSON）
/sandbox              → 一時的な DOM 取得・検証スクリプト（原則 Git 管理外が望ましいが、必要なものは明示的に管理）
/logs                 → テストログ（Git 管理外）
.github/workflows     → CI 定義
env.yaml              → プロファイル定義（INTERNET / LGWAN / CI など）
pyproject.toml        → パッケージ / 依存定義
requirements.txt      → CI など必要に応じた補助的依存リスト
PROJECT_GRAND_RULES.md
PROJECT_STATUS.md
CHANGELOG.md
README.md
````

---

## 4. ドキュメント規範（Documentation Standard）

### 4.1 基本規範

* h1 はタイトルのみ使用する。
* 設計書は「目的 → 背景 → 要求 → 設計 → 例外 → テスト → 拡張案」のテンプレートに沿う。
* コードブロックには必ず言語指定（`python`, `yaml`, `bash` など）を付与する。
* Markdown の階層構造を適切に保つ。
* 設計書・STATUS・Template に不整合が生じた場合、
  **設計書（Design_*.md）が唯一の“正”として優先される。**

### 4.2 設計書バージョニング標準（Design Document Versioning Policy）

（v3.0 から継承しつつ補足）

1. 設計書（Design_XXX_*）は原則として **バージョン付きファイル形式** で管理する。

   * 例：`Design_BasePage_v0.1.md`, `Design_BasePage_v0.2.md`

2. 過去バージョンは削除せず、**docs ディレクトリ内に全て履歴として保存**する。

3. 最新版のみ参照させたい場合は、固定名の
   **`Design_XXX.md`（latest alias）** を作成し、そこから最新版へ誘導する。

4. 破壊的変更（Breaking Changes）がある場合は、
   **v0.x → v0.(x+1)** の形式でバージョンを increment する。

5. 設計書の更新フローは以下の順序に従う：
   **設計 → 実装 → ローカルテスト → CI → STATUS 更新 → CHANGELOG 追記**

6. 旧版を supersede（置き換え）する場合は、
   **新バージョンの冒頭に supersede を明記**する。

   * 例：`This document supersedes Design_BasePage_v0.2.`

---

## 5. env / Secrets / pytest 環境規範

* 実行環境の設定は **原則 `env.yaml` + .env（dotenv）+ OS 環境変数 + GitHub Secrets** の組み合わせとする。
* `src/env_loader.py` を通さずに個別に環境変数を読む実装は原則禁止。
* `env.yaml` のプレースホルダ `${VAR}` は `env_loader` により解決される。

  * 解決できない場合は MissingSecretError を送出する。
* conftest では MissingSecretError を検知し、CI 用の安全な fallback を適用してもよいが、
  その場合も **理由・挙動をコードコメントと DESIGN / GRAND_RULES に残すこと。**
* pytest の実行は、原則として `python -m pytest` 形式を推奨する。

---

## 6. デバッグ・インシデント対応フロー

バグ・CI エラー・テスト失敗に直面した場合、以下の順序で対応する：

1. **状況の記録**

   * エラーメッセージ・ログ・DOM・スクリーンショットなどを sandbox / logs に保存する。

2. **一次情報の観察**

   * コード / CI ログ / DOM / env.yaml / pytest 設定を確認する。

3. **仮説の整理**

   * 「何が起きているか」「なぜ起きているか」を Debugging_Principles に従って文章化。

4. **最小再現と検証スクリプト**

   * 可能な限り **最小コード** で再現する検証スクリプトを sandbox/ に作る。

5. **修正案の実装**

   * PageObject / env / CI / テストのどれに手を入れるかを明確にし、
     影響範囲を説明した上でパッチを提案する。

6. **再テスト・再発防止**

   * Smoke / 該当テストを再実行し、再発防止策（追加テストやログ）を検討する。

7. **ドキュメント更新**

   * 必要に応じて Design_*, PROJECT_STATUS, CHANGELOG に反映する。

---

## 7. PENTA 運用規範（PENTA Governance）

* PENTA は **複雑・不確実・影響が大きい場合** に使用する。

* 典型的な利用タイミング：

  * GRAND_RULES の MAJOR 更新（今回の v4.0 など）
  * PageObject 構造の大幅変更
  * CI 基盤の見直し（ワークフロー構造を含む）
  * 再発系バグ・設計レベルのデグレが疑われるデバッグ

* 5 脳の役割（例）：

  * アーキテクト / QA / インフラ / ドキュメント / デバッグ監査

* PENTA の結論は、STATUS または設計書・GRAND_RULES に反映する。

* 不必要な PENTA の乱用を避け、**「ここぞ」というポイントに集中して使う。**

---

## 8. 更新ポリシー（Update Policy）

* PROJECT_GRAND_RULES の変更は慎重に行う。
* MAJOR 更新（v3 → v4 など）は、以下のいずれかがある場合に行う：

  * デバッグ原則の大幅改訂
  * PageObject / CI / env など基盤アーキテクチャの変更
  * テスト戦略の根本的な見直し
* 更新前には PENTA レビューを行うことが望ましい。
* 変更は必ず CHANGELOG に記録する。

---

## 9. 本文書の位置づけ

本ファイルはプロジェクトの最上位レイヤ（統治層）であり、
Startup Template（第2層）と Startup Workflow（第2.5層）、STATUS（第3層）に **優先する**。

---

以上を **gov-llm-e2e-testkit の PROJECT_GRAND_RULES v4.0（正式版案）** とする。
