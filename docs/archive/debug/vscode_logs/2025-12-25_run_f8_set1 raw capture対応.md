---
date: 2025-12-25
source: vscode-chat
context: run_f8_set1 raw capture対応
related:
- src/execution/run_f8_set1.py
- docs/design/Design_F8_v0.3_runner.md
---
【VS CODE 作業要約】

1.実施したこと（事実）

- _capture_raw_answer_block を追加し、DOM候補を量的・構造的スコアで選択して raw_answer.html / raw_answer.txt / raw_capture_meta.json を上書きなしで保存（src/execution/run_f8_set1.py）。
- 各質問実行後に上記 raw capture をベストエフォート実行し、frontmatter に raw_capture 真偽を追加した answer.md を生成するよう変更（result_status など既存挙動は非変更）。
- run_f8_set1.py 実行で構文エラーなしを確認。

2.観測された問題／なかった問題

- ローカル実行・Playwright 挙動は未検証（UI 依存のため）。
- 現状の変更による構文エラーや型エラーは未発生。

3.判断した点（理由つき）

- スコアはテキスト長＋p/h/li 個数に重みをつけた単純合算を採用し、設計の「量的・構造的指標に基づく選択」を最小実装で満たすため。
- raw アーティファクトが既に存在する場合は保存をスキップし、上書き禁止ポリシーを守るため。
- 成否にかかわらず capture を試行し、Answer Detection とは独立した素材回収経路を常時確保する設計方針に合わせるため。

4.判断を保留した点

- 実際の UI で候補選択が適切か、及びスコア重みの妥当性は未評価。
- 既存 raw ファイルがある場合に raw_capture をどう扱うか（現状は新規保存がないため false）。

5.次に Web版で裁定してほしい論点

- 実機 UI での raw capture 結果確認とスコアリング重みの調整要否。
- 既存 raw アーティファクトがある場合の raw_capture フラグ扱いをどう定義するか。
