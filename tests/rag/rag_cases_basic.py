# ==========================================================
# RAG Basic 事前定義ケース v0.1
# ==========================================================

def load_basic_cases():
    """
    Basic 形式（シングルターン）の評価ケース。
    """
    return [
        {
            "id": "BASIC_001",
            "question": "かつらぎ町の魅力を3つ教えて",
            "expected_keywords": ["自然", "歴史", "食"],
            "must_not_contain": ["エラー", "不明"],
        },
        {
            "id": "BASIC_002",
            "question": "和歌山県の特産品を教えて",
            "expected_keywords": ["梅", "みかん"],
            "must_not_contain": ["不明"],
        },
    ]
