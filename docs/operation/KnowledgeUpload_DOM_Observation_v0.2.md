# Private Knowledge 登録画面の実機DOM観測手順 v0.2

更新日：2026-10-09  
対象：Issue #2 / Draft PR #1（`feature/private-knowledge-upload-mvp`）  
旧版：`KnowledgeUpload_DOM_Observation_v0.1.md`（履歴として保存）

## 1. 目的と確認済みの範囲

**今回の目的は「ログインして登録画面の実際の導線とDOMを観測する」ことだけ。ファイルは選択・アップロードしない。**

- main の PR #4 はマージ済み。ログイン成功待機は CSP を回避する Playwright のネイティブ `wait_for_url` に変更済み。
- Draft PR #1 にその修正を統合済み（コミット `2d32e521c2292c04f7ea39332025285cbea68f7d`）。
- 統合後の CI `37850592792` では Smoke Test 1件PASS。**Windows実機の `--inspect-ui`、登録画面DOM、アップロードは未検証。**
- `--inspect-ui` はログイン後にInspectorで停止する。アップロードはコード上無効のまま。

## 2. 実行する環境と事前確認

- インターネット接続できる**検証用Windows端末**と、操作権限のあるQommonsAIのテストアカウントを使用する。LGWAN本番端末・町の業務データを使用しない。
- **GitHub Actions の Secrets はローカルPCには反映されない。** 手元の既存 `.env` / `.env.internet` / OS環境変数に、当該テストアカウントのログイン情報が揃っていることを本人が確認する。
- `load_env()` はプロファイルを `ENV_PROFILE` 優先、なければ `env.yaml` の `profile` で選択し、値の優先順位はOS環境変数 ＞ `.env` ＞ `.env.<profile>`。今回の想定は既存の `internet`。勝手に設定を編集・切替しない。
- 認証情報、`.env`、Cookie、Storage State、ログイン画面HTML、DevToolsのNetworkレスポンスは共有・コミットしない。
- ローカルに未コミット変更がある場合は一旦停止。作業ツリーを消したり、強制切替・上書き・stash/dropをしない。

## 3. PowerShellでの実行準備

**既存のリポジトリのルート**でPowerShellを開く（パスは各端末の実配置を使う）。

```powershell
git status --short
git branch --show-current
git fetch origin
git switch feature/private-knowledge-upload-mvp
git merge --ff-only origin/feature/private-knowledge-upload-mvp
git rev-parse --short HEAD
```

- `git switch` が「ブランチなし」で失敗する場合のみ、既存の変更がないことを確認して `git switch --track origin/feature/private-knowledge-upload-mvp` を使用する。
- 期待するHEADは `2d32e521c229` またはそれ以降の同じDraftブランチのコミット。予想外の差分・分岐があれば停止する。
- 以下は**既に導入済みなら省略可**。端末の管理権限や接続制限を超えるインストールは行わない。

```powershell
if (-not (Test-Path ".\.venv\Scripts\python.exe")) { py -3 -m venv .venv }
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m playwright install chromium
```

既存のChromiumを `out/playwright-browsers` に配置済みの場合は、代わりにその場所を利用できる。例：`$env:PLAYWRIGHT_BROWSERS_PATH = (Resolve-Path .\out\playwright-browsers).Path`。**ブラウザのインストール先と実行時のパスを一致させる。**

ログイン情報の値を表示せず、必要な設定が解決できるかだけ確認する：

```powershell
.\.venv\Scripts\python.exe -c "from src.knowledge_upload_probe import load_login_config; c=load_login_config(); b=c['browser']; assert all(isinstance(b.get(k), int) and b[k]>0 for k in ('browser_timeout_ms','page_timeout_ms')); print('LOCAL_LOGIN_CONFIG=READY')"
```

`LOCAL_LOGIN_CONFIG=READY` が出なければ**そこで停止**。例外や環境設定の値をそのままチャット・Issueへ貼らない。リポジトリの既存の環境設定を現地で確認する。

オフライン回帰テスト（本番サービスに接続しない）：

```powershell
.\.venv\Scripts\python.exe -m pytest tests/unit/test_knowledge_upload_probe.py tests/unit/test_login_wait_csp.py -q
```

テストが失敗した場合は実機UI観測を始めず、まず非機密の失敗概要だけ整理する。

## 4. UI観測の起動（ここまで自動、以降は人の目で確認）

```powershell
.\.venv\Scripts\python.exe scripts/knowledge_upload_probe.py data/knowledge_upload/synthetic.md --synthetic --inspect-ui
```

1. スクリプトが**変更されていない同梱の合成Markdown**を検証し、必要なら同じバイト列の `synthetic.txt` を作る。異なる内容の既存 `.txt` は上書きしない。
2. Chromiumが可視画面で起動し、既存の `LoginPage` で自動ログインする。成功後は `Login completed. Inspect registration navigation in Playwright Inspector.` と表示され、`page.pause()` で止まる。
3. Inspector / ブラウザの要素選択・開発者ツールを使い、**プライベートナレッジ登録画面までの実際のメニュー操作**を調べる。チャットを選ぶ操作と登録画面の導線は別物として観測する。
4. 登録画面の各コントロールについて、role、アクセス可能な表示名、経路の形、ファイル選択欄の `type` / `accept` / `multiple`、所属フォーム、登録トリガーの見た目、説明文を確認する。**推測でCSSやXPathを作らない。**
5. **ファイルを選択しない。** 保存・登録・削除・既存ファイル置換・チャット送信・リクエスト再送はしない。ファイル選択で即送信されるかは未検証なら「不明」と記録する。
6. Inspectorを再開・閉じ、Chromiumを終了する。実装上、画面観測を正常に終えてもプログラムの終了コードは `2`（アップロード未実装）であり、**終了コードだけでログイン失敗と判断しない**。失敗時は `Stopped: ...` が出る。

## 5. 必要最小限の観測記録（公開可能な情報だけ）

元のスクリーンショット／DOM全文／開発者ツールのNetwork情報はローカル内だけで扱う。必要なら無関係な文字・氏名・アカウント・識別子を**削除した断片**のみ共有する。ローカル資料の保存先は無視対象 `logs/` とし、Gitへ追加しない。

```text
観測日時（JST）:
Git HEAD（短縮値）:
実行したモード: --synthetic --inspect-ui
ログイン完了: はい / いいえ
Inspectorで停止: はい / いいえ
登録画面へ到達: はい / いいえ
画面経路: （個人IDやトークンを除いたパスの「形」）
導線（順序）:
  1) role= / 表示名= （個人情報は伏せる）
  2) role= / 表示名=
ファイル欄: type= / accept= / multiple= / 所属フォーム=
登録ボタンのroleと表示名:
ファイル選択で即送信されるか: 不明（選択しないため原則不明）
エラーや差分: （非機密の要旨のみ）
未確認事項:
```

登録導線、関連するボタン／ファイル欄が存在しない場合、URLだけ変わってフォームが表示されない場合、または認証・権限エラーの場合は**そこで停止**。存在しないDOMを補完しない。

## 6. 次のゲート

この観測で「操作した事実とサニタイズ済みの一次情報」を揃えてから、登録専用PageObjectと**合成ファイル1件**の選択・HTTP受理・一覧登録・検索反映を段階的に設計する。アップロード承認、最終 `UPLOAD` 入力、同名更新／置換、Ready化・マージ、実データ送信は**今回の観測に含めない**。
