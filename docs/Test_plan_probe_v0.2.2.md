# Test Plan — probe v0.2.2

**Version:** v0.2.2
**Status:** Stable
**Location:** `scripts/probe_v0_2.py`

---

## 1. Purpose（目的）

本書は、Answer Detection Layer の基盤である
**probe v0.2.2（REST `/messages` を primary とする回答検知ツール）**
の品質を保証するための **正式テスト計画**である。

probe の役割：

* REST `/messages` を **一次的な回答確定イベント**として観測する
* GraphQL *createData* を **補助的な検証経路**として記録する
* 両経路の時系列・整合性を一次情報として保存する
* ChatPage.ask v0.6 の設計根拠となる事実データを提供する
* CI に属さない **手動実行ツール（scripts 配下）**として動作する

本 Test Plan に準拠した検証により、
**仕様準拠・後方互換性・揺らぎ耐性**が担保される。

---

## 2. Scope（対象範囲）

対象ファイル：

```text
scripts/probe_v0_2.py   # probe v0.2.2 本体
```

対象外：

* ChatPage.ask
* LoginPage
* CI（GitHub Actions）
* DOM 依存の回答検知

---

## 3. References（参照資料）

* Design_chat_answer_detection_v0.1
* Design_probe_graphql_answer_detection_v0.2
* PROJECT_STATUS v0.4.5
* Debugging_Principles v0.2
* PROJECT_GRAND_RULES v4.2

---

## 4. Test Objectives（テスト目的）

probe v0.2.2 が次の要件を満たすことを確認する。

1. REST `/messages` から **assistant の最終回答**を正確に抽出できる
2. GraphQL *createData* を検知できる場合は補助情報として記録できる
3. GraphQL が存在しない場合でも **REST-only で完了判定**できる
4. chat_id によるフィルタリングが誤検知ゼロである
5. JSON parse 不能レスポンスが判定に影響しない
6. POST →（GraphQL）→ GET の **時系列順序**を保持する
7. summary.json が **スキーマ凍結（Schema Freeze）**に従う
8. 遅延・揺らぎ・長文生成に対して安定動作する

---

## 5. Test Layers（テスト体系）

本テスト計画は次の 3 層で構成される。

### **Layer A — 単体テスト（Static / Logic）**

コード内部の純粋なロジックを検証する。

### **Layer B — 実ブラウザテスト（Real Browser）**

Playwright + Qommons.AI の実通信を観測する。

### **Layer C — 耐性 / 例外テスト（Stress / Negative）**

揺らぎ・遅延・順序乱れなど、現実に起こりうる異常系を検証する。

---

## 6. Layer A：Unit Tests（単体テスト）

### A-1. 回答抽出関数の検証

対象関数：

* `_extract_graphql_answer(raw)`
* `_extract_rest_answer(raw)`
* `_extract_chat_id_from_sk(sk)`

確認観点：

* REST `data.messages[*].role == "assistant"` の正規抽出
* `assistant.content` が文字列として取得できる
* content が None / 非文字列の場合は None を返す
* GraphQL `assistant#` プレフィックス揺らぎへの耐性
* sk → chat_id 抽出（正常系／異常系）

---

### A-2. summary.json ロジック検証

モックイベントを用いて以下を確認する。

* status == `"ok"`
* status == `"no_graphql"`
* status == `"mismatch_with_rest"`
* status == `"incomplete"`
* first_graphql_ts の正当性
* has_post / has_get / has_graphql の判定

---

### A-3. イベント種別の分類

URL・method に応じて次が正しく分類されること。

* GraphQL → `"graphql"`
* POST /messages → `"rest_post"`
* GET /messages → `"rest_get"`
* その他 → `"other"`

---

## 7. Layer B：Real Browser Test（実ブラウザテスト）

### B-0. REST-only 正常系（最重要）

条件：

* 長文・制約付き質問
* capture_seconds = 90

期待結果：

* has_get == true
* rest_answer != None
* status == `"no_graphql"`
* UI 表示内容と rest_answer が一致

---

### B-1. GraphQL createData 正常検知（補助経路）

条件：

* createData が発火する質問文
* capture_seconds = 30〜60

期待結果：

* has_graphql == true
* graphql_answer != None
* rest_answer != None
* status == `"ok"`

---

### B-2. createData の時系列確認

POST →（GraphQL）→ GET の順序が保持されていること。

* events の順序が逆転しない
* first_graphql_ts が最初の GraphQL と一致

---

### B-3. 複数 createData の扱い

* graphql_answer は **最初の 1 回**から抽出
* first_graphql_ts と一致

---

### B-4. chat_id フィルタリング強度テスト

次のすべてで **混入ゼロ**を確認する。

1. 他チャットを別タブで開く
2. 別アカウントのチャットを開く
3. “似た URL” の XHR（部分一致誤検知）
4. 背景の polling / updateMessages

---

### B-5. JSON parse 不能レスポンスの影響

* parse_error == true のイベントが存在しても

  * status
  * has_graphql
  * graphql_answer
  * rest_answer
    に影響しないこと。

---

## 8. Layer C：耐性テスト（Stress / Negative）

### C-1. GraphQL 非存在ケース（必須）

条件：

* createData が発火しない質問
* capture_seconds = 30

期待結果：

```text
status == "no_graphql"
graphql_answer == None
rest_answer == None または取得済み
```

---

### C-2. REST 遅延ケース

* GraphQL は来るが GET /messages が遅延

期待結果：

* status == `"incomplete"`
* 例外が発生しない

---

### C-3. 時系列逆転の耐性

POST → GET → GraphQL の順序でも：

* 例外を出さない
* status が mismatch / incomplete になる

---

### C-4. 高負荷イベント耐性

条件：

* capture_seconds = 60〜120
* 大量 XHR を発生させる

期待結果：

* jsonl / summary が破損しない

---

## 9. Success Criteria（合格基準）

以下をすべて満たした場合、probe v0.2.2 は **仕様準拠**と判定する。

1. REST `/messages` で意味的完了を検知できる
2. GraphQL 非存在でも完了判定できる
3. GraphQL が存在する場合は補助情報として整合
4. chat_id 混入ゼロ
5. JSON parse 不能が判定に影響しない
6. 時系列順序が保持される
7. summary.json が **スキーマ完全一致（増減なし）**
8. 例外発生ゼロ

---

## 10. Test Execution Procedure（運用手順）

```Bash
(1) git pull
(2) python -m scripts.run_probe_once [--seconds 30 | 90]
(3) scripts/xhr_probe_yyyyMMdd_HHmmss/ を確認
(4) summary.json を本 Test Plan の観点で評価
(5) ChatPage.ask v0.6 設計へ反映
```

---

## 11. Notes（補足）

* probe は **CI 非対象の手動実行ツール**である
* seconds は **完了条件ではなく fallback timeout**である
* 本 Test Plan は probe の後方互換性を保証する基準文書である
* Test Plan の更新は **設計変更または実測事実確定時のみ**行う

---

## 12. Revision History

| Version | Date    | Description               |
| ------- | ------- | ------------------------- |
| v0.2.1  | 2025-12 | 初版（完全版）                   |
| v0.2.2  | 2025-12 | REST primary 確定・実測（90秒）反映 |

---
