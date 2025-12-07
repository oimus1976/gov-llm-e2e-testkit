import pytest
import yaml
import pathlib

# YAML 読み込みユーティリティ
def load_basic_cases():
    path = pathlib.Path("data/rag/basic_cases.yaml")
    try:
        with path.open("r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            cases = data.get("cases", [])
            if not cases:
                pytest.skip("No basic RAG cases found (skip to avoid CI exit 5).")
            return cases
    except Exception as e:
        pytest.skip(f"YAML load error: {e}")

@pytest.mark.asyncio
@pytest.mark.parametrize("case", load_basic_cases())
async def test_rag_basic(case, chat_page):
    """
    Basic RAG Test v0.1
    - expected_keywords がすべて回答文に含まれているか
    - must_not_contain が回答文に含まれないか
    """
    question = case["question"]
    expected_keywords = case.get("expected_keywords", [])
    must_not = case.get("must_not_contain", [])

    # LLMへの質問（Page Objectの高レベルAPI）
    answer = await chat_page.ask(question)

    # expected_keywords の AND 判定
    for kw in expected_keywords:
        assert kw in answer, f"[{case['id']}] expected keyword not found: {kw}"

    # must_not_contain の NOT 判定
    for bad in must_not:
        assert bad not in answer, f"[{case['id']}] prohibited keyword found: {bad}"
