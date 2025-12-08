# Design_logging_v0.1  

gov-llm-e2e-testkit — テストログ仕様書  
バージョン: v0.1  
最終更新: 2025-12-07

---

## 1. 目的（Purpose）

本書は gov-llm-e2e-testkit における  
**テストログ（logs/YYYYMMDD/caseID.md）標準フォーマットの正式仕様**  
を定義する。

ログは次の要件を満たす：

- LLM テストの合否根拠を再現できる  
- Basic / Advanced の両方に対応  
- INTERNET / LGWAN の環境差を吸収  
- 機械解析可能（frontmatter + Markdown）  
- 人間が読みやすい  
- CI / ローカルで同一フォーマット  

---

## 2. ログファイル配置規約

### 2.1 ディレクトリ構成

```text
logs/
YYYYMMDD/
RAG_BASIC_001.md
RAG_ADV_002.md
SMOKE_001.md
assets/
YYYYMMDD/
RAG_BASIC_001/
screenshot.png
dom.html
```

### 2.2 命名規則
- caseID.md（例：`RAG_BASIC_001.md`）  
- 1ケース = 1ファイル  
- 画像や DOM snapshot は assets/ 内の caseID ディレクトリに格納

---

## 3. ログファイルの構造（固定）

ログファイルは **必ず次の順序で構成**する。

```text
---

case_id: RAG_BASIC_001
test_type: basic        # smoke / basic / advanced
environment: internet   # or lgwan
timestamp: 2025-12-07T23:30:00+09:00
browser_timeout_ms: 15000
page_timeout_ms: 15000
----------------------

## 1. Test Summary

（成功 / 失敗、簡単な概要）

## 2. Input

* question: "条例の施行日を教えてください"

## 3. Output

```
```text
(実際のモデル出力)
```

```
## 4. Expected

- keywords:
    - "施行日"
    - "平成"

## 5. Result

- status: PASS or FAIL
- missing_keywords:
    - ...
- unexpected_words:
    - ...

## 6. Details（advanced のみ）

- 判定ロジックの説明
- 差分ハイライト
- 抽出根拠

## 7. Artifacts

- screenshot: assets/YYYYMMDD/RAG_BASIC_001/screenshot.png
- dom_snapshot: assets/YYYYMMDD/RAG_BASIC_001/dom.html

## 8. Metadata

- browser: chromium
- env_profile: internet
- exec_time_ms: 3200
```

---

## 4. Basic / Advanced の差分

| セクション       | Basic | Advanced  |
| ----------- | ----- | --------- |
| frontmatter | 〇     | 〇         |
| Summary     | 〇     | 〇         |
| Input       | 〇     | 〇         |
| Output      | 〇     | 〇         |
| Expected    | 〇     | 〇         |
| Result      | 〇     | 〇         |
| Details     | ×     | 〇（深層判定結果） |
| Artifacts   | 〇     | 〇         |

Advanced は Basic の superset。

---

## 5. スクリーンショット／DOM 保存仕様

### 5.1 保存場所

```text
logs/assets/YYYYMMDD/{case_id}/
```

### 5.2 ファイル名

- screenshot.png
- dom.html

### 5.3 保存タイミング

- FAIL のとき必須
- PASS は任意（v0.2で CI の設定と連動予定）

---

## 6. CI（e2e.yml）との責務境界

CI は以下のみを行う：

- pytest の exit code を確認
- FAIL のとき artifacts をアップロード
- ログ内容そのものには介入しない（pytest 側の責務）

---

## 7. 今後の拡張（v0.2 / v1.0）

| 版    | 機能                                 |
| ---- | ---------------------------------- |
| v0.2 | 差分ハイライト（HTML比較）自動生成                |
| v0.2 | JSON 形式ログの自動併産（解析ツール向け）            |
| v0.2 | screenshot をベースに自動黒塗り（庁内向け）        |
| v1.0 | Obsidian / Doccano / DataLake への直結 |

---

## 8. まとめ

Design_logging_v0.1 は gov-llm-e2e-testkit の
**結果再現性・監査性・解析性を保証する標準ログ仕様**である。

この形式に従う限り、INTERNET / LGWAN、Basic / Advanced、
Smoke / RAG いずれの実行でも統一したログ資産が残る。

以上を v0.1 として正式採用する。

---

