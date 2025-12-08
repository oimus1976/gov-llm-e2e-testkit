> **Note**  
> 本ドキュメント **Design_BasePage_v0.2.md** は  
> **Design_BasePage_v0.1.md を正式に supersede（置換）する後継バージョン**です。  
> v0.1 は履歴保持のため docs/ に残しています。

# Design_BasePage_v0.2

gov-llm-e2e-testkit — PageObject: BasePage v0.2 設計書

- バージョン: v0.2
- 最終更新日: 2025-12-09
- 対象: `tests/pages/base_page.py`
- 依存バージョン:
  - Playwright: v0.1 系（async）
  - PageObject v0.1（LoginPage / ChatPage）
  - log_writer.py v0.1
  - env_loader / pytest env v0.1
  - Responsibility_Map v0.1

---

## 1. 目的（Purpose）

BasePage v0.2 の目的は、既存の v0.1 で定義された「UI 操作の共通基盤」に対して、以下の機能を追加することにある。

1. **UI 操作失敗時の証跡収集（スクリーンショット + DOM HTML）を標準化すること**
2. **safe_click / safe_fill / その他の操作 API に例外フックを組み込み、失敗時に自動的に証跡を残すこと**
3. **Application Test / log_writer から見た証跡（artifacts）の扱いを一貫させること**
4. **pytest / CI / log_writer v0.1 と自然に接続できる拡張ポイントを提供すること**

これにより、以下が実現される。

- UI 変更や一時的な不具合でテストが FAIL した場合でも、  
  「そのとき画面がどうなっていたのか」「どの locator が死んでいたのか」を後から解析可能。
- pytest 側や log_writer 側に証跡収集の責務を持ち込まず、  
  **PageObject Layer の責務として完結**させる。

---

## 2. v0.1 との関係・位置づけ

### 2.1 v0.1 の BasePage の責務（おさらい）

v0.1 の BasePage は以下の責務を持っていた。

- Playwright `page` / `timeout` の保持
- 共通のユーティリティ操作
  - locator 取得（`find`）
  - ページ遷移
  -（必要に応じて）スクリーンショット保存
- LoginPage / ChatPage の「親クラス」として、UI 操作の基本機能を提供

### 2.2 v0.2 で追加される責務

v0.2 では、上記に加え次の責務を追加する。

1. **証跡収集 API の提供**
   - `collect_evidence(evidence_dir, label)`  
     - `label.png` と `label.html` を生成
2. **UI 操作失敗時の自動証跡保存**
   - `safe_click(locator, evidence_dir, label)`  
   - `safe_fill(locator, text, evidence_dir, label)`  
   - 必要に応じて他の high-level 操作も同様に扱う
3. **Application Test から渡される `case_assets_dir` との連携**
   - pytest 側で `case_assets_dir` を生成し、PageObject 側に渡すことで、  
     証跡が `logs/assets/YYYYMMDD/{case_id}/` に一貫して保存される。

### 2.3 非目標（Out of Scope）

- log_writer 自身の仕様変更（v0.1 のまま）
- pytest 側での自動スクリーンショット呼び出し
- CI（e2e.yml）側での artifacts パスの変更

---

## 3. 責務と境界（Responsibility & Boundaries）

### 3.1 BasePage v0.2 の責務

- Playwright `page` を安全に操作するための共通 API を提供する。
- UI 操作の失敗時に **スクリーンショット / DOM HTML の取得を一括で行う**。
- Application Test / log_writer から見た「証跡のファイルパス」を決定する役割を持たない。  
  - ファイルパス（ディレクトリ）は **pytest + log_writer 側**で決定され、  
    PageObject は「渡されたディレクトリにファイルを作る」だけ。

### 3.2 pytest / log_writer との境界

- pytest:
  - env_loader から env 設定を読み、`log_base_dir` を解決する。
  - log_writer のために `case_log_dir`, `case_assets_dir` を生成する。
  - PageObject に `evidence_dir` として `case_assets_dir` を渡す。

- PageObject (BasePage v0.2):
  - `evidence_dir` 配下に `screenshot` / `dom.html` を保存する。
  - 例外が起きたときに `collect_evidence()` を呼び出す。
  - 保存したファイルへのパスは、必要であれば Application Test 層へ返す。

- log_writer:
  - Application Test 層から渡された `artifacts`（パスの dict）をそのまま Markdown に出す。
  - 実ファイル作成には関与しない。

---

## 4. クラス構成（Class Design）

### 4.1 クラス概要

- 対象ファイル: `tests/pages/base_page.py`
- クラス名: `BasePage`

```python
class BasePage:
    def __init__(self, page, timeout: int = 20000): ...
    async def find(self, selector: str): ...
    async def safe_click(self, locator, *, evidence_dir=None, label="click_error"): ...
    async def safe_fill(self, locator, text: str, *, evidence_dir=None, label="fill_error"): ...
    async def collect_evidence(self, evidence_dir, label: str) -> dict[str, str]: ...
    async def screenshot(self, path): ...
````

※ v0.2 で追加・強化されるメソッドは `safe_click`, `safe_fill`, `collect_evidence`。

### 4.2 **init**

```python
def __init__(self, page, timeout: int = 20000):
    self.page = page
    self.timeout = timeout
```

* `page`: Playwright の `Page` インスタンス（pytest の `page` fixture から渡される）
* `timeout`: ミリ秒。env_config（config["browser"]["page_timeout_ms"]）から決定される想定。

---

## 5. 証跡収集 API（collect_evidence）

### 5.1 役割

* UI 操作失敗時（または任意のタイミング）に、以下の 2 つを保存する。

  * `screenshot`（PNG）
  * `DOM`（HTML）

### 5.2 シグネチャ

```python
from pathlib import Path
from typing import Union

async def collect_evidence(
    self,
    evidence_dir: Union[str, Path],
    label: str,
) -> dict[str, str]:
    ...
```

### 5.3 入力

* `evidence_dir`:

  * 例: `logs/assets/20251209/RAG_BASIC_001`
  * pytest + log_writer 側で `ensure_log_dirs()` により生成されたディレクトリ。
* `label`:

  * 例: `"click_error"`, `"ask_error"`, `"login_error"` など。
  * ファイル名のプレフィックスとして利用される。

### 5.4 出力

* `dict[str, str]`:

  * `"screenshot"` → `"/path/to/.../click_error.png"`
  * `"dom"` → `"/path/to/.../click_error.html"`

### 5.5 擬似実装

```python
async def collect_evidence(self, evidence_dir, label: str) -> dict[str, str]:
    evidence_dir = Path(evidence_dir)
    evidence_dir.mkdir(parents=True, exist_ok=True)

    screenshot_path = evidence_dir / f"{label}.png"
    dom_path = evidence_dir / f"{label}.html"

    # スクリーンショット取得
    await self.page.screenshot(path=str(screenshot_path))

    # DOM 取得
    html = await self.page.content()
    dom_path.write_text(html, encoding="utf-8")

    return {
        "screenshot": str(screenshot_path),
        "dom": str(dom_path),
    }
```

---

## 6. 安全な UI 操作（safe_* 系）

### 6.1 safe_click

#### 6.1.1 目的

* locator をクリックする際に、

  * `visible` になるまで待機
  * click 失敗時に `collect_evidence()` を呼び出し、証跡を保存
  * その後例外を再送出し、pytest の FAIL に繋げる

#### 6.1.2 シグネチャ

```python
async def safe_click(
    self,
    locator,
    *,
    evidence_dir=None,
    label: str = "click_error",
):
    ...
```

#### 6.1.3 擬似実装

```python
async def safe_click(self, locator, *, evidence_dir=None, label: str = "click_error"):
    try:
        await locator.wait_for(state="visible", timeout=self.timeout)
        await locator.click()
    except Exception:
        if evidence_dir is not None:
            await self.collect_evidence(evidence_dir, label)
        raise
```

### 6.2 safe_fill

#### 6.2.1 シグネチャ

```python
async def safe_fill(
    self,
    locator,
    text: str,
    *,
    evidence_dir=None,
    label: str = "fill_error",
):
    ...
```

#### 6.2.2 擬似実装

```python
async def safe_fill(self, locator, text: str, *, evidence_dir=None, label: str = "fill_error"):
    try:
        await locator.wait_for(state="visible", timeout=self.timeout)
        await locator.fill(text)
    except Exception:
        if evidence_dir is not None:
            await self.collect_evidence(evidence_dir, label)
        raise
```

---

## 7. screenshot（既存メソッドの整理）

v0.1 時点で存在するスクリーンショット API を、v0.2 では次のように整理する。

### 7.1 シグネチャ

```python
async def screenshot(self, path) -> None:
    await self.page.screenshot(path=str(path))
```

* 呼び出し側（Application Test / ChatPage / LoginPage）は、
  `ensure_log_dirs()` で得た `case_assets_dir` を用いてパスを決定し、`BasePage.screenshot()` を呼び出す。

---

## 8. LoginPage / ChatPage との連携

### 8.1 LoginPage v0.2 側の利用イメージ

```python
class LoginPage(BasePage):
    async def login(self, username: str, password: str, *, evidence_dir=None):
        user_input = self.page.get_by_test_id("login-username")
        pass_input = self.page.get_by_test_id("login-password")
        submit_btn = self.page.get_by_test_id("login-submit")

        try:
            await self.safe_fill(user_input, username, evidence_dir=evidence_dir, label="login_username_error")
            await self.safe_fill(pass_input, password, evidence_dir=evidence_dir, label="login_password_error")
            await self.safe_click(submit_btn, evidence_dir=evidence_dir, label="login_submit_error")
        except Exception:
            # ここでは例外を握りつぶさず、そのまま上位へ伝播
            raise
```

### 8.2 ChatPage v0.2 側の利用イメージ

```python
class ChatPage(BasePage):
    async def ask(self, text: str, *, evidence_dir=None) -> str:
        input_box = self.page.get_by_test_id("chat-input")
        send_button = self.page.get_by_test_id("chat-send")

        try:
            await self.safe_fill(input_box, text, evidence_dir=evidence_dir, label="chat_input_error")
            await self.safe_click(send_button, evidence_dir=evidence_dir, label="chat_send_error")
            # ここでLLMの応答待ち
            await self._wait_for_response()
            return await self._get_latest_response()
        except Exception:
            if evidence_dir is not None:
                # ask() 全体の失敗時にも追加証跡が必要ならここで collect_evidence
                await self.collect_evidence(evidence_dir, "ask_error")
            raise
```

---

## 9. pytest / log_writer との接続仕様

### 9.1 pytest 側（Application Test）の流れ（例）

```python
from src.log_writer import LogContext, create_case_log, ensure_log_dirs

async def test_rag_basic(case, chat_page, env_config, log_base_dir):
    config, options = env_config
    now = datetime.now(timezone(timedelta(hours=9)))

    # 1. ログ用ディレクトリ生成
    case_log_dir, case_assets_dir = ensure_log_dirs(log_base_dir, case["id"], now)

    # 2. 実行（証跡ディレクトリを渡す）
    question = case["question"]
    answer = await chat_page.ask(question, evidence_dir=case_assets_dir)

    # 3. 判定ロジック（missing / unexpected）
    #    ...
    artifacts = {
        "screenshot": str(case_assets_dir / "ask_error.png"),  # 実際には存在チェックしてから
        "dom": str(case_assets_dir / "ask_error.html"),
    }

    ctx = LogContext(
        case_id=case["id"],
        test_type="basic",
        environment=config["profile"],
        timestamp=now,
        browser_timeout_ms=config["browser"]["browser_timeout_ms"],
        page_timeout_ms=config["browser"]["page_timeout_ms"],
        question=question,
        output_text=answer,
        # 各種判定結果…
        artifacts=artifacts,
        status=status,
    )

    create_case_log(log_base_dir, ctx)
    assert status == "PASS"
```

※ 実装時には、`artifacts` の内容を **実際に存在する場合のみ** 設定するなどの防御を加える。

---

## 10. 例外・エラー処理方針

1. **safe_click / safe_fill**

   * locator 操作が失敗した場合は、証跡保存を試みたうえで例外を再送出する。
   * 証跡保存自体が失敗した場合（ディスクフル等）は、その例外も pytest に伝播する。

2. **collect_evidence**

   * `evidence_dir` に書き込み不可の場合、`OSError` をそのまま送出。
   * Application Test / pytest 側で FAIL として扱う（テスト環境問題として認識）。

3. **ページ状態異常**

   * `page.content()` が取得できない（ページが閉じられている等）場合も例外をそのまま伝播。

---

## 11. テスト観点（BasePage v0.2）

BasePage 単体のテスト方針（概略）：

1. **正常系**

   * `safe_click` が成功するケース
   * `safe_fill` が成功するケース
   * `collect_evidence` が指定パスに PNG / HTML を生成する

2. **異常系**

   * locator が存在しない場合に `safe_click` が例外を raise し、同時に証跡を作成する
   * locator が表示されない場合に timeout となり、証跡が残る
   * `collect_evidence` で write 不可のディレクトリを指定した場合に `OSError` が発生する

v0.2 の段階では、E2E テストの一部として検証されることを優先し、
BasePage 単体テストは「余裕があれば」範囲でよい。

---

## 12. 今後の拡張（v0.3 以降の想定）

* 証跡の分割収集：

  * 操作ごとに `label` を変えて複数セットの PNG/HTML を残す
* 差分ハイライト:

  * DOM の差分を抽出し、ログの Details にハイライトを記録する
* 画面要素単位スクリーンショット:

  * 特定 locator の bounding box のみを切り出した画像を生成する

---

## 13. 実装・運用メモ

1. 本設計書に基づき、`tests/pages/base_page.py` を v0.2 相当に実装する。
2. LoginPage / ChatPage に `evidence_dir` パラメータを追加する（v0.2 化）。
3. pytest 側（Smoke / Basic / Advanced）にて `case_assets_dir` を PageObject に渡すように修正する。
4. ログ仕様（Design_logging_v0.1）は v0.1 のまま利用し、v0.2 では artifacts の充実のみを行う。
5. 実装完了後、PROJECT_STATUS / CHANGELOG を v0.1.16 などに更新する。

---
