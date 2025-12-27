# Design_log_writer_v0.1

gov-llm-e2e-testkit — Logging Helper（log_writer.py）設計書

最終更新日: 2025-12-08
バージョン: v0.1

参照文書:

- PROJECT_GRAND_RULES v2.0 
- Startup Template v3.0 
- Startup Workflow v3.0 
- Responsibility_Map_v0.1 
- Design_pytest_env_v0.1 
- Design_logging_v0.1 
- Design_env_v0.1 
- Design_BasePage_v0.1（スクリーンショット仕様） 

---

## 1. 目的（Purpose）

本設計書は gov-llm-e2e-testkit における **テストログ生成ヘルパー `log_writer.py`** の v0.1 仕様を定義する。

log_writer の目的は次のとおり：

1. Design_logging_v0.1 で定義されたログフォーマット（frontmatter + Markdown）を **コードレベルで一貫して生成** できるようにする。
2. pytest Execution Layer / PageObject Layer / Application Test Layer の責務境界を保ったまま、**ログ生成を Application Test Layer に集約**できるようにする。
3. INTERNET / LGWAN / Smoke / Basic / Advanced のすべてで **同一フォーマットのログ** を生成できる共通ライブラリとする。
4. CI（e2e.yml）がログの中身を知らなくても、`logs/` 以下を artifacts として収集するだけで再現性・監査性を確保できる状態を作る。

本 v0.1 は **「最小限の実用的ヘルパー」** として実装し、v0.2 以降で JSON 併産などを拡張する。

---

## 2. 背景・位置づけ（Background & Positioning）

### 2.1 レイヤ構造との関係

Responsibility Map v0.1 によると、本プロジェクトは以下の 4 層構造を持つ。

1. Environment Layer（env.yaml / env_loader）
2. Execution Layer（pytest / conftest / browser/context/page）
3. PageObject Layer（BasePage / LoginPage / ChatPage）
4. Application Test Layer（Smoke / Basic RAG / Advanced RAG）

Design_logging_v0.1 では、ログの具体フォーマットとディレクトリ構成が定義されているが、**どのレイヤがログを生成するか** は実装設計が必要だった。

本設計では：

- **log_writer.py = Application Test Layer の共通ユーティリティ**
- Execution Layer（pytest）は log_writer の利用を支援する fixture と log_dir の準備に限定
- PageObject Layer は、スクリーンショットや DOM 保存など **“素材” の作成のみ** を担当し、ログ組み立ては行わない

という責務分担を正式に定める。

### 2.2 env.yaml / pytest との整合

Design_env_v0.1 において、ログディレクトリは `options.log_dir` として予約されている。

```yaml
options:
  retry_policy: 0
  log_dir: "logs"
```

Design_pytest_env_v0.1 により、pytest（Execution Layer）は env_loader から env.yaml を読み込み、テスト実行に必要な環境設定を提供する。

本設計では、pytest 側で `log_base_dir` を解決し、Application Test Layer に渡すことで、**ログディレクトリのルート管理は pytest / env.yaml 側、ログファイルの生成は log_writer 側**という分担を取る。

---

## 3. 要求仕様（Requirements）

### 3.1 機能要件（Functional Requirements）

1. **frontmatter 付き Markdown ログの生成**

   - Design_logging_v0.1 で定義された frontmatter（`case_id`, `test_type`, `environment` 等）を YAML 形式で出力する。
   - frontmatter の直後に固定セクション構造（Summary / Input / Output / Expected / Result / Details / Artifacts / Metadata）を出力する。

2. **テストタイプ別の差分表現**

   - `test_type` が `smoke` の場合：

     - 基本的には `Summary`, `Input`, `Output`, `Result`, `Artifacts`, `Metadata` を出力。
   - `basic` の場合：

     - `Expected` セクションに keywords / must_not 等を含める。
   - `advanced` の場合：

     - `Details` セクションを含め、詳細な判定ロジック説明を記録できるようにする。

3. **ディレクトリ構成の自動生成**

   - `logs/YYYYMMDD/` 直下に `case_id.md` を作成する。
   - `logs/assets/YYYYMMDD/{case_id}/` 直下にスクリーンショットや DOM ファイルを保存することを想定し、パスを返却する。

4. **環境情報／タイムアウト情報の記録**

   - env.yaml から解決された `env_profile`（例: internet / lgwan）と、
     `browser_timeout_ms`, `page_timeout_ms` を frontmatter に埋め込む。

5. **Metadata 拡張の余地**

   - `metadata` セクションにはブラウザ種別など柔軟な key-value を追加できるようにする（例: `browser: chromium`, `exec_time_ms` など）。

6. **文字コード / 改行**

   - 文字コード: UTF-8
   - 改行コード: LF（GitHub / LGWAN 両対応）

### 3.2 非機能要件（Non-Functional Requirements）

1. **GRAND_RULES 準拠**

   - 設計書 → 実装 → テスト → CI の順で更新する。
   - 仕様変更時は PROJECT_STATUS / CHANGELOG を更新する。

2. **レイヤ境界の尊重**

   - log_writer は **ブラウザ操作や UI ロケータに依存しない**。
   - pytest / PageObject / CI への逆依存を持たない（log_writer は純粋なユーティリティ）。

3. **テスト件数 0 問題への影響なし**

   - log_writer 導入により pytest のテスト検出数が変化しないこと（CIの exit code 5 回避要件を妨げないこと）。

4. **INTERNET / LGWAN 両対応**

   - 外部通信を行わず、ファイル操作のみで完結する（LGWAN 制約順守）。

---

## 4. 設計仕様（Design Specification）

### 4.1 配置とモジュール構成

- 物理ファイル: `src/log_writer.py`
- テスト層からの利用を想定した **シンプルな関数 API** を提供する。

```text
src/
  log_writer.py      ← 本設計の対象
  env_loader.py
tests/
  conftest.py
  test_smoke_llm.py
  rag/
    test_rag_basic_v0.1.py
    test_rag_advanced_v0.1.py
logs/
  （実行時に生成）
```

### 4.2 データモデル

#### 4.2.1 テスト種別（TestType）

```python
TestType = Literal["smoke", "basic", "advanced"]
```

#### 4.2.2 判定結果（TestStatus）

```python
TestStatus = Literal["PASS", "FAIL"]
```

#### 4.2.3 ログコンテキスト（LogContext）

pytest / Application Test から log_writer に渡されるコンテキスト情報の論理モデル：

```python
@dataclass
class LogContext:
    case_id: str
    test_type: TestType
    environment: str          # "internet" / "lgwan"
    timestamp: datetime       # 実行時刻（タイムゾーン付き）
    browser_timeout_ms: int
    page_timeout_ms: int
    question: str | None = None
    output_text: str | None = None
    expected_keywords: list[str] | None = None
    must_not_contain: list[str] | None = None
    status: TestStatus | None = None
    missing_keywords: list[str] | None = None
    unexpected_words: list[str] | None = None
    details: str | None = None
    artifacts: dict[str, str] | None = None  # "screenshot" → PATH など
    metadata: dict[str, Any] | None = None
```

※ v0.1 の実装では dataclass を必須化するか、辞書ベースで受け取るかは任意とするが、「論理モデル」としてこの構造を前提にコードを設計する。

### 4.3 公開 API

#### 4.3.1 `ensure_log_dirs(base_log_dir: Path, case_id: str, timestamp: datetime)`

**目的**

- `logs/YYYYMMDD/` と `logs/assets/YYYYMMDD/{case_id}/` を作成し、パスを返す。

**入力**

- `base_log_dir`: env.options.log_dir などから解決された log ルート (`Path("logs")` を想定)
- `case_id`: テストケース ID（例: "RAG_BASIC_001", "SMOKE_001"）
- `timestamp`: 実行時刻（YYYYMMDD 判定用）

**出力**

- `case_log_dir`: `logs/YYYYMMDD/`
- `case_assets_dir`: `logs/assets/YYYYMMDD/{case_id}/`

```python
def ensure_log_dirs(base_log_dir: Path, case_id: str, timestamp: datetime) -> tuple[Path, Path]:
    ...
```

#### 4.3.2 `write_markdown_log(log_dir: Path, context: LogContext) -> Path`

**目的**

- 指定ディレクトリに `case_id.md` を生成し、Design_logging_v0.1 で定義された構造の Markdown ログを書き込む。

**入力**

- `log_dir`: `logs/YYYYMMDD/`
- `context`: ログ内容を表す `LogContext`

**処理概要**

1. `log_path = log_dir / f"{context.case_id}.md"` を決定。
2. `frontmatter` を生成：

   - `case_id`, `test_type`, `environment`, `timestamp`
   - `browser_timeout_ms`, `page_timeout_ms`
3. セクション出力：

   - `## 1. Test Summary`
   - `## 2. Input`（question）
   - `## 3. Output`（` ```text ... ``` `）
   - `## 4. Expected`（basic / advanced のみ）
   - `## 5. Result`（status / missing_keywords / unexpected_words）
   - `## 6. Details`（advanced のみ）
   - `## 7. Artifacts`（artifacts のパス一覧）
   - `## 8. Metadata`（metadata キーの列挙）
4. ファイルへ書き込み。

**出力**

- 実際に生成した `.md` ファイルの `Path` を返す。

```python
def write_markdown_log(log_dir: Path, context: LogContext) -> Path:
    ...
```

#### 4.3.3 `create_case_log(base_log_dir: Path, context: LogContext) -> Path`

**目的**

- 典型ユースケース：1テストケースの終了時に「ディレクトリ生成＋Markdown書き込み」までを一括で行う高レベル API。

**処理概要**

1. `case_log_dir, case_assets_dir = ensure_log_dirs(base_log_dir, context.case_id, context.timestamp)`
2. 必要なら `context.artifacts` に `case_assets_dir` を前提としたパスを設定する（テストコード側で設定済みを推奨）。
3. `write_markdown_log(case_log_dir, context)` を呼び出す。
4. `Path` を返却。

```python
def create_case_log(base_log_dir: Path, context: LogContext) -> Path:
    ...
```

---

## 5. pytest / PageObject との結合仕様

### 5.1 pytest（Execution Layer）側

Design_pytest_env_v0.1 に準拠し、env_loader から env 設定を読み込む。

```python
# conftest.py（概念レベル）

@pytest.fixture(scope="session")
def env_config():
    config, options = load_env()
    return config, options

@pytest.fixture(scope="session")
def log_base_dir(env_config):
    config, options = env_config
    return Path(options.get("log_dir", "logs"))
```

各テスト（Smoke / Basic / Advanced）は `log_base_dir` と env_config に含まれる `browser_timeout_ms` / `page_timeout_ms` / `env_profile` を使って `LogContext` を構築し、`create_case_log()` を呼び出す。

### 5.2 PageObject（BasePage）側

PageObject Layer はログの「生成」ではなく「素材提供」のみを行う（スクリーンショットなど）。

Design_BasePage_v0.1 における `screenshot` メソッドを、以下のように呼び出すことを想定。

```python
# BasePage 側（v0.1.1 で path 渡しを許容する方向）

async def screenshot(self, path: str | Path):
    await self.page.screenshot(path=str(path))
```

Application Test Layer は、`ensure_log_dirs()` で得た `case_assets_dir` を使ってパスを決定し、PageObject の `screenshot` を呼ぶ。

---

## 6. テストケースからの利用例（擬似コード）

### 6.1 Smoke Test（test_smoke_llm.py）

```python
async def test_smoke_llm(chat_page, env_config, log_base_dir):
    config, options = env_config
    now = datetime.now(timezone(timedelta(hours=9)))

    # 1. 実行
    question = "こんにちは"
    answer = await chat_page.ask(question)

    # 2. 判定
    status = "PASS" if isinstance(answer, str) and answer.strip() else "FAIL"

    # 3. LogContext 構築
    context = LogContext(
        case_id="SMOKE_001",
        test_type="smoke",
        environment=config.get("profile_name", "internet"),  # 実装側で決める
        timestamp=now,
        browser_timeout_ms=config["browser"]["browser_timeout_ms"],
        page_timeout_ms=config["browser"]["page_timeout_ms"],
        question=question,
        output_text=answer,
        status=status,
        metadata={"browser": "chromium"},
    )

    # 4. ログ生成
    create_case_log(log_base_dir, context)
```

### 6.2 Basic RAG Test

Basic / Advanced では `expected_keywords` / `must_not_contain` / `missing_keywords` / `unexpected_words` などを `LogContext` に含める。

---

## 7. 例外・エラー処理（Exceptions）

1. **ディレクトリ作成失敗**

   - OS エラーなどでログディレクトリ生成に失敗した場合、`OSError` をそのまま raise。
   - pytest 側で捕捉してテスト FAIL として扱う方針（v0.1 時点）。

2. **必須フィールド不足**

   - `case_id` / `test_type` / `environment` / `timestamp` が未設定の場合は `ValueError` を発生させる。
   - それ以外のフィールドは `None` を許容。

3. **型不整合**

   - 型ヒントに反する値が渡された場合の挙動は v0.1 では未定義（Python 側の静的解析に依存）。
   - v0.2 でバリデーション強化を検討。

---

## 8. テスト項目（Test Items）

v0.1 では単体テスト（pytest）を想定する。

1. `ensure_log_dirs()`

   - `base_log_dir="logs"`、`case_id="RAG_BASIC_001"`、任意の timestamp を与えたとき、

     - `logs/YYYYMMDD/` が作成される
     - `logs/assets/YYYYMMDD/RAG_BASIC_001/` が作成される

2. `write_markdown_log()`

   - `LogContext` を渡したとき、

     - 指定パスに `.md` ファイルが生成される
     - frontmatter に `case_id`, `test_type`, `environment` が含まれる
     - `## 1. Test Summary` 等のセクションが順番どおりに出力される

3. `create_case_log()`

   - 上記 1 + 2 の複合（ディレクトリ生成＋Markdown生成）

4. Smoke / Basic / Advanced の差分

   - `test_type="smoke"` → `Expected` / `Details` セクションが空 or スキップ
   - `test_type="basic"` → `Expected` は出るが `Details` は任意
   - `test_type="advanced"` → `Details` が出力される

---

## 9. 今後の拡張（Future Work）

v0.2 以降で検討する拡張：

1. JSON ログの併産（機械解析用）
2. 差分ハイライトの自動生成（応答テキスト vs 期待テキスト）
3. Obsidian / Doccano / DataLake 等への流し込みを見据えたメタデータ拡張
4. LGWAN でのログ持ち出しポリシーとの連動（黒塗りオプションなど）

---

## 10. まとめ

- log_writer.v0.1 は、Design_logging_v0.1 の仕様を **Application Test Layer から一貫して使用できるヘルパー** として設計した。
- pytest / PageObject / CI それぞれの責務を尊重しつつ、ログ生成を 1 箇所に集約することで、長期運用性と保守性を確保する。
- 本設計に基づき、次ステップとして `src/log_writer.py` の実装および簡易単体テストを作成し、PROJECT_STATUS / CHANGELOG を更新する。

---

