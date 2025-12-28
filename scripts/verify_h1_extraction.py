# verify_h1_extraction.py
from pathlib import Path
from bs4 import BeautifulSoup

HTML_PATH = Path(
    "out/f8/20251228/20251228T185721_manual/20251228/manual-test/Q15/after_answer_ready.html"
)

html = HTML_PATH.read_text(encoding="utf-8")
soup = BeautifulSoup(html, "html.parser")

# 1. message-received を取得
messages = soup.select("div.message-received")
print(f"message-received count: {len(messages)}")

if not messages:
    print("=> INVALID: no message-received")
    exit()

# 2. 最後の message-received
answer_scope = messages[-1]

# 3. その中の markdown を取得
markdowns = answer_scope.select("div.markdown")
print(f"markdown count in last message-received: {len(markdowns)}")

if not markdowns:
    print("=> INVALID: no markdown in last message-received")
    exit()

# 4. 最後の markdown を選択
target = markdowns[-1]
text = target.get_text(separator="\n", strip=False)

print(f"selected markdown id: {target.get('id')}")
print(f"text_len: {len(text)}")

if text.strip() == "":
    print("=> INVALID: empty text")
else:
    print("=> VALID")
    print("----- preview -----")
    print(text[:500])
