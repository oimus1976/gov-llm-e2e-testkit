# PROJECT_STATUS v0.4.0  
gov-llm-e2e-testkit — 現在地（Single Source of Truth）

最終更新：2025-12-10  
参照 GRAND_RULES：v4.0

---

## 1. 現在地（Current Status）

本プロジェクトは、以下の 4 つの主要コンポーネントを中心に安定化フェーズへ移行している：

1. **PageObject 4層構造の確立**  
   - BasePage v0.21  
   - LoginPage v0.3  
   - ChatSelectPage v0.3  
   - ChatPage v0.5（初の安定版）  

2. **CI の改善と headless 動作の確立途中**  
   - pytest-playwright / pytest-asyncio / PYTHONPATH 設定  
   - env.yaml → env_loader v0.2 → MissingSecretError → conftest fallback  
   - Smoke Test v0.3 はローカルでは安定。CI では URL 問題は解決済み。

3. **Debugging_Principles v0.2 を正式運用開始**  
   - GRAND_RULES v4.0 に統合  
   - 「推測禁止」「一次情報必須」「再発防止」を憲法レベルへ格上げ

4. **設計書の世代交代（Design_* 最新 v0.5 シリーズの整備進行中）**  
   - Design_ChatPage_v0.5.md 追加  
   - BasePage / LoginPage / ChatSelectPage も今後 v0.3〜0.4 系へ統一予定  

---

## 2. 最新成果（成果サマリ）

- **ChatPage v0.5** が安定し、CI/ローカルとも最小 E2E が通る状態へ到達  
- **env.yaml → Secrets → conftest fallback** が動作し、CI エラー原因が完全に可視化  
- **ChatSelectPage v0.3** を正式管理下へ（import 復活も完了）  
- **GRAND_RULES v4.0** を正式に再構築し、プロジェクト統治の中核を刷新  
- **Debugging_Principles v0.2** をプロジェクト標準に格上げ  
- PROJECT_STATUS / CHANGELOG / 設計書の三位一体運用が安定してきた  

---

## 3. 未解決の課題（Open Issues）

1. **CI（GitHub Actions）での Smoke 成功率 100% ではない**  
   - headless モードでの Locator（card, chat-input 等）の安定性改善が必要  
   - ChatSelectPage と ChatPage の DOM 解析による locator 安定化（v0.6）  

2. **PageObject のバージョン整合性が v0.2〜v0.5 で混在している**  
   - 統一した PageObject 系 Design Document を作成する必要あり  

3. **RAG テスト（Basic/Advanced）は CI では未検証**  
   - Smoke が安定後に CI の二段階実行へ移行予定  

4. **sandbox ディレクトリの整理**  
   - input.html / validation script の扱いを統一すべき  

---

## 4. リスク・注意点（Risks）

- CI を壊す修正（locator 変更等）が依然高リスク  
- DOM 変動の多い Web アプリのため、locator 改修時は Design → PO → test → CI の順を厳守  
- Secrets 未設定時の fallback はあくまで CI 用であり、本番動作を保証しない  
- Debugging 原則に違反（推測ベース修正 / import 削除系修正）は再発率が跳ね上がる  

---

## 5. Next Action（単一タスク原則）

### **Next Action（v0.4.0 → v0.4.1）**  
**CI での Smoke Test の headless 完全安定化（locator 再点検・DOM 再解析）**

理由：  
- 現状の最大のボトルネックは CI 失敗  
- PageObject レイヤーの locator 安定が全後続タスクの前提  
- GRAND_RULES v4.0 のガイドラインが最初に適用されるべき領域のため  

---

## 6. 参照ドキュメント

- PROJECT_GRAND_RULES v4.0  
- Design_BasePage_v0.21  
- Design_ChatPage_v0.5  
- Design_LoginPage_v0.3  
- Design_env_v0.2  
- Debugging_Principles_v0.2  
- Design_ci_e2e_v0.1  
