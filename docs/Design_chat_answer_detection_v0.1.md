# 📘 **Design_chat_answer_detection_v0.1.md

Qommons.AI — AI回答収束検知方式の設計（案B vs 案C 統合知見）**

## 1. 目的

Qommons.AI の自動テストにおいて、
**AI の最終回答を “確実に・短時間で・誤判定なく” 取得する方法**を標準化する。

---

## 2. 確定した事実（一次情報に基づく）

### 2.1 Qommons は WebSocket を使わない

通信はすべて **HTTP（REST）＋ GraphQL（AppSync）**。

### 2.2 AI最終回答は GraphQL createData.value に格納される

jsonl 内 11行目より確認：

```
value: "assistant#<最終回答全文>"
```

### 2.3 REST GET /messages も最終回答を返す

GraphQL 保存 → REST 反映の順序。

### 2.4 DOM に流れるストリームは “途中テキスト”

最終回答判定には使用不可。

---

## 3. 検討された3案と成立可否

| 案      | 内容                              | 成立可否 | 備考                     |
| ------ | ------------------------------- | ---- | ---------------------- |
| **案1** | REST GET `/messages` を監視        | ○    | 最終回答は取れるが GraphQL より遅い |
| **案2** | **GraphQL createData を監視（最適解）** | ◎    | 最初に届く“確定回答”のソース        |
| **案3** | POST `/messages` を API で再現      | △    | 技術的には可能だがセッション再現が重い    |

---

## 4. 結論

**案2（GraphQL createData監視）を標準とする。**

理由：

* 最速かつ最確実
* 完全回答が 1イベントで到達
* DOM 監視・部分テキスト処理不要
* CI テストの安定性が最大化される

---

## 5. Sandbox テンプレ構成と現在の到達点（このスレッドで追加確定した内容）

- `template_prepare_chat_v0_1.py`
  - 責務：ログイン → チャット選択 → 1回目メッセージ送信までを **安定テンプレ** として提供する。
  - 戻り値：`page, context, chat_id`（今後の全 sandbox / probe はこれを入力とする）
  - 方針：一度動作確認した後は、検証目的の変更でテンプレ本体を壊さない（Stable Core として扱う）。

- `test_template_prepare_chat_v0_1.py`
  - 役割：テンプレートが期待どおり動作し、`chat_id` まで取得できることを確認する最小検証。

- `test_xhr_stream_probe_v0_1.py`
  - 役割：テンプレを呼び出して 1チャットを実行し、
    POST `/messages`、GraphQL `/graphql`（`createData`）、GET `/messages` のレスポンスを
    `xhr_stream.jsonl` として 30秒分記録する。
  - 現在地：1チャット内で上記3種類のイベントが揃うこと、および
    GraphQL `createData.value` に最終回答が入り、その後の GET `/messages` にも反映されることを実証済み。

---

## 6. probe v0.1 の到達点（実証結果）

* XHR/GraphQL を 30秒キャプチャ
* 以下3イベントが確実に検出された：

1. POST /messages（質問送信）
2. **GraphQL createData（最終回答）**
3. GET /messages（保存済み回答の反映）

* GraphQL の `value` と、REST GET の assistant.content が一致することを確認
* **増分ストリームは存在せず、最終回答だけが届く** ことが確定

---

## 7. probe v0.2（次に作るべきもの）

**目的：**

* GraphQL createData の `"value": "assistant#..."` を抽出
* 完了時刻（ts）を取得
* GET /messages と順序の整合性を記録
* 完了検知ロジックの原型を作成

**将来用途：**
`ChatPage.ask()` vNext の完了判定を
**“GraphQL createData 到着をトリガー”** として実装する基盤になる。

---

## 8. ログ解析デバッグ方針（誤読防止のためのルール）

- XHR / GraphQL / jsonl を解析するときは、
  必ず **全行（少なくとも該当チャット分）を一次情報として確認する**。
- 「仕様としてイベントが飛んでいる」のか、「ロガー／解析側の取りこぼし」なのかを
  区別する前に、ログ全体を読んだうえで結論を出す。
- json.parse 不能な行も raw のまま扱い、意味づけは後段で行う

---

# 以上

（このファイルは docs/Design_chat_answer_detection_v0.1.md として保存することを推奨）

---

