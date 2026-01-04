"""
Manual runner for F8 Set-1 (orchestrator-backed).

Purpose:
- Execute F8 via f8_orchestrator with a real browser
- Verify runtime behavior (DOM capture, answer.md generation)
- Collect operational artifacts only

Non-Goals:
- Evaluation or comparison of answers
- Automatic retries or heuristics
"""

import os
from pathlib import Path
from playwright.sync_api import sync_playwright
import yaml

from src.env_loader import load_env
from tests.pages.login_page import LoginPage
from tests.pages.chat_select_page import ChatSelectPage
from tests.pages.chat_page import ChatPage

from src.execution.f8_orchestrator import (
    run_f8_collection,
    OrdinanceSpec,
    QuestionSpec,
    ExecutionProfile,
)


def _resolve_output_root() -> Path:
    value = os.getenv("OUTPUT_ROOT")
    if not value:
        raise EnvironmentError(
            "OUTPUT_ROOT is required and must point to the final output directory (includes run_id)."
        )
    output_root = Path(value).expanduser().resolve()
    output_root.mkdir(parents=True, exist_ok=True)
    return output_root


def _write_yaml_once(path: Path, payload: dict) -> None:
    if path.exists():
        raise FileExistsError(f"file already exists: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        yaml.safe_dump(payload, sort_keys=False, allow_unicode=True), encoding="utf-8"
    )


def _write_readme_once(path: Path) -> None:
    if path.exists():
        raise FileExistsError(f"file already exists: {path}")
    content = """# F10-A Observation Dataset

- 本成果物は Qommons.AI UI を観測した一次データです（評価なし）。
- 評価・判定・Gate は reiki-rag-converter 側の責務です。
- manifest.yaml と answer/ 配下のファイル群をそのまま引き渡してください。
"""
    path.write_text(content, encoding="utf-8")


def _collect_manifest_entries(answer_root: Path) -> list[dict]:
    if not answer_root.exists():
        return []

    entries = []
    for ordinance_dir in sorted(
        [p for p in answer_root.iterdir() if p.is_dir()], key=lambda p: p.name
    ):
        for answer_file in sorted(ordinance_dir.glob("*.md"), key=lambda p: p.name):
            entries.append(
                {
                    "ordinance_id": ordinance_dir.name,
                    "question_id": answer_file.stem,
                    "file": (
                        Path("answer")
                        / ordinance_dir.name
                        / answer_file.name
                    ).as_posix(),
                }
            )
    return entries


def main():
    # --------------------------------------------------
    # Load environment (same as conftest.py)
    # --------------------------------------------------
    config, _ = load_env()

    # --------------------------------------------------
    # Fixed manual execution parameters (explicit)
    # --------------------------------------------------
    output_root = _resolve_output_root()
    run_id = output_root.name

    # ---- F8 Set-1 (explicit, no inference) ----
    ordinances = [
        OrdinanceSpec(
            ordinance_id="manual-test",
            display_name="manual-test",
        )
    ]

    questions = [
        QuestionSpec(
            question_id="Q01",
            question_text="Q1. この条例の目的を分かりやすく説明してください。",
        ),
        QuestionSpec(
            question_id="Q02",
            question_text="Q2. この条例が何条で構成されているかを示し、それぞれの条の概要を説明してください。",
        ),
        QuestionSpec(
            question_id="Q03",
            question_text="Q3. 第○条の内容を要約してください。",
        ),
        QuestionSpec(
            question_id="Q04",
            question_text="Q4. 第○条第○項の内容を説明してください。",
        ),
        QuestionSpec(
            question_id="Q05",
            question_text="Q5. この条例で定められている義務・禁止事項をすべて抽出し、箇条書きで説明してください。",
        ),
        QuestionSpec(
            question_id="Q06",
            question_text="Q6. この条例に基づく手続きの全体的な流れを、関連条文を引用しながら説明してください。",
        ),
        QuestionSpec(
            question_id="Q07",
            question_text="Q7. 他の条文の解釈に影響を与える条があれば、引用して説明してください。",
        ),
        QuestionSpec(
            question_id="Q08",
            question_text="Q8. 附則がある場合、その内容を要約し、本則との関係を説明してください。",
        ),
        QuestionSpec(
            question_id="Q09",
            question_text="Q9. 住民（関係者）が特に注意すべき点を説明してください。",
        ),
        QuestionSpec(
            question_id="Q10",
            question_text="Q10. 例外規定がある場合、その内容を説明してください。なければ「ない」と答えてください。",
        ),
        QuestionSpec(
            question_id="Q11",
            question_text="Q11. 定義されている用語があれば、定義条を引用して説明してください。",
        ),
        QuestionSpec(
            question_id="Q12",
            question_text="Q12. 第○条と第○条の関係性を説明してください。",
        ),
        QuestionSpec(
            question_id="Q13",
            question_text="Q13. 回答の根拠となる条文を引用して示してください。",
        ),
        QuestionSpec(
            question_id="Q14",
            question_text="Q14. 判断基準を本文の記載箇所を引用しながらまとめてください。",
        ),
        QuestionSpec(
            question_id="Q15",
            question_text="Q15. 条例を「目的→手続き→義務→例外→附則」の順に再構成してください。",
        ),
        QuestionSpec(
            question_id="Q16",
            question_text="Q16. 第三者に説明する場合の最適な説明順を、条文に基づいて示してください。",
        ),
        QuestionSpec(
            question_id="Q17",
            question_text="Q17. 条例全体を統合して説明してください。",
        ),
        QuestionSpec(
            question_id="Q18",
            question_text="Q18. 条例全体を100字以内で要約してください。",
        ),
    ]

    execution_profile = ExecutionProfile(
        profile_name="web-default",
        run_mode="collect-only",
    )
    question_pool = "Golden_Question_Pool_A_v1.1"
    ordinance_set = "Golden_Ordinance_Set_v1"

    # --------------------------------------------------
    # Playwright bootstrap
    # --------------------------------------------------
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()

        # ---- Login ----
        login = LoginPage(page, config)
        login.open()
        login.login()

        # ---- Chat selection ----
        select_page = ChatSelectPage(page, config)
        ai_name = config.get("chat_name", "プライベートナレッジ")
        select_page.open_ai(ai_name)

        # ---- ChatPage ----
        chat_page = ChatPage(page, config)

        # --------------------------------------------------
        # Run F8 via orchestrator
        # --------------------------------------------------
        summary = run_f8_collection(
            chat_page=chat_page,
            ordinances=ordinances,
            questions=questions,
            execution_profile=execution_profile,
            run_id=run_id,
            qommons_config={
                "model": "gpt-5.2",
                "web_search": False,
                "region": "jp",
                "ui_mode": "web",
            },
            knowledge_scope="golden",
            knowledge_files=[],
            ordinance_set=ordinance_set,
            output_root=output_root,
            execution={
                "mode": "manual",
                "retry": 0,
                "temperature": 0.0,
                "max_tokens": 2048,
            },
            question_pool=question_pool,
        )

        # --------------------------------------------------
        # DOM observation (manual, one-shot)
        # --------------------------------------------------
        debug_dir = output_root / "debug_dom"
        debug_dir.mkdir(parents=True, exist_ok=True)

        # 1) Full HTML snapshot
        html = page.content()
        (debug_dir / "page_full.html").write_text(html, encoding="utf-8")

        # 2) Ordered div text dump
        div_texts = page.locator("div").all_inner_texts()
        with (debug_dir / "div_texts.txt").open("w", encoding="utf-8") as f:
            for i, t in enumerate(div_texts):
                f.write(f"\n===== DIV[{i}] =====\n")
                f.write(t.strip())
                f.write("\n")

        # --------------------------------------------------
        # Minimal result summary (fact only)
        # --------------------------------------------------
        print("aborted:", summary.aborted)
        print("fatal_error:", summary.fatal_error)

        # --------------------------------------------------
        # F10-A artifacts
        # --------------------------------------------------
        executed_at = summary.executed_at.isoformat()
        manifest = {
            "schema_version": "manifest_v0.1",
            "based_on_interface": "v0.1r+",
            "kind": "manifest",
            "run_id": run_id,
            "executed_at": executed_at,
            "sets": {
                "ordinance_set": ordinance_set,
                "question_pool": question_pool,
            },
            "entries": _collect_manifest_entries(output_root / "answer"),
        }

        execution_meta = {
            "run_id": run_id,
            "executed_at": executed_at,
            "question_csv": None,
            "question_pool": question_pool,
            "ordinance_set": ordinance_set,
            "execution_account": config.get("username", "N/A"),
            "evaluation_performed": False,
            "notes": ["UI 観測のみ。評価・Gate 判定は含まない。"],
        }

        _write_yaml_once(output_root / "manifest.yaml", manifest)
        _write_yaml_once(output_root / "execution_meta.yaml", execution_meta)
        _write_readme_once(output_root / "README.md")

        context.close()
        browser.close()


if __name__ == "__main__":
    main()
