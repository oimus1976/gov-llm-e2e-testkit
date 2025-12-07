# gov-llm-e2e-testkit — Test Plan v0.1  

最終更新: 2025-12-07  
参照文書：  

- PROJECT_GRAND_RULES v2.0  
- Startup Template v3.0  
- Startup Workflow v3.0  
- Design_BasePage_v0.1  
- Design_ChatPage_v0.1  
- Design_LoginPage_v0.1  
- Locator_Guide_v0.2  
- PROJECT_STATUS_v0.1.6  

---

## 1. 目的（Purpose）

本 Test Plan は、gov-llm-e2e-testkit における  
**E2E テスト体系の最上位仕様書**として、

- テストの種類  
- テスト目的  
- テストデータ仕様（YAML/JSON）  
- INTERNET / LGWAN の実行ポリシー  
- CI（e2e.yml）と Smoke Test の必須性  
- UI 変動 / モデル更新時の対応方針  

を一元的に規定する。

本書は **全テストの基準点（Single Source of Truth for Testing）** であり、  
CI・設計書・STATUS と整合しなければならない。

---

## 2. テスト体系（Test Categories）

本プロジェクトのテスト体系は以下の3層に分かれる：

1. **Smoke Test（最小動作確認）**  
2. **Basic RAG Test（キーワード一致）**  
3. **Advanced RAG Test（精度＋妥当性の高度検証）**

```text
Smoke
└─ Basic RAG
└─ Advanced RAG
```

下位テストは常に上位テストの成功を前提とする。

---

## 3. テスト種別（Test Types）

### 3.1 Smoke Test（必須・最優先）

目的：  
→ 「ログイン→質問→応答が返る」という **最小動作** を確認する。

特徴：  

- UI変動に最も強く設計  
- Page Object の正常性確認  
- CI で必ず実行  
- RAG要素は含めない  
- 失敗したら RAG は絶対に実行しない

合格条件：  

- ask("…") の応答文字列が **空でない**こと

---

### 3.2 Basic RAG Test（期待語句の一致）

目的：  
→ LLM が最低限の「正答特徴語」を応答に含むか確認。

特徴：  

- expected_keywords（AND条件）  
- ケースは YAML で管理  
- UI ではなく応答本文だけを見る  
- テキスト比較は厳密一致ではなく “含まれるか”

合格条件：  

- expected_keywords のすべてが応答本文に含まれていること

---

### 3.3 Advanced RAG Test（高度検証）

目的：  
→ 説明の妥当性・理由の整合・複合要素の検証。

特徴：  

- hierarchical expected structure  
- root / subpoints / evidence の3階層  
- 差分（diff-based）検証  
- advanced/*.yaml の構造を使用

合格条件：  

- expected_evidence 等が応答本文に一貫して含まれる  
- 誤り・矛盾がない

---

## 4. RAG ケース設計（YAML スキーマ）

### 4.1 Basic RAG（basic/*.yaml）

```yaml
case_id: Q001
input: "条例の制定手続きについて教えてください"
expected_keywords:
  - "議会"
  - "公布"
  - "施行"
strict: false   # false = 含まれるかのみ（デフォルト）
```

### 4.2 Advanced RAG（advanced/*.yaml）

```yaml
case_id: A001
input: "森林環境税の使途を説明してください"
expected:
  summary_keywords:
    - "森林"
    - "環境"
    - "保全"
  details:
    - "間伐"
    - "整備"
    - "維持管理"
  evidence:
    - "法第"
    - "根拠"
strict: true
```

---

## 5. 実行環境（INTERNET / LGWAN ポリシー）

### 5.1 INTERNET モード

- CI（GitHub Actions）で実行
- Playwrightブラウザは Actions 上で動作
- 外部通信が可能
- 標準 timeout

### 5.2 LGWAN モード

- 外部通信禁止
- テストは **手動実行のみ**
- timeout は INTERNET の 2〜3倍
- データは必ずローカル YAML のみを使用
- ログ持ち出し禁止（artifacts 生成不可）

---

## 6. CI（e2e.yml）の実行方針

CI のテスト順序は固定：

1. **Smoke Test（必須）**
2. **Basic RAG**
3. **Advanced RAG**

CI の失敗条件：

- Smoke Test が 1件でも失敗 → 全テスト stop
- Basic が1件でも失敗 → Advanced は skip
- テスト件数 0 の場合 → CI exit 5（禁止）
- Playwright のブラウザ未インストール禁止
- YAML パースエラーは即 fail

---

## 7. UI変動 / モデル更新時の再テスト方針

UI変動が発生 → 優先度順に修正：

1. Locator_Guide
2. BasePage
3. Page Object（Login / Chat）
4. Smoke Test
5. Basic RAG
6. Advanced RAG

モデル更新時 → 再走順：

1. Smoke
2. Basic
3. Advanced

---

## 8. ファイル構成（Test Assets）

```text
tests/
 ├── pages/
 │   ├── base_page.py
 │   ├── chat_page.py
 │   └── login_page.py
 │
 ├── rag/
 │   ├── basic/*.yaml
 │   └── advanced/*.yaml
 │
 └── test_smoke_llm.py

docs/
 └── test_plan/test_plan_v0.1.md
```

---

## 9. 更新ルール（STATUS / CHANGELOG）

- test_plan の更新は必ず **PENTA** を経由
- 更新時は必ず

  - PROJECT_STATUS
  - CHANGELOG
    を新バージョンへ更新する

---
