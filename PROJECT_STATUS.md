# ==========================================================
# PROJECT_STATUS.md   — gov-llm-e2e-testkit
# Version: v0.3.0  (2025-12-10)
# ==========================================================

## 1. プロジェクト名
gov-llm-e2e-testkit  
（自治体向け LLM サービスの自動 E2E テスト基盤）

---

## 2. 目的
- Qommons.AI に対する **ログイン → チャット利用 → 応答取得** の完全自動テストを実現する。
- 自治体環境（INTERNET / LGWAN / CI）の差異を吸収し、  
  **安定運用できる自動テスト基盤**を提供する。
- OSS として他自治体でも使えるテンプレート化を目指す。

---

## 3. 現在の進捗（Progress v0.3.0）
### ✔ ChatPage v0.5（DOM 完全対応版）を正式実装  
- id ベースの安定ロケータ（#message, #chat-send-button）に統一  
- 最新メッセージ取得を message-item-N / markdown-N に刷新  
- UI 揺らぎに強い「メッセージ件数増加検知」方式を採用

### ✔ Smoke Test v0.3 がローカル環境で **初成功**  
- ログイン → 遷移 → メッセージ送信 → 応答取得まで成功  
- PageObject・DOM 理解の根本問題がすべて解消

### ✔ Design_ChatPage_v0.5.md をドキュメント化  
- DOM 構造・ロケータ仕様・待機戦略・保守指針を正式化  
- E2E テスト基盤の中核設計が完成

### ✔ CHANGELOG v0.3.0 を更新（ChatPage / Smoke Test 大幅刷新）

---

## 4. 完了済みの成果物
- BasePage v0.2（安定動作中）
- LoginPage v0.3（sync API 完全対応）
- ChatSelectPage v0.3（任意利用モジュール化）
- ChatPage v0.5（最新 DOM 対応の正式版）
- Smoke Test v0.3（ローカルで PASS 済）
- Design_ChatPage_v0.5.md（新規作成）
- Design_env_v0.2.md（env_loader v0.2 の前提仕様）
- CHANGELOG v0.3.0 更新済

---

## 5. 未解決の課題（Open Issues）
1. **CI（GitHub Actions）で headless=True のまま Smoke Test を安定動作させる**
2. ChatSelectPage v0.3.1（UI 再設計）  
3. マルチ AI モデル対応（private / public / カスタムモデル）
4. ストリーミング応答への将来的対応（今後の UI 変更に備える）
5. ログ・DOM・スクリーンショットの CI 保存方式の標準化
6. エラー UI（LLM 応答不可時）の DOM 解析とテストケース化

---

## 6. リスク・注意点
- Qommons.AI の UI 変更が定期的に入る可能性  
  → ロケータ維持のための DOM チェック手順が必要  
- ストリーミング化が導入された場合、現行の「件数増加検知」は要改修  
- LGWAN プロファイルでのネットワーク遅延が CI・ローカルと大きく異なる  
- pytest のテスト数 0 件問題（exit code 5）は  
  Smoke Test が必ず一件実行されることで回避

---

## 7. 次の最重要アクション（Next Action 🟥）
### **▶ CI 統合（headless 成功の保証）【最優先タスク】**
- GitHub Actions（e2e.yml）の v0.3 仕様へのアップデート  
- headless=True で PASS するまで wait 条件を微調整  
- 失敗時の evidence（スクショ・DOM）を CI に保存  
- CI プロファイル環境（env_loader v0.2）との整合性確認  
- Qommons 側の DOM 変動が CI ログで即検知できる状態にする

**これが完了すると、gov-llm-e2e-testkit は  
「全国自治体で使えるレベルの安定版」に到達する。**

---

## 8. 参照すべき資料
- docs/Design_ChatPage_v0.5.md  
- docs/Design_env_v0.2.md  
- tests/pages/chat_page.py（v0.5 実装）  
- tests/test_smoke_llm.py（v0.3）  
- CHANGELOG.md（v0.3.0）  
- DOM 保存ファイル（tmp_chat_dom.html / tmp_menu_dom.html）

---

## 9. PENTA 推奨ポイント
- 複雑な DOM 解析（message-item / markdown）に PENTA を使うと強力  
- headless 動作の不安定性は  
  **「タイミング」「DOM 付与」「SPAトランジション」** の 3 種類に分類して解析  
- CI 導入はブレイン分割が有効：
  - Brain1：DOM 変動分析  
  - Brain2：ロケータ安定性  
  - Brain3：CI のタイミング  
  - Brain4：エビデンス収集設計  
  - Brain5：E2E 仕様書の整合性確認

---

# Status: **v0.3.0（CI 連携フェーズへ突入）**
