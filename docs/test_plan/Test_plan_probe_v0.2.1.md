# 📘 **docs/Test_plan_probe_v0.2.1.md**

（**正式版 / 保存用**）

# Test Plan — probe v0.2.1  
**Version:** v0.2.1  
**Status:** Stable  
**Location:** `sandbox/probe_v0_2.py`

---

## 1. Purpose（目的）

本書は、Answer Detection Layer の基盤である  
**probe v0.2.1（GraphQL createData 監視ツール）**  
の品質を保証するための **正式テスト計画**である。

probe の役割：
- GraphQL *createData* を **回答確定イベント**として観測する  
- REST `/messages` との同期点を記録する  
- ChatPage.ask v0.6 の設計根拠となる一次情報を提供する  
- CI に属さない **sandbox 専用ツール**として動作する

本 Test Plan に準拠した検証により、  
**仕様準拠・後方互換性・揺らぎ耐性**が担保される。

---

## 2. Scope（対象範囲）

対象ファイル：

```
sandbox/probe_v0_2.py   # probe v0.2.1 本体
```

対象外：

- ChatPage.ask  
- LoginPage  
- CI (GitHub Actions)  
- DOM 依存の回答検知

---

## 3. References（参照資料）

- Design_chat_answer_detection_v0.1  
- Design_probe_graphql_answer_detection_v0.1  
- PROJECT_STATUS v0.4.4  
- Debugging_Principles v0.2  
- PROJECT_GRAND_RULES v4.2

---

## 4. Test Objectives（テスト目的）

probe v0.2.1 が次の要件を満たすことを確認する：

1. GraphQL *createData* を正確に検知できる  
2. createData が存在しない場合は `status = "no_graphql"` を返す  
3. GraphQL → REST の回答抽出が整合している  
4. chat_id によるフィルタリングが誤検知ゼロである  
5. JSON parse 不能レスポンスが判定に影響しない  
6. POST → createData → GET の **時系列順序**を保持する  
7. summary.json が **スキーマ凍結（Schema Freeze）**に従う  
8. 負荷・順序揺らぎ・遅延に対して安定動作する  

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

- `_extract_graphql_answer(raw)`
- `_extract_rest_answer(raw)`
- `_extract_chat_id_from_sk(sk)`

確認観点：

- `"assistant#本文"` を正しく抽出  
- プレフィックス揺らぎ（`Assistant#...`）への耐性  
- content が None / 非文字列  
- REST messages[*].role=="assistant" の正規抽出  
- sk → chat_id の抽出（正常系／異常系）  

---

### A-2. summary.json ロジック検証

モックイベントを用いて以下を確認：

- status == "ok"  
- status == "no_graphql"  
- status == "mismatch_with_rest"  
- status == "incomplete"  
- first_graphql_ts の正当性  
- has_post / has_get / has_graphql の判定  

---

### A-3. イベント種別の分類

URL・method に応じて：

- GraphQL → `"graphql"`  
- POST /messages → `"rest_post"`  
- GET /messages → `"rest_get"`  
- その他 → `"other"`

が正しく分類されること。

---

## 7. Layer B：Real Browser Test（実ブラウザテスト）

### B-1. createData 正常検知テスト

手順：

1. `template_prepare_chat_v0_1.py` で page / chat_id を準備  
2. probe を 30 秒実行  
3. `summary.json` の次を確認：
   - has_graphql == true  
   - graphql_answer != None  
   - rest_answer != None  
   - status == "ok"  

---

### B-2. createData の時系列確認（最重要）

POST → createData → GET の順序が保持されていること：

1. events[0] が POST  
2. 次が GraphQL (createData)  
3. その後 GET /messages  
4. first_graphql_ts が GraphQL と一致  

---

### B-3. 複数 createData の扱い

複数の createData が存在しても：

- graphql_answer は **最初の 1 回**から抽出  
- summary の first_graphql_ts と一致

---

### B-4. chat_id フィルタリング強度テスト

次のすべてで **混入ゼロ**を確認：

1. 他チャットを別タブで開く  
2. 別アカウントのチャットを開く  
3. “似た URL” の XHR（部分一致誤検知）  
4. 背景の polling / updateMessages  

---

### B-5. JSON parse 不能の影響テスト

- parse_error=True のイベントが存在しても  
  - status  
  - has_graphql  
  - graphql_answer  
に影響しないこと。

---

## 8. Layer C：耐性テスト（Stress / Negative）

### C-1. createData の Negative Test（必須）

方法：質問送信せず probe を起動、または capture_seconds=1 にする。

期待結果：

```
status == "no_graphql"
graphql_answer == None
rest_answer == None

```

---

### C-2. REST の遅延耐性（incomplete 判定）

- GraphQL は来るが GET /messages が遅れるケース  
- summary.status == "incomplete" を確認

---

### C-3. 時系列逆転の耐性

POST → GET → GraphQL の順序でも：

- 例外を出さない  
- status が mismatch/incomplete になる  

---

### C-4. 高負荷イベントの耐性

- capture_seconds=60  
- 入力を連打して大量 XHR を発生させる  
- jsonl / summary が破損しないことを確認

---

## 9. Success Criteria（合格基準）

以下をすべて満たした場合、probe v0.2.1 は “仕様準拠” と判定する。

1. GraphQL createData を正確に検知  
2. createData が無い場合は no_graphql  
3. GraphQL / REST の回答が整合（正常系）  
4. chat_id フィルタリング混入ゼロ  
5. JSON parse 不能が判定に影響しない  
6. 時系列順序が保持される  
7. summary.json が **スキーマ完全一致（増減なし）**  
8. 例外発生ゼロ  

---

## 10. Test Execution Procedure（運用手順）

```
(1) git pull
(2) python -m sandbox.run_probe_once
(3) sandbox/xhr_probe_yyyyMMdd_HHmmss/ を確認
(4) summary.json → 本 Test Plan の観点で評価
(5) ChatPage.ask v0.6 の設計へ反映

```

---

## 11. Notes（補足）

- probe は **sandbox 専用**であり CI 上では実行しない  
- 本 Test Plan は probe の後方互換性を保証するための基準文書  
- Test Plan の更新は **設計書変更時のみ**発生する  

---

## 12. Revision History

| Version | Date | Description |
|---------|------|-------------|
| v0.2.1 | 2025-12 | 初版（不足点レビューに基づく完全版） |

---
