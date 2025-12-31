# src/f9/a/resolution/resolution_required.py


class ResolutionRequired(Exception):
    """
    自動解決不可。
    人間入力（A-4）に委譲するための候補情報を保持する。
    """

    def __init__(self, message: str, candidates: dict):
        super().__init__(message)
        self.candidates = candidates
