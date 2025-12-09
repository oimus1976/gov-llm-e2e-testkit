# PROJECT_STATUS — gov-llm-e2e-testkit
バージョン: **v0.2.1**  
最終更新日: 2025-12-09  
管理レイヤ: Execution Layer（実行制御）

本書は gov-llm-e2e-testkit の「現在地・進行中タスク・次のアクション」を統一的に管理する  
**単一の最新状態（Single Source of Truth）**である。

---

## 1. プロジェクト目的（Mission）
- Qommons.AI（INTERNET / LGWAN）に対する **完全自動 E2E テスト基盤**を確立する。
- Playwright（Sync）・pytest（v0.2）・PageObject（v0.2）・env_loader・log_writer を  
  統合した **分離可能で再利用性の高い OSS テストキット**を実現する。
- LGWAN 環境の offline 要求を満たすため、  
  **外部依存ゼロ・ログ完全保存・再現性100%** を確保する。

---

## 2. 現在地（Where We Stand）
### ✔ 完了済み（v0.2.0〜v0.2.1）
- Playwright Async → Sync へ正式移行、UI安定性が大幅改善
- PageObject v0.2（BasePage / LoginPage）
- pytest Execution Layer v0.2（case_dirs, evidence_dir, Sync統合）
- Debugging Principles v0.1 の策定
- **Design_env_v0.2 の策定（← v0.2.1 の主要成果）**  
  - env.yaml / .env / 環境変数の三層構造を正式定義  
  - `.env.<profile>` 切り替え方式の導入  
  - MissingSecretError の導入仕様を確立
- OSSユーザー向けの導入 UX を改善（.env 方式へ移行準備完了）

### ✔ 安定稼働中
- test_smoke_v0.2（Sync Playwright）
- LogContext / log_writer v0.1（frontmatter + セクション構造）

---

## 3. 未完了タスク（Backlog）
- ChatPage Sync 実装 v0.2（UI要素の変動吸収 + evidence_dir 標準化）
- RAG Basic / Advanced の Sync Playwright 対応
- CI（e2e.yml）の artifacts 改修（v0.2仕様に追従）
- pytest strict/lenient 切り替えモード
- retry_policy の導入（ページ遷移タイムアウト吸収）

---

## 4. リスク・懸念点（Risk Log）
- ChatPage の UI 変動が頻発するため、Locator_Guide の fallback 設計が必須  
- env_loader が実装前のため、LGWAN/internet 切替テストがまだ安定しない  
- evidence_dir の運用ルールが暫定のまま（整備予定）  
- CI（headless=True）で Sync 時間差が発生する可能性あり

---

## 5. 本日の主要成果（v0.2.1）
- **環境レイヤの設計再構築（Design_env_v0.2）を正式採用**
- OSS としての導入のしやすさ（dotenv）と  
  多環境（INTERNET / LGWAN / CI）での安全運用が両立する基盤を確立
- env_loader v0.2 の仕様が揺るぎない状態になった  
  → これにより PageObject / pytest / CI レイヤが安定して依存できる

---

## 6. 次の最重要アクション（Next Action）
### 🔥 **優先度トップ（v0.2.2 に向けて）**
1. **env_loader v0.2 実装（Design_env_v0.2 に準拠）**  
   - dotenv 読み込み（.env → .env.<profile>）  
   - MissingSecretError  
   - 既存環境変数方式との後方互換  
   - プロファイル切り替えロジックの実装

2. `.env.sample` / `.env.internet.sample` の追加  
   - OSSユーザーがコピペで導入できるようにする

3. README の Quick Start を「dotenv 前提」に刷新

---

## 7. 中期アクション（v0.2.x 系）
- ChatPage Sync v0.2 完全実装  
- evidence_dir の標準構造化  
- retry_policy の導入  
- strict/lenient の2モード運用  
- CI（e2e.yml）で HTML / screenshot / metadata を完全保存

---

## 8. 長期アクション（v0.3 以降）
- RAG Basic / Advanced の安定化  
- LGWAN 実運用向けの “full offline mode test pipeline” 完成  
- ChatPage の UI 変動吸収アルゴリズムの強化  
- Visual Regression Test（将来）

---

## 9. 必須資料リスト（Reference Docs）
- Design_env_v0.2.md（NEW）  
- Design_pytest_v0.2  
- Design_BasePage_v0.2  
- Design_LoginPage_v0.2  
- Design_ChatPage_v0.2  
- Locator_Guide_v0.2  
- Debugging_Principles_v0.1  
- Design_playwright_v0.1  

---

（END OF PROJECT_STATUS v0.2.1）
