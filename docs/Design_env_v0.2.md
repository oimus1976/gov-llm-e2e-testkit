いい勘してます。ここは「とりあえず動かす」より **設計レイヤを先に固める局面**ですね。
約束どおり、**Design_env_v0.2 を正式設計書として起こす＋STATUS/CHANGELOG 更新案**まで一気に出します。

---

## 📝 Design_env_v0.2（新規設計書・全文）

> **Note**
> 本ドキュメント **Design_env_v0.2.md** は
> **Design_env_v0.1.md を正式に supersede（置換）する後継バージョン**です。
> v0.1 は履歴保持のため docs/ に残します。 

# Design_env_v0.2

gov-llm-e2e-testkit — 環境設定レイヤ（env.yaml / .env / env_loader）設計書 v0.2

* バージョン: v0.2
* 最終更新日: 2025-12-09
* 対象ファイル:

  * `config/env.yaml`
  * `src/env_loader.py`
  * （参考）`.env*` （Git 管理外、ユーザー環境ファイル）
* 依存バージョン:

  * PROJECT_GRAND_RULES v3.0 
  * Startup Template v3.0 
  * Design_pytest_v0.2
  * Design_playwright_v0.1

---

## 1. 目的（Purpose）

本設計書の目的は、gov-llm-e2e-testkit における
**環境設定（INTERNET / LGWAN などのプロファイル）と認証情報管理の方式を、OSS として無理なく運用できるレベルに整理**することである。

特に以下を達成する：

1. `env.yaml` と `.env` を組み合わせた、
   **「構造は YAML・秘密情報は .env」** という役割分担の明確化。
2. Windows / Mac / Linux いずれの一般ユーザーでも、
   **追加ツールをほぼ入れずにテストを実行できる運用方法**を提供する。
3. 環境変数・.env・env.yaml の **優先順位とエラー挙動を明確化し、後から破綻しない基盤**を作る。
4. CI（GitHub Actions）および LGWAN 運用と矛盾しない形で、
   **Secrets 管理方式を将来のプロジェクトにもテンプレ化**できるようにする。 

---

## 2. 背景（Background）

v0.1 では以下の設計で運用していた：

* `config/env.yaml` に `url`, `username`, `password` 等を定義
* 値は `${QOMMONS_URL}` のように **環境変数のプレースホルダ**で表現
* `src/env_loader.py` が env.yaml を読み、
  `${VARNAME}` を `os.environ[VARNAME]` で置換
* 環境変数が未定義の場合、`OSError` を送出

この設計は以下の点で合理的だったが：

* **Secrets を env.yaml に直書きしない**（セキュリティ上の最低ラインを確保）
* CI（GitHub Actions）の `secrets.*` と相性が良い

一方で、次の課題が明確になった：

1. **複数プロジェクト・複数サイトを扱うときに、環境変数の管理が破綻しやすい**

   * Windows / Mac / Linux で設定方法が異なる
   * ローカル端末を変えるごとに再設定が必要
2. gov-llm-e2e-testkit を OSS として配布した場合、

   * 「まず環境変数を○個作ってください」という導入手順は **一般ユーザーには重いハードル**になる。
3. LGWAN / INTERNET / dev / ci など複数プロファイルを想定すると、

   * **環境変数名が爆発しやすく、どれがどこで使われているか見えにくい。**

これらの理由から、v0.2 では **`.env` 方式を正式に採用し、環境変数は「高度・特殊な用途」に限定する**方向へ再設計する。

---

## 3. 要求仕様（Requirements）

### 3.1 機能要求（Functional）

1. **複数プロファイル対応**

   * INTERNET / LGWAN / dev / ci など、`env.yaml` の profile に応じて設定を切り替えられること。 

2. **.env による Secrets 管理**

   * URL / USERNAME / PASSWORD 等の秘密情報は `.env` ファイルもしくは環境変数で提供される。
   * env.yaml に平文を書かせない。

3. **プロファイル別 .env ファイル**

   * `profile=internet` の場合は `.env.internet` を優先的に読み込める。
   * `profile=lgwan` の場合は `.env.lgwan` を読み込める。

4. **既存の環境変数方式との両立**

   * すでに `QOMMONS_URL` などを環境変数に設定している環境でも、変更なしで動作する。

5. **エラー時の明確なメッセージ**

   * 未設定の変数がある場合は、「どの profile の・どのキー・どの環境変数名が足りないか」を明示して例外を送出する。

---

### 3.2 非機能要求（Non-Functional）

1. **OSS ユーザーに優しい初期設定**

   * インストール後の手順は、基本的に
     **「.env.sample を .env にコピーして値を入れる」**だけで完結させる。

2. **LGWAN 運用と矛盾しない**

   * `.env` の実体は LGWAN 側の閉域環境ストレージに置くことを前提とする。
   * env_loader 自体は外部通信を行わない。 

3. **CI パイプラインを壊さない**

   * GitHub Actions では現行どおり `env:` / `secrets.*` 経由の環境変数注入をサポートする。
   * `.env` が存在しなくても、CI が想定どおり動作する。

4. **後方互換性**

   * `load_env()` のシグネチャは v0.1 と同一のまま維持する。

     ```python
     def load_env(env_path: str = "env.yaml") -> Tuple[Dict[str, Any], Dict[str, Any]]:
         ...
     ```

---

## 4. 全体アーキテクチャ（Overview）

### 4.1 構成要素

* `config/env.yaml`

  * プロファイルごとの **構造的な設定**（URL, TIMEOUT, ログディレクトリ等）を記述
  * Secrets 部分は `${VARNAME}` プレースホルダで表現

* `.env`, `.env.internet`, `.env.lgwan`（Git 管理外）

  * 実際の URL / ユーザー名 / パスワードを記載
  * プロファイルごとに分割・使い分け可能

* `os.environ`

  * CI や高度な環境での Secrets 注入経路
  * `.env` よりも優先される

* `src/env_loader.py`

  * 上記の3レイヤを読み込み・マージし、pytest / Playwright に渡す dict を生成する。

---

### 4.2 読み込みフロー

1. `load_env(env_path="env.yaml")` 呼び出し
2. `env.yaml` を読み込み、`profile` を決定
3. `.env` / `.env.<profile>` の順で `load_dotenv()` を実行
4. `${VARNAME}` プレースホルダを `os.environ` から解決
5. 解決後の `profile_config` / `options` を返却

---

## 5. env.yaml 設計

### 5.1 サンプル構造

```yaml
# config/env.yaml（例）

profile: internet  # デフォルトプロファイル

profiles:
  internet:
    url: ${QOMMONS_URL}
    username: ${QOMMONS_USERNAME}
    password: ${QOMMONS_PASSWORD}
    browser_timeout_ms: 60000
    page_timeout_ms: 30000

  lgwan:
    url: ${QOMMONS_LGWAN_URL}
    username: ${QOMMONS_LGWAN_USERNAME}
    password: ${QOMMONS_LGWAN_PASSWORD}
    browser_timeout_ms: 90000
    page_timeout_ms: 60000

options:
  log_base_dir: logs
  # 将来: retries, strict_mode など
```

### 5.2 プロファイル選択ロジック

* `ENV_PROFILE` 環境変数が指定されていればそれを優先。
* それ以外の場合は `env.yaml` の `profile` キーを使用。
* `profiles` に存在しない profile が指定された場合は `ValueError` を送出。

---

## 6. .env 設計（dotenv 方式）

### 6.1 ファイル命名規則

* 共通設定（どのプロファイルでも使う値）:

  * `.env`

* プロファイル固有の Secrets:

  * `.env.internet`
  * `.env.lgwan`
  * `.env.dev` 等

### 6.2 変数命名規則

* URL:

  * `QOMMONS_URL`, `QOMMONS_LGWAN_URL` など
* ユーザー名:

  * `QOMMONS_USERNAME`, `QOMMONS_LGWAN_USERNAME`
* パスワード:

  * `QOMMONS_PASSWORD`, `QOMMONS_LGWAN_PASSWORD`

### 6.3 読み込み順序

1. `.env`（存在すれば）
2. `.env.<profile>`（存在すれば）
3. OSの環境変数（すべて）

**優先順位**は次章の `os.environ` 優先ルールを参照。

---

## 7. 優先順位ルール（Precedence）

### 7.1 環境変数 vs .env

* `python-dotenv` は `.env` を読み込むとき、
  デフォルトでは **既に存在する `os.environ` を上書きしない** 前提で利用する。

env_loader v0.2 ではこれを前提とし、次のルールを採用する：

1. OS 環境変数（CI / 手動設定）は **常に最優先**。
2. `.env` および `.env.<profile>` は **OS に存在しないキーだけを補完**する。
3. env.yaml の `${VARNAME}` は、最終的な `os.environ` から取得する。

### 7.2 実装イメージ

```python
from dotenv import load_dotenv

def _load_dotenv_for_profile(profile: str) -> None:
    # 1. .env 共通
    load_dotenv(".env", override=False)

    # 2. プロファイル別
    profile_env = f".env.{profile}"
    load_dotenv(profile_env, override=False)

    # 将来: DOTENV_PATH 環境変数で明示指定も可
```

---

## 8. env_loader v0.2 仕様

### 8.1 シグネチャ（v0.1 から変更なし）

```python
from typing import Any, Dict, Tuple

def load_env(env_path: str = "env.yaml") -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """
    env.yaml + .env + 環境変数から設定を読み込み、
    profile_config, options の2つの dict を返す。
    """
```

### 8.2 処理フロー

1. `env.yaml` を読み込む。
2. `ENV_PROFILE` または `env.yaml["profile"]` から `selected_profile` を決定。
3. `_load_dotenv_for_profile(selected_profile)` を呼び出す。
4. `cfg["profiles"][selected_profile]` を `profile_cfg` として取得。
5. `profile_cfg` 中の文字列値について `${VARNAME}` プレースホルダを解決する。
6. 解決結果 `profile_cfg_resolved` と `cfg.get("options", {})` を返す。

### 8.3 プレースホルダ解決処理

* 対象:

  * `profile_cfg` 内の文字列値のうち、
    `value.startswith("${") and value.endswith("}")` のもの。
* 手順:

  1. `env_key = value.strip("${}")`
  2. `env_val = os.getenv(env_key)`
  3. env_val が `None` の場合は例外を送出。

### 8.4 例外仕様

#### 8.4.1 不正な profile

```python
ValueError("Invalid profile '<name>' in ENV_PROFILE or env.yaml")
```

#### 8.4.2 未定義の環境変数（Secrets 不足）

```python
class MissingSecretError(EnvironmentError):
    pass
```

メッセージ例：

```text
MissingSecretError: Environment variable 'QOMMONS_URL' is not set
but required by env.yaml profile 'internet' (key: url)
```

※ pytest / CI 側で `MissingSecretError` をキャッチし、
`SKIP_E2E` 等の制御フラグと組み合わせて「テストを SKIP する」「実行を中止する」などを選択できるようにする。
env_loader 自身は **「足りない」ことだけを正直に報告**し、スキップ判断は上位レイヤに委ねる。 

---

## 9. pytest / CI との連携

### 9.1 pytest（ローカル実行）

* 開発者は以下の手順で使う想定：

  1. `.env.sample` を `.env.internet` にコピー
  2. 値（URL / USER / PASSWORD）を記入
  3. `ENV_PROFILE=internet python -m pytest`

* プロファイル切り替え例：

  ```bash
  ENV_PROFILE=lgwan python -m pytest
  ```

### 9.2 CI（GitHub Actions）

* CI 上では `.env` は使わず、`env:` と `secrets.*` を用いて環境変数を設定する。
* その場合も `.env` ロードは実行されるが、`override=False` により `secrets` が優先される。

### 9.3 LGWAN 環境

* `.env.lgwan` を LGWAN 内ストレージに配置し、
  `ENV_PROFILE=lgwan` でテストを実行する。
* `.env.lgwan` 自体は Git に含めず、運用手順書側で取り扱う。

---

## 10. テスト方針（Test Plan）

1. **正常系**

   * `.env` のみで INTERNET profile を起動 → `url/username/password` が正しく解決される。
   * `.env.internet` のみで INTERNET profile → 同上。
   * `.env` + `.env.internet` + 環境変数競合時に、
     環境変数が最優先されること。

2. **異常系**

   * env.yaml のプレースホルダに対応する値が一切存在しない場合、
     `MissingSecretError` が送出される。
   * ENV_PROFILE に無効な値を入れた場合、`ValueError` が送出される。

3. **CI**

   * GitHub Actions 上で `.env` が存在しない前提で、
     `secrets` による環境変数注入のみで正常動作すること。

---

## 11. 移行ガイド（Migration）

1. 既存の `config/env.yaml` は基本的にそのまま利用できる。
2. これまで OS 環境変数のみに頼っていた環境では、動作は変わらない。
3. 新規の推奨フロー：

   * `.env.sample` を追加（URL / USER / PASSWORD のキーのみ）
   * 利用者は `.env` or `.env.internet` を作成し、値を書くだけでよい。
4. env_loader v0.2 実装後、PROJECT_STATUS / CHANGELOG に反映する。

---

（Design_env_v0.2.md 本文ここまで）

