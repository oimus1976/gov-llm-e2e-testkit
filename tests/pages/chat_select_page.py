# ---------------------------------------------------------
# ChatSelectPage v0.3  (gov-llm-e2e-testkit)
# チャット一覧 (/chat) から個別チャット (/chat/<uuid>) への遷移担当
# 最終更新: 2025-12-10
# ---------------------------------------------------------

import re
from .base_page import BasePage


class ChatSelectPage(BasePage):
    """メニュー画面（チャット一覧）で AI を選択する PageObject (v0.3)"""

    # ------------------------------
    # Locator
    # ------------------------------
    def card(self, name: str):
        """
        data-slot='card' 内のテキスト一致で目的のAIを選ぶ
        例: name = "プライベートナレッジ"
        """
        return self.page.locator("div[data-slot='card']").filter(has_text=name)

    # ------------------------------
    # 高レベルAPI: open_ai()
    #  - 指定したカードをクリック
    #  - URL が /chat/<何か> に変わるまで待機
    # ------------------------------
    def open_ai(self, name: str, *, evidence_dir=None) -> None:
        target = self.card(name)

        # クリック（失敗時は safe_click が証跡を取って例外送出）
        self.safe_click(target, evidence_dir=evidence_dir, label="chat_select_error")

        try:
            # URL が /chat/<something> になるまで待つ
            # 例: /chat/f5e7... のような形式
            self.page.wait_for_url(
                re.compile(r"/chat/[^/]+$"),
                timeout=self.timeout,
            )

            # ChatPage の入力欄が操作可能になるまで待つ
            self.page.locator("#message").wait_for(state="visible", timeout=self.timeout)
            self.page.wait_for_timeout(300)

        except Exception:
            if evidence_dir:
                self.collect_evidence(evidence_dir, "chat_room_open_error")
            raise
