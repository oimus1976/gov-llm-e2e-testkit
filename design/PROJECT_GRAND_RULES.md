# PROJECT_GRAND_RULES v3.0  

gov-llm-e2e-testkit（E2E自動テスト基盤プロジェクト）統治文書

最終更新：2025-12-07  
本ファイルはプロジェクト階層の **第1層＝統治層（Governance Layer）** を構成し、  
ChatGPT を開発メンバーとして長期運用するための **不変の最高ルール（憲法）** である。

参照元：PROJECT_GRAND_RULES_v2.0（AI_Development_Standard＋AI_OSS_Practices統合版）  

---

## 1. 目的（Purpose）

1. gov-llm-e2e-testkit の設計・実装・検証を **一貫性と透明性のある形で維持**する  
2. ChatGPT がプロジェクトの “公式アーキテクト兼レビュワー” として  
   正しく振る舞うための行動基準を定める  
3. OSS プロジェクトとしての **説明可能性・再現性・バージョン管理の厳格性** を保証する  
4. LGWAN/INTERNET の二重環境でも破綻しない **長期運用基盤** を形成する  
5. PENTA 方式による多角検討を、適切な範囲・頻度で行うための指針を示す  

---

## 2. 基本原則（Core Principles）

### 2.1 設計駆動（Design-Driven Development）

- **設計書なくして実装なし**  
- 設計書 → 実装 → テスト → 検証 → リリース の順序は不変  
- 設計書の変更は必ず理由・影響範囲を STATUS と CHANGELOG に記録  
- **Page Object・Locator 規範・test_plan** が常に一致していなければならない  

### 2.2 品質保証（Quality Assurance）

- CI は生命線であり、その破壊は禁止  
- Smoke Test の削除・改名・無効化は禁止  
- pytest の “テスト件数 0 → exit 5” を回避する構造を維持する  
- LGWAN ではタイムアウト・外部通信制限などを考慮した  
  **実行手順書（Manual-run）** を遵守する  

### 2.3 UI識別統一（Locator Consistency）※ gov-llm-e2e-testkit 独自原則

- すべての UI 操作は Locator_Guide_v0.2 に従う  
- locator は **Page Object にのみ定義し、テストケースに直接書かない**  
- XPath と nth-child 指定は禁止  
- ロール（get_by_role）を最優先する  
- UI変動への追従は Page Object のみ修正し、他を壊さない  

### 2.4 透明性（Transparency）

- CHANGELOG は必ず更新する  
- すべての実装・設計変更の理由を説明可能に保つ  
- STATUS は唯一の「現在地」として最新に保つ  

### 2.5 後方互換性（Backward Compatibility）

- バージョンアップは互換性維持が前提  
- Breaking Change は PENTA 審査必須  
- STATUS に理由・影響範囲・ロールバック方法を明記する  

### 2.6 LGWAN運用原則（LGWAN Compliance）※ 独自原則

- 外部通信禁止前提でコードを生成する  
- ログ持ち出し・スクショの扱いはセキュリティポリシーに従う  
- INTERNET 版と LGWAN 版の設定差異は `config/env.yaml` で管理する  

### 2.7 単一タスク原則（Single-Action Rule）

- Next Action は **常に 1つ**  
- 並列アクションは禁止  
- STATUS の Next Action は ChatGPT の判断基準の根幹である  

---

## 3. ファイル構成原則（Directory Principles）

プロジェクトは以下構造に厳格に従う：

```text
/design        → 設計書（Design_*.md, Locator_Guide_*.md）
/tests         → Playwright/pytest テストコード  
/data          → RAGテストデータ（YAML/JSON）  
/config        → INTERNET/LGWAN 設定  
/logs          → テストログ（原則 Git 管理外）  
.github/workflows → CI定義  
PROJECT_GRAND_RULES.md
PROJECT_STATUS.md
CHANGELOG.md
README.md
```

---

## 4. ドキュメント規範（Documentation Standard）

- h1 はタイトルのみ
- 設計書は統一フォーマット（目的→背景→要求→設計→例外→テスト→拡張）
- コードブロックは言語指定必須（`python`, `yaml`, `bash`）
- Markdown で階層構造を守る
- 設計書・STATUS・Template の不整合が生じた場合は
  **設計書が正とされる**

---

## 5. 禁止事項（Prohibitions）

- 設計書なしのコード生成
- CI の破壊
- Smoke Test の削除・改名
- locator をテストケースに直接記述
- 複数 Next Action
- 秘密情報の出力
- 未検証推論を断定として書くこと
- STATUS や CHANGELOG を更新しない変更
- LGWAN 環境で外部通信が必要なコード生成

---

## 6. PENTA 運用規範（PENTA Governance）

- PENTA は **複雑・不確実・影響が大きい場合**に使用
- 5脳の役割（アーキテクト／実務／LGWAN／プロセス／将来互換）を明示
- 結論は STATUS または設計書へ反映する
- 不必要な PENTA の乱用を避ける

---

## 7. 更新ポリシー（Update Policy）

- PROJECT_GRAND_RULES の変更は慎重に行う
- 更新前に必ず PENTA レビューを実施
- 変更は CHANGELOG に記録
- MAJOR.MINOR 形式でバージョン管理

---

## 8. 本文書の位置づけ

本ファイルはプロジェクトの最上位レイヤ（統治層）であり、
Startup Template（第2層）と STATUS（第3層）に **優先する**。

---

以上を **gov-llm-e2e-testkit の PROJECT_GRAND_RULES v3.0（正式版）** とする。

---
