# 📘 **Design_pytest_v0.2.md**

**This document supersedes Design_pytest_env_v0.1.**
（pytest Execution Layer の正式設計仕様 v0.2）

---

# 1. Document Purpose（目的）

pytest v0.2 は gov-llm-e2e-testkit における
**E2E 自動テスト実行レイヤーの標準仕様**を定義する。

特に v0.2 では、以下の責務を追加・強化する：

1. **evidence_dir（証跡保存ディレクトリ）の生成と PageObject v0.2 への伝搬**
2. **Smoke / Basic / Advanced テストの構造統一**
3. **log_writer v0.1 と evidence の自然な統合**
4. **INTERNET / LGWAN 両環境での安定実行**
5. **将来の v0.3+（strict/lenient）へ拡張できる構造**

本仕様は Playwright / PageObject（BasePage / LoginPage / ChatPage）および
log_writer v0.1 と密接に連携する。

---

# 2. Responsibilities（責務）

## 2.1 pytest Execution Layer が担当すること（MUST）

* env_loader が返す設定値（INTERNET / LGWAN）を反映する
* Browser / Context / Page の生成と破棄
* **テストケース単位の evidence_dir 生成**（v0.2 で追加）
* PageObject に evidence_dir を渡す
* log_writer にログ出力（case_log_dir）を渡す
* CI の exit code 5（テスト数 0）回避のための skip ハンドリング

## 2.2 PageObject に任せること（MUST NOT）

pytest v0.2 は以下のロジックを持たない：

* UI 操作（click / fill / wait）
* スクリーンショットや DOM 取得（BasePage v0.2 の責務）
* ログファイル（Markdown）の書き込み（log_writer の責務）

pytest はあくまで **「実行環境の管理」＋「PageObject 呼び出し」**に徹する。

---

# 3. pytest v0.2 の新要素（v0.1 → v0.2 の主な差分）

| 機能                       | v0.1       | v0.2                            |
| ------------------------ | ---------- | ------------------------------- |
| evidence_dir の扱い         | なし         | **テストケース単位で生成し、PageObject に伝搬** |
| case_dirs fixture        | なし         | **追加（標準化）**                     |
| smoke/basic/advanced の構造 | ばらばら       | **統一化（例外時 evidence 保存）**        |
| page.timeout の設定         | 一部テスト内     | **conftest に集約し、環境ごとに適用**       |
| log_writer 統合            | smoke のみ手動 | **全テスト統一で統合**                   |

---

# 4. conftest.py 設計（v0.2）

pytest v0.2 の中心となる強化ポイント。

---

## 4.1 fixture: env_config（v0.1 継続）

env_loader から profile, browser.timeout などを取得する。

```python
@pytest.fixture(scope="session")
def env_config():
    config, options = load_env()
    return config, options
```

---

## 4.2 fixture: browser（v0.1 → v0.2 強化）

Profile（INTERNET/LGWAN）の timeout 値を page.default_timeout に反映。

```python
@pytest.fixture(scope="session")
async def browser(env_config):
    config, _ = env_config
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=config["browser"]["headless"])
        yield browser
        await browser.close()
```

---

## 4.3 fixture: page（timeout 統合）

PageObject から参照される timeout を保証。

```python
@pytest.fixture
async def page(browser, env_config):
    config, _ = env_config
    context = await browser.new_context()
    page = await context.new_page()
    page.set_default_timeout(config["browser"]["page_timeout_ms"])
    yield page
    await context.close()
```

---

## 4.4 fixture: log_base_dir（v0.1 継続）

ログ保存ルートを options から取得。

```python
@pytest.fixture(scope="session")
def log_base_dir(env_config):
    _, options = env_config
    log_dir = options.get("log_dir", "logs")
    return Path(log_dir)
```

---

## 4.5 fixture（v0.2 新規）: case_dirs

**case_id + timestamp を入力すると case_log_dir と case_assets_dir を返す
“標準フック” として pytest に追加。**

```python
@pytest.fixture
def case_dirs(log_base_dir):
    def _make(case_id: str, now: datetime):
        return ensure_log_dirs(log_base_dir, case_id, now)
    return _make
```

### 役割

* **log_writer が使う case_log_dir**
* **PageObject に渡す evidence_dir（＝case_assets_dir）**

この 2 つを pytest 側で完全に分離して管理する。

---

# 5. テストコードの標準構造（pytest v0.2）

## 5.1 Smoke Test v0.2 の構造（例）

```python
now = datetime.now(JST)
case_log_dir, case_assets_dir = case_dirs("SMOKE_001", now)

answer = await chat_page.ask("こんにちは", evidence_dir=case_assets_dir)

ctx = LogContext(
    case_id="SMOKE_001",
    test_type="smoke",
    ...
    assets_dir=str(case_assets_dir),
)

create_case_log(case_log_dir, ctx)
assert ...
```

---

## 5.2 Basic Test v0.2 の構造（例）

```python
case_log_dir, case_assets_dir = case_dirs(case["id"], now)

answer = await chat_page.ask(case["question"], evidence_dir=case_assets_dir)

missing = [kw for kw in case["expected_keywords"] if kw not in answer]
unexpected = ...

ctx = LogContext(
   ...
   assets_dir=str(case_assets_dir)
)

create_case_log(case_log_dir, ctx)
assert status == "PASS"
```

---

## 5.3 Advanced Test v0.2 の構造（例）

Multi-turn でも evidence_dir を共通で使う：

```python
case_log_dir, case_assets_dir = case_dirs(case["id"], now)

for turn in case["turns"]:
    if turn["role"] == "user":
        last_answer = await chat_page.ask(turn["content"], evidence_dir=case_assets_dir)
```

応答検証・log_writer 呼び出しなどは v0.1 継続。

---

# 6. Integration with PageObject v0.2（統合仕様）

pytest v0.2 は PageObject v0.2 と次の関係にある：

| Component      | pytest の役割                    | PageObject の役割                            |
| -------------- | ----------------------------- | ----------------------------------------- |
| BasePage v0.2  | timeout 与える / evidence_dir 渡す | safe_click / safe_fill / collect_evidence |
| LoginPage v0.2 | evidence_dir を与えて login       | UI 操作＋異常時 evidence 生成                     |
| ChatPage v0.2  | evidence_dir を ask() に与える     | 応答取得＋異常時 evidence 生成                      |
| log_writer     | case_log_dir を与える             | Markdown ログ生成                             |

pytest は **一切の UI 操作を行わず、PageObject に責務を委譲**する。

---

# 7. Error Handling（エラー処理）

## 7.1 evidence_dir が None の場合

PageObject 側は証跡を取らずに例外を再送出
→ pytest がそのまま FAIL を報告
→ log_writer のみがログを記録
（初心者向け：これは smoke の最軽量実行に対応）

## 7.2 evidence_dir が指定されている場合

PageObject 側で：

* chat_input_error
* chat_send_error
* chat_wait_error
* chat_extract_error
* ask_error
* login_failure

などの PNG / HTML が自動生成される。

---

# 8. CI（GitHub Actions）との連携

pytest v0.2 は CI で次を保証する：

* **Skip 判定**により exit code 5（テスト数0）を回避
* smoke/basic/advanced の3カテゴリが必ず1件以上実行される
* logs/ 以下の evidence (assets) が CI artifacts として収集可能
* SKIP_E2E が立っている場合は Skip として扱う
* synthetic_html データが存在する場合、Basic/Advanced の 0件実行を防ぐ

---

# 9. 将来拡張（pytest v0.3+）

* strict/lenient モードの導入

  * strict：応答検証失敗でも evidence 追加収集
* retry_policy（LGWAN 用）
* evidence_dir の自動整理（一定期間で削除）
* JSON ログ＋HTML レポート統合
* parallel execution（Playwright shard）対応

---

# 10. Versioning（バージョン管理）

本設計書は：

* `Design_pytest_env_v0.1.md` を supersede
* 旧版は docs/ に残し
* 最新版は `Design_pytest.md` を介して参照する

  * ※次ステップで自動生成します

---

# 📌 **End of Document**

---

