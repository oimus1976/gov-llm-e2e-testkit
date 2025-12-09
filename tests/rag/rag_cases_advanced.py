# ==========================================================
# RAG Advanced（マルチターン）事前定義ケース v0.1
# ==========================================================

def load_advanced_cases():
    """
    Advanced（複数ターン、期待語・禁止語チェック）用ケース。
    """
    return [
        {
            "id": "ADV_001",
            "turns": [
                {"role": "user", "content": "かつらぎ町について教えて"},
                {"role": "expected_keywords", "content": ["町", "自然"]},
                {"role": "user", "content": "特におすすめの場所は？"},
                {"role": "expected_keywords", "content": ["神社", "温泉"]},
            ],
            "must_not_contain": ["エラー", "不明"],
        },
        {
            "id": "ADV_002",
            "turns": [
                {"role": "user", "content": "和歌山県の名物は？"},
                {"role": "expected_keywords", "content": ["梅", "みかん"]},
                {"role": "user", "content": "他には？"},
                {"role": "expected_keywords", "content": ["那智黒", "金山寺味噌"]},
            ],
            "must_not_contain": ["不明"],
        },
    ]
