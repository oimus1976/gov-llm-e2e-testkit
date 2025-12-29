# Responsibility Map v0.1  

gov-llm-e2e-testkit — コンポーネント責務マップ  
バージョン: v0.1  
最終更新: 2025-12-07

本書は gov-llm-e2e-testkit における **全コンポーネントの責務境界（Responsibility Boundaries）** を定義する。  
本マップは、設計・実装・CI・テストの整合性を保ち、役割の衝突や重複を防ぐための上位レイヤ文書である。

---

## 1. 全体構造

本プロジェクトは次の 4 層で構成される。

1. **Environment Layer（env.yaml / env_loader）**  
2. **Execution Layer（pytest / conftest / browser/context/page）**  
3. **PageObject Layer（BasePage / LoginPage / ChatPage）**  
4. **Application Test Layer（Smoke / Basic RAG / Advanced RAG）**

この4層が責務を分担し、疎結合で動作することを保証する。

---

## 2. 各レイヤの責務一覧

---

### 2.1 Environment Layer  

#### （env.yaml / env_loader.py）

**責務：**

- INTERNET / LGWAN のプロファイル管理  
- URL / 認証情報の placeholder 定義  
- ブラウザ timeout（browser/page_timeout）の環境別管理  
- プロジェクト全体の環境変数の唯一の定義場所  
- ENV_PROFILE によるプロファイル切替機構の提供  

**非責務（やってはいけない）：**

- ブラウザの起動  
- ログイン処理  
- UI 操作  
- RAG 検証ロジック  
- pytest 実行順序の制御

---

### 2.2 Execution Layer  

#### （pytest / conftest.py / playwright async）

**責務：**

- Playwright browser / context / page の生成  
- env_loader に基づく timeout/headless の適用  
- page に対する default timeout の注入  
- PageObject へ page を渡す  
- CI（e2e.yml）からの “唯一の実行窓口” となる  
- Smoke → Basic → Advanced の順にテストを実行（test_plan 依存）

**非責務：**

- UI ロジック  
- HTML/RAG 検証ロジック（これは Application Test Layer）  
- URL/ユーザー名/パスワードの直書き（必ず env.yaml 経由）

---

### 2.3 PageObject Layer  

#### （BasePage / LoginPage / ChatPage）

---

#### BasePage の責務：

- locator strategies（role/label/testid/css）  
- wait / click / find / fill などの共通関数  
- 汎用的な UI 操作の抽象化

**BasePage の明確な非責務：**

- env.yaml の読み込み  
- timeout の適用  
- Browser/Context/Page の生成  
- URL 生成や遷移制御  
- RAG 検証ロジック  

---

#### LoginPage の責務：

- ログインフォーム操作（ユーザー名/パスワード入力）  
- ログイン開始・ログイン完了の検知  

**LoginPage の非責務：**

- 認証情報の保管（env_loader → pytest が持つ）  
- ページ生成  
- timeout 設定  

---

#### ChatPage の責務：

- チャット送信 / 返信取得  
- 送信ボタンの locator 選択  
- 出力部分の抽象化（response_text を返す等）

**ChatPage の非責務：**

- RAG 検証  
- YAML ケースの読み込み  
- ブラウザ起動  
- 環境設定の取り扱い

---

### 2.4 Application Test Layer  

#### （Smoke / RAG Basic / RAG Advanced）

**責務：**

- RAG YAML（data/rag/*.yaml）の読み込み  
- case の展開  
- ChatPage を使った API/LLM の問合せ  
- expected との比較（RAG Basic）  
- strict モードでの深層検証（RAG Advanced）

**非責務：**

- env.yaml の管理  
- UI locator  
- PageObject の内部仕様  
- ログインフローの定義（LoginPage に委譲する）

---

## 3. 各レイヤ間の責務境界図（ASCII）

```

[ env.yaml ] ----> [ env_loader ]
|                 |
|             provides config
v                 v
---------------------------------------

| Execution Layer (pytest + conftest) |
| - browser/context/page generation   |
| - timeout injection                 |



               |
               | inject page
               v
 -----------------------------------
 |      PageObject Layer           |
 | BasePage / LoginPage / ChatPage |
 -----------------------------------
               |
               | use(PO)
               v
 -----------------------------------
 | Application Test Layer          |
 | smoke / rag_basic / rag_adv     |
 -----------------------------------
```

---

## 4. トレース例：RAG Basic 実行時の責務フロー

1. pytest が env.yaml を読み込む（env_loader）  
2. browser/context/page を作成し、timeout を適用  
3. LoginPage → ChatPage を生成（page は pytest から渡される）  
4. RAG YAML を読み込み、case を展開  
5. ChatPage.send() を呼び出し、LLM 応答を取得  
6. expected と比較し判定  
7. CI は pytest の exit code を受け取るだけ

**責務の重複ゼロ。**

---

## 5. 本マップの目的

- 誤提案（BasePage に env_loader を入れる等）の防止  
- 設計書 / 実装 / pytest / CI の全整合性の確保  
- 今後の機能追加（v0.2/v1.0）で“どこを触るべきか”を迷わない構造づくり  
- 大規模テスト基盤としての長期保守性向上

---

## 6. 今後の拡張

- Responsibility Map v0.2：LGWAN 専用モード / retry_policy の責務追加  
- Responsibility Map v1.0：マルチテナント / マルチエージェント責務を追加

---

## 7. まとめ

Responsibility Map v0.1 により、  
gov-llm-e2e-testkit の **全コンポーネントの責務境界が正式確定**した。

このマップはすべての設計（pytest / env_loader / PageObject / CI）の  
基準となる最上位ドキュメントであり、今後の機能追加における  
中心的な参照点となる。

以上を v0.1 として正式に採用する。

---
