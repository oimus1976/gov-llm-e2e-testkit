# Design_env_v0.1  

gov-llm-e2e-testkit — env.yaml 設計書  
バージョン: v0.1  
最終更新: 2025-12-07  

参照:  
- PROJECT_GRAND_RULES v2.0  
- Startup Template v3.0  
- Startup Workflow v3.0  
- test_plan_v0.1  
- Design_playwright_v0.1  
- Design_BasePage_v0.1 / ChatPage_v0.1 / LoginPage_v0.1  
- Design_ci_e2e_v0.1  

---

## 1. 目的（Purpose）

本書は gov-llm-e2e-testkit における  
**INTERNET / LGWAN の 2 種類の実行環境を統一的に扱うための env.yaml の正式仕様**  
を定義する。

env.yaml は以下を実現するための唯一の設定ファイルである：

- INTERNET（GitHub Actions / 開発端末）と LGWAN（庁内ネットワーク）の切り替え  
- URL / 認証情報の安全な参照（環境変数を前提）  
- Playwright の browser / page timeout のプロファイル差分  
- pytest 実行時の環境依存パラメータの一本化  

本設計は v0.1（最小仕様）として定義し、将来の拡張（v0.2 → v1.0）を見据えた構造を採用する。

---

## 2. スコープ（Scope）

env.yaml は以下のレイヤで用いる。

- Python（BasePage / ChatPage / LoginPage）のブラウザ起動設定  
- pytest の実行環境（URL / 認証情報 / timeout）  
- GitHub Actions（INTERNET profile のみ使用）  
- LGWAN 実行時のローカル環境（profile=lgwan）

env.yaml は *設計書レベルで必須* とし、削除を禁止する（PROJECT_GRAND_RULES 2.2）。

---

## 3. 設計方針（Design Principles）

### 3.1 profiles 方式の採用  
INTERNET / LGWAN の設定差分を **profiles** として env.yaml 内に保持する。

### 3.2 認証情報は平文で格納しない  
env.yaml には `${VARNAME}` の placeholder のみ記載する。  
実際の値は環境変数（GitHub Secrets / ローカル）で提供する。

### 3.3 profile 切替は ENV_PROFILE で行う  
デフォルト profile は `internet`。  
pytest 実行時に以下のように指定することで LGWAN に切り替える。

```bash
ENV_PROFILE=lgwan pytest ...
```

### 3.4 timeout の差分を許容

LGWAN は遅延が大きいため、timeouts は INTERNET の 4〜6 倍を推奨とする。

### 3.5 versioned schema

env.yaml 自体の version を明記し、将来の破壊的変更（v1.0）に備える。

---

## 4. env.yaml（v0.1） スキーマ定義

```yaml
version: "0.1"

# 現在使用する profile（実行時に ENV_PROFILE で上書き可）
profile: "internet"

profiles:
  internet:
    description: "GitHub Actions / 開発端末向けの高応答環境"
    url: "https://example-internet-service/"     # 実値は必ず環境変数で上書きする
    username: "${QOMMONS_USERNAME}"
    password: "${QOMMONS_PASSWORD}"
    browser:
      headless: true
      browser_timeout_ms: 15000      # browser-level timeout
      page_timeout_ms: 15000         # page.set_default_timeout()

  lgwan:
    description: "庁内 LGWAN 用プロファイル（低速・高遅延環境）"
    url: "https://example-lgwan-service/"        # 実値は庁内端末のみで保持
    username: "${LGWAN_USERNAME}"
    password: "${LGWAN_PASSWORD}"
    browser:
      headless: true
      browser_timeout_ms: 60000       # INTERNET の約 4 倍
      page_timeout_ms: 60000

# pytest 実行時の共通設定（予約領域）
options:
  retry_policy: 0       # v0.2 で LGWAN の再試行ポリシーに拡張可能
  log_dir: "logs"       # ログ保存先（LGWAN はローカル固定）
```

---

## 5. env.yaml のロード方式（BasePage / pytest）

### 5.1 読み込み処理（疑似コード）

```python
import yaml, os

def load_env():
    cfg = yaml.safe_load(open("env.yaml", "r", encoding="utf-8"))
    profile = os.getenv("ENV_PROFILE", cfg.get("profile", "internet"))
    resolved = cfg["profiles"][profile]

    # ${VAR} プレースホルダを環境変数で置換
    for key in ["url", "username", "password"]:
        val = resolved.get(key)
        if isinstance(val, str) and val.startswith("${") and val.endswith("}"):
            env_name = val.strip("${}")
            resolved[key] = os.environ.get(env_name)

    return resolved, cfg.get("options", {})
```

### 5.2 BasePage での利用

```python
config, opt = load_env()

browser = playwright.chromium.launch(headless=config["browser"]["headless"])
context = browser.new_context()
page = context.new_page()
page.set_default_timeout(config["browser"]["page_timeout_ms"])
```

LGWAN と INTERNET の差分は **ブラウザの timeout** のみで実行可能。

---

## 6. CI（e2e.yml）との整合性

Design_ci_e2e_v0.1 により、GitHub Actions では profile=internet を利用する。
env.yaml の役割は以下：

* env.yaml の存在チェック（削除防止）
* URL / USERNAME / PASSWORD は Secrets で上書き
* LGWAN 用 profile は CI では使用しない

（LGWAN テストは人間が庁内端末から手動実行する運用）

---

## 7. セキュリティポリシー（v0.1 強制）

* env.yaml に **生パスワードを書いてはならない**
* GitHub Actions はすべて Secrets 上書き
* LGWAN 端末は「ローカル環境変数 + env.yaml」の組合せ
* LGWAN プロファイルの URL は庁内ネットワーク以外で利用不可
* env.yaml は `.gitignore` に含めず、必ず Git にコミットする（設計上必須）

---

## 8. 将来拡張（v0.2 / v1.0 予定）

| バージョン | 拡張内容                                                 |
| ----- | ---------------------------------------------------- |
| v0.2  | retry_policy による LGWAN 自動再試行、timeout 自動調整、ログ構造追加     |
| v1.0  | multi-tenant profile、secrets マッピングのスキーマ化、RAG 検証レベル設定 |

---

## 9. まとめ

env.yaml v0.1 は、
gov-llm-e2e-testkit における **INTERNET / LGWAN の統一設定基盤** を提供する。

今後の CI 実装・LGWAN 手動実行・pytest 拡張
すべての共通土台として機能するため、
**このファイルはプロジェクト全体のクリティカルコンポーネント**である。

以上を env.yaml の正式 v0.1 として採用する。

---
