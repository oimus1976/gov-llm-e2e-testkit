class BasePage:
    def __init__(self, page):
        self.page = page

    def goto(self, url: str):
        self.page.goto(url)

    def fill(self, selector: str, text: str):
        self.page.fill(selector, text)

    def click(self, selector: str):
        self.page.click(selector)

    def text(self, selector: str) -> str:
        return self.page.inner_text(selector)
