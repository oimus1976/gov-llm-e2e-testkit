# Debugging Principles v0.1  

AIプロジェクト / E2Eテスト / Python / SPA / CI 向け 共通デバッグ原則  
作成日: 2025-12-09  
対象範囲: gov-llm-e2e-testkit / reiki-rag-converter / Obsidian系 / Python系 全域  
ステータス: Draft（次版で v0.2: 体系化予定）

---

## 1. 目的  

この文書は、開発中に遭遇するバグ・挙動不良・テスト失敗を  
**最速・最小コストで解決するための共通デバッグ原則** をまとめたもの。

Playwright、Python、pytest、SPA、YAML、CI、ファイルI/O、  
あらゆる領域で再利用できる “横断デバッグ基盤” を提供する。

---

## 2. Debugging 原則（全領域共通・最重要12条）

### **原則1：不具合は「黒箱の外側 → 内側」の順で攻略する**

バグの大半はコード内部ではなく環境や境界で起きる。

チェックすべき優先順：

1. 実行コマンド（python -m pytest / python script.py）
2. Python環境（version / path / venv / editable install）
3. ファイル構造（パスの誤り・import先）
4. 設定（YAML, env vars）
5. ライブラリ（Playwright, pytest, pydantic）
6. 自作コード（最終チェック）

**内部を見る前に、外側を固める。これが最短ルート。**

---

### **原則2：わからなくなったら「同期化」する**

async は便利だが複雑性が跳ね上がる。

- pytest-asyncio(strict)
- event loop 複数管理
- Playwright async の二重 await
- SPA の hydration 待ち

**→ 全部“同期化（Sync Playwright）”した瞬間に問題が蒸発する。**

同期はデバッグの拠点。  
async は完成してから戻れば良い。

---

### **原則3：まず「見える化」。ログ・HTML・スクショを必ず取る**

デバイスは嘘をつかない。人間は勘違いする。

- print  
- screenshot  
- HTMLダンプ  
- URL 出力  
- title 出力  

**“状況を正確に観測すること” がデバッグの 80% を解決する。**

---

### **原則4：バグは「再現」できれば勝ち**

再現する → 理由を特定できる → 修正できる。

逆に言えば：

- 再現しないバグを無理に追わない  
- 再現条件を特定することが最重要タスク  

---

### **原則5：テストは思想ではなく“実際の挙動”に従う**

正論よりも、事実が強い。

例：  
SPA のログインは navigation をしない → navigation を待つコードは不正解  
headless は不安定 → headless=False にするべき

**現実に合わせてコードを作る。**

---

### **原則6：ログは「過去・現在・未来」を同時に語らせる**

実行順序を見れば、何が起こり、何が起こらなかったか一目でわかる。

例：
```python
print("BEFORE CLICK:", page.url)
print("AFTER CLICK:", page.url)
```

→ click により何が“起きた/起きなかった”かが明確になる。

---

### **原則7：小さく切って、一つずつ確実に通す**

巨大なテストを一度に通そうとすると失敗する。

- Login を通す  
- Chat を通す  
- RAG Basic を通す  
- RAG Advanced を通す  

**階段を一段ずつ登るほうが早い。**

---

### **原則8：Playwrightは人間とは違う UI を見る**

- 人間には見える  
- Playwright には見えない  
- 逆もある  

SPA やフレームワークは描画の順序が変わるため、  
Playwright のほうが“正確に失敗を教えてくれる”。

---

### **原則9：false-positive と false-negative を切り分ける**

バグの種類は2つだけ：

- **本当に失敗している → 正しいFail**
- **正しい動作だがテストの書き方が悪い → 誤判定のFail**

後者を減らすとテストは急に安定する。

---

### **原則10：時間は“敵”ではなく“味方”。Wait戦略を整える**

SPA / ネットワーク / 認証 の世界では時間差が常にある。

- wait_for_selector  
- timeouts  
- no_wait_after  
- wait_for_load_state("networkidle")

**待ち方こそが E2E の品質。**

---

### **原則11：環境依存の問題を“疑わない”日は一日もない**

- Python 3.13 の仕様変更  
- Windows の PATH 問題  
- Git Bash と PowerShell の実体差  
- headless の挙動差  

**環境の問題と仮定するのは“敗北”ではなく最速ルートである。**

---

### **原則12：エラーは“敵”ではなくガイド**

沈黙こそ最悪。  
エラーは「教えてくれている」。

- import error  
- selector timeout  
- 401 unauthorized  
- navigation timeout  

全部ヒント。

---

## 3. Playwright（E2E）専用の原則

### **P1：ログインはnavigationしない（SPA）**

SPAのログインは  
**URLが変わらず内部状態だけ変わる**  
→ navigation を待つとハングする  
→ 必ず no_wait_after=True

---

### **P2：headless=True は最後に使う**

初期構築は headless=False が最強。  
UI の挙動が丸見えになる。

---

### **P3：selector は「将来変更される」前提で書く**

- id → 変わる  
- CSS クラス → 変わる  
- role + name → 安定しやすい  

---

### **P4：デバッグでは“遷移前後のURL”を必ず記録せよ**

```python
print(page.url)
page.screenshot(...)
```

これは真実を語る。

---

## 4. pytest のデバッグ原則

- **まず --maxfail=1**  
- **collect-only で先に構造を確認**  
- **fixture の scope は慎重に**  
- **asyncio の strict モードは理解して使う**

---

## 5. CI 上のデバッグ原則

- ローカルで headless=False → PASS  
- CI は headless=True → FAIL  
- → 待ち時間が足りない、selector 調整不足のサイン

**CIに合わせるのではなく、CIが動くコードをローカルで作る。**

---

## 6. 結論  

デバッグは “才能” ではなく “手順” と “観察力”。  
今回の E2E 構築は、その両方が極めて高いレベルで発揮された例である。

---

## 7. 次版（v0.2）で追加予定  

- デバッグフローチャート  
- SPAログインの正式手順  
- selector戦略のガイドライン  
- CI用 headless 運用ガイド  
- エラー → 原因 → 対策の逆引き辞典化

---

（End of Document）
