# sandbox/debug_chat_inspect.py
import inspect
from tests.pages.chat_page import ChatPage

print("=== ChatPage file path ===")
print(inspect.getfile(ChatPage))

print("\n=== ChatPage.ask() source ===")
print(inspect.getsource(ChatPage.ask))
