from .base_page import BasePage

class ChatPage(BasePage):

    def send_message(self, text: str):
        self.fill("#chat-input", text)
        self.click("#send-button")

    def last_response(self) -> str:
        return self.text(".assistant-message:last-child")
