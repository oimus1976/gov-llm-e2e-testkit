"""
bootstrap_env.py

目的:
- ローカル実行時に .env の存在を保証する（冪等）
- 既存の .env は絶対に上書きしない
- 既知の候補ファイルから .env を生成する
- 必要に応じてユーザーに手動入力を促す

注意:
- 本スクリプトは「人間のローカル初期設定」専用
- CI 環境では使用しない（CI は環境変数を明示的に設定する）
"""

from pathlib import Path
import shutil
import sys

# 正本となる .env
ENV = Path(".env")

# コピー元の優先順位（人間の実運用を優先）
CANDIDATES = [
    Path(".env.internet_html"),  # 既存の実データ（人間管理）
    Path(".env.internet.sample"),  # 推奨サンプル
    Path(".env.sample"),  # フォールバック
]

# 必須環境変数
REQUIRED_KEYS = [
    "QOMMONS_URL",
    "QOMMONS_USER",
    "QOMMONS_PASSWORD",
]


def main() -> None:
    # --- 冪等性ガード ---
    if ENV.exists():
        print("[bootstrap] .env は既に存在します。何もしません。")
        return

    # --- コピー元の探索 ---
    for src in CANDIDATES:
        if src.exists():
            shutil.copy(src, ENV)
            print(f"[bootstrap] {src} から .env を作成しました。")
            break
    else:
        print("[bootstrap][エラー] .env のコピー元が見つかりません。")
        print("手動で .env を作成してください。")
        sys.exit(1)

    # --- 内容チェック ---
    text = ENV.read_text(encoding="utf-8", errors="ignore")

    missing = []
    for key in REQUIRED_KEYS:
        if f"{key}=" not in text:
            missing.append(key)

    if missing:
        print("\n[bootstrap][要対応]")
        print(".env は作成されましたが、必須項目が不足しています。")
        for k in missing:
            print(f"  - {k}")
        print("\n.env を開いて実際の値を入力してください。")
        return

    if "dummy" in text.lower() or "changeme" in text.lower():
        print("\n[bootstrap][要対応]")
        print(".env にダミー値が含まれています。")
        print("実際の認証情報に置き換えてください。")
        return

    print("[bootstrap] .env の内容を確認しました。問題なさそうです。")


if __name__ == "__main__":
    main()
