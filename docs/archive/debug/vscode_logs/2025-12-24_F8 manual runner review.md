---
date: 2025-12-24
source: vscode-chat
context: F8 manual runner review
related:
- scripts/run_f8_set1_manual.py
- tests/conftest.py
- src/execution/run_f8_set1.py
---
【VS CODE 作業要約】

1.実施したこと（事実）

- run_f8_set1_manual.py を読み、conftest.py の ChatPage 手順および run_f8_set1.py のシグネチャ・挙動と突き合わせて確認した。
- 必須メタデータ（qommons_config/execution）の明示有無と結果出力形式を確認した。
- 設計逸脱がないことを確認したためコード変更は行っていない。

2. 観測された問題／なかった問題

- 問題なし: ChatPage 生成手順が LoginPage.open/login → ChatSelectPage.open_ai → ChatPage の順で、conftest.py と一致 (run_f8_set1_manual.py、conftest.py).
- 問題なし: run_f8_set1 呼び出しが必須引数をすべて指定し、qommons_config に model/web_search/region/ui_mode、execution に retry/temperature/max_tokens が明示されており、writer の必須キー要件を満たす (run_f8_set1_manual.py, run_f8_set1.py).
- 問題なし: 実行結果表示は question_id と OK/ERR とエラー文字列のみで評価・整形を追加していない (run_f8_set1_manual.py).
- 問題なし: run_f8_set1 の break-on-error 動作を変更しておらず、失敗時は outcomes 記録後に中断する設計がそのまま (run_f8_set1.py 呼び出し部).

3.判断した点（理由つき）

- 変更不要と判断: 手動スクリプトは pytest 依存なしで単独実行可能な構成であり、必須メタデータを明示して runner/writer の責務境界を崩していないため、現行のままでブリーフ要件を満たすと判断した。

4.判断を保留した点

- run_id/ordinance_id/model/max_tokens/headless などパラメータの正規値や命名規約は未FIXのまま現行値を維持している（ブリーフで保留扱い）。
- conftest.py が行う MissingSecret への CI fallback を手動スクリプトでは実装していない点について統一要否を未判断。

5.次に Web版で裁定してほしい論点

- 手動スクリプトで load_env 失敗時に conftest.py 同様の CI fallback（環境変数補完）を行うかどうか。
- run_id/ordinance_id/model/max_tokens/headless など手動実行時のデフォルト値・命名規約をどこまで規定するか。