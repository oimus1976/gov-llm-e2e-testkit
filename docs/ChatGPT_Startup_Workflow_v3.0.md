# ChatGPT Startup Workflow v3.0  

gov-llm-e2e-testkit 専用（PROJECT_GRAND_RULES v3.0 ＋ Startup Template v3.0 準拠）

最終更新：2025-12-07  
本書は ChatGPT が /start 受領時・作業中に実行する  
**標準ワークフロー（行動制御プロセス）** を定める。  
本書は第2.5層＝運転層と実行層の仲立ちとして機能する。

---

## 1. 基本理念（Principles）

1. ChatGPT の内部状態を常に“正・一貫性”に保ち、  
   gov-llm-e2e-testkit の開発品質を守るための OS 手順である。  
2. PROJECT_GRAND_RULES（統治層）の遵守を最優先とし、  
   Startup Template v3.0（運転層）が規定する行動規範に従う。  
3. Playwright・UIロケータ・LGWAN 環境の制約を  
   **ワークフロー内で明示的に扱う**。

---

## 2. /start 時のブートシーケンス（Boot Sequence）

ChatGPT は /start 受領時に以下を実行する：

### 2.1 GRAND RULES のロード

- PROJECT_GRAND_RULES v3.0 をロードし、  
  すべての原則（設計書主導・後方互換性・禁止事項等）を最優先ルールとして適用。

### 2.2 Startup Template v3.0 のロード

- プロジェクト固有の行動規範・出力規範・参照文書セットを読み込む。  
- GRAND RULES と矛盾があれば GRAND RULES を優先。

### 2.3 参照文書の同期確認

- Design_playwright_v0.1.md  
- Locator_Guide_v0.2.md  
- CI 設計書（e2e.yml 予定）  
- CHANGELOG.md  
- これらの存在と整合性を軽くチェックする。

### 2.4 STATUS のロード（Single Source of Truth）

- PROJECT_STATUS.md を読み込み、  
  **Next Action を唯一の正解**として認識する。

### 2.5 Next Action の単一性検証

- STATUS の Next Action が 1つであるか確認。  
- 無い／複数 → 「Next Action 再設定フェーズ」へ移行。

### 2.6 LGWAN / INTERNET 環境の考慮

- `config/env.yaml` により環境設定を再確立。  
- LGWAN の場合：外部通信コード生成禁止を強制適用。

### 2.7 PENTA 要否判定

次の場合、PENTA を自動で提案：

- 設計書更新  
- Page Object / Locator 変動  
- UI破壊リスク  
- GRAND RULES の解釈が絡む場合  
- CI 行動の影響が大きい場合  

## 2.8 次のアクション提示

- STATUS の Next Action（必ず1つ）を ChatGPT が再提示。  
- ユーザー承認を得て作業フェーズに移行。

---

## 3. 作業フェーズ（Work Cycle）

ChatGPT は以下の順に作業する：

### 3.1 要件理解  

- ユーザーの目的を明確化  
- 必要に応じて再確認

### 3.2 参照文書の照合  

- Design_playwright  
- Locator_Guide  
- CI（e2e.yml）  
- Startup Template  
- GRAND RULES  
を参照し矛盾や抜けを確認。

### 3.3 設計書フェーズ  

- 設計書の更新案を作成する  
- Page Object の仕様変更は設計書優先とする

### 3.4 実装フェーズ  

- Playwright コード生成  
- Page Object の更新  
- ロケータ破壊を検知した場合は警告＋案内

### 3.5 テストフェーズ  

- pytest のテストコードを生成  
- Smoke → Basic → Advanced の順で提供  
- LGWAN 遅延向け timeout を調整

### 3.6 ドキュメント反映  

- PROJECT_STATUS 更新  
- CHANGELOG 更新  
- 必要に応じて Template 更新

---

## 4. 自己監査（Self-QA）

ChatGPT は作業中に常に以下を監査する：

- Locator_Guide と Page Object の一致  
- Grand Rules 違反  
- テスト件数ゼロ（CI exit 5）回避  
- LGWAN に不向きなコード生成  
- Next Action の逸脱  
- 破壊的変更の兆候  

問題があれば即停止し、修正案を提示する。

---

## 5. UI変動・モデル更新対応（Dynamic Behavior Handling）

UI変動または LLM モデル更新が疑われる場合：

1. Smoke Test を一度生成して実行  
2. ロケータ破壊を検知  
3. Page Object の修正案を提示  
4. Locator_Guide の更新要否を検討（PENTA）  
5. CI への影響確認  
6. STATUS 更新

---

## 6. LGWAN 実行フロー（Offline Mode）

LGWAN 環境では以下を上書き適用：

- 外部通信コード禁止  
- timeout（倍増）  
- スクショ・ログは内部保存のみ  
- INTERNET 向け機能（外部API利用）を無効  
- CI は INTERNET のみ実行対象  
- manual-run 手順を優先

---

## 7. 終了・再開（Exit & Resume）

### 終了時

- PROJECT_STATUS を更新  
- CHANGELOG 更新案を提示  
- 次の最小タスクを短く提示

### 再開時
- PROJECT_STATUS を再読み込みし、Next Action から再開

---

## 8. 本書の位置づけ

本 Workflow は：

- **第1層：PROJECT_GRAND_RULES（統治層）**  
- **第2層：Startup Template v3.0（運転層）**  
- **第3層：PROJECT_STATUS（実行層）**  

を結びつける **第2.5層＝行動制御プロセス** として機能する。

---

以上を **ChatGPT Startup Workflow v3.0（gov-llm-e2e-testkit 専用版）** とする。
