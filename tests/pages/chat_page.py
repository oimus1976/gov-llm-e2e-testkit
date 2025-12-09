# ==========================================================
# ChatPage v0.2
# ==========================================================

from .base_page import BasePage
import time


class ChatPage(BasePage):

    LOC_INPUT = "textarea"
    LOC_SEND = "button:has-text('送信')"
    LOC_LAST_ANSWER = ".ai-answer:last-of-type"

    def __init__(self, page, config):
        super().__init__(page, config)

    def ask(self, text: str, evidence_dir=None) -> str:
        # 入力
        self.safe_type(self.LOC_INPUT, text)
        self.safe_click(self.LOC_SEND)

        # 応答待機（簡易）
        time.sleep(1.0)

        answer = self.safe_get_text(self.LOC_LAST_ANSWER)

        # 必要なら証跡保存
        if evidence_dir:
            f = evidence_dir / "answer.txt"
            f.write_text(answer, encoding="utf-8")

        return answer
