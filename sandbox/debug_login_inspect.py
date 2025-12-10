# sandbox/debug_login_inspect.py
import inspect
from tests.pages.login_page import LoginPage

print("=== LoginPage: file path ===")
print(inspect.getfile(LoginPage))

print("\n=== LoginPage: source code ===")
print(inspect.getsource(LoginPage))
