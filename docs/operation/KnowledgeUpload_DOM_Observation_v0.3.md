# Private Knowledge 登録コントロールの読み取り専用確認 v0.3

更新日：2026-10-09 / Issue #2 / Draft PR #1

## 1. すでに観測した事実

- ログイン後、プライベートナレッジの「マイドライブ」のURLは `/private-knowledge/my-drive`。
- 「新規」は `button` / 表示名「新規」 / `aria-haspopup="menu"`。
- 「ファイルをアップロード」は `role="menuitem"`。
- ファイル欄の観測値：`type=file`, `multiple`, `accept=".txt,.pdf,.docx,.html,.csv,.pptx,.xlsx,.md,.mp3,.wav,.png,.jpg,.jpeg"`。別の `webkitdirectory` 入力はフォルダ用。
- メニューをクリックするとWindowsファイル選択画面が開いたが、ファイルは選択していない。**選択と同時に送信されるかは不明。**
- UI根拠の原記録：[Issue #2 コメント `6073127818`](https://github.com/oimus1976/gov-llm-e2e-testkit/issues/2#issuecomment-6073127818)。

## 2. 今回は操作するのはここまで

インターネット接続できるWindows検証端末で、Draft PR #1の最新ブランチを利用する。ログイン情報は既存のローカル `.env` などで解決し、共有しない。既存の未コミット変更があれば停止し、強制切替しない。

```powershell
git status --short
git fetch origin
git switch feature/private-knowledge-upload-mvp
git merge --ff-only origin/feature/private-knowledge-upload-mvp
.\.venv\Scripts\python.exe -m pytest tests/unit/test_private_knowledge_page.py tests/unit/test_knowledge_upload_probe.py tests/unit/test_login_wait_csp.py -q
```

PythonやPlaywrightが未導入の場合は、旧版 `KnowledgeUpload_DOM_Observation_v0.2.md` のセットアップ手順を先に行う（環境と権限に応じて）。

オフラインテストがPASSしたら、**このコマンドを実行**する。

```powershell
.\.venv\Scripts\python.exe scripts/knowledge_upload_probe.py data/knowledge_upload/synthetic.md --synthetic --inspect-ui --check-observed-controls
```

起動したブラウザは自動ログインし、マイドライブのURLへ移動し、「新規」メニューだけをクリックして、DOMの必要な属性を検査する。アップロードメニュー項目は**クリックしない**。成功すると以下の表示を想定：

```text
Read-only check PASS: My Drive, New menu, upload item and file input.
No file was selected; network acceptance remains unverified.
```

その後 Playwright Inspector で一時停止する。**ファイルは選択しない。** Inspectorを再開・終了した際の終了コード `2` は既存仕様（実アップロード無効）である。

## 3. 出力結果だけ教えてください

`Read-only check PASS` が出たか、または `Stopped:` で止まったか、ブラウザがどの画面で止まったかを、機密情報を伏せて知らせる。HTML全文、`.env`、ユーザー名、パスワード、Cookie、認証済み画面の個人名を含むスクリーンショットは貼り付けない。

この確認で実際のファイル選択・HTTP受理・登録一覧・検索反映は一切保証されない。これらは次の明示的な承認後に別段階で実施する。
