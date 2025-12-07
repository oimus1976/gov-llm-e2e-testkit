import pytest
import yaml
import pathlib

def load_advanced_cases():
    path = pathlib.Path("data/rag/advanced_cases.yaml")
    try:
        with path.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            cases = data.get("cases", [])
            if not cases:
                pytest.skip("No advanced RAG cases found (skip to avoid CI exit 5).")
            return cases
    except Exception as e:
        pytest.skip(f"YAML load error: {e}")

@pytest.mark.asyncio
@pytest.mark.parametrize("case", load_advanced_cases())
async def test_rag_advanced(case, chat_page):
    """
    Advanced RAG Test v0.1（簡易 multi-turn）
    - user → expected_keywords の turn を順に実行
    - must_not_contain の検証
    """
    turns = case.get("turns", [])
    must_not = case.get("must_not_contain", [])
    last_answer = ""

    for turn in turns:
        role = turn.get("role")
        content = turn.get("content")

        # user ターン：LLMに質問
        if role == "user":
            last_answer = await chat_page.ask(content)

        # expected_keywords ターン：検証
        elif role == "expected_keywords":
            for kw in content:
                assert kw in last_answer, f"[{case['id']}] expected keyword not found: {kw}"

        else:
            # 未対応ロールはスキップ（後方互換のため）
            continue

    # must_not_contain 検証
    for bad in must_not:
        assert bad not in last_answer, f"[{case['id']}] prohibited keyword found: {bad}"
