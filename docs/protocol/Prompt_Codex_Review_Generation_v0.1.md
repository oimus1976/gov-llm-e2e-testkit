---
title: Codex Review Generation Prompt
version: v0.1
status: active
category: protocol-support
consumers:
  - codex-vscode
related:
  - Protocol_Web_VSCode_Roundtrip_v1.1.md
  - Review_Template_v0.1.md
---

## Purpose

This document defines the **exact prompt** used to instruct Codex
to generate a review document from a fixed template.

This is NOT a template.
This is NOT a review result.
This is an operational instruction.

---

## Prompt (DO NOT MODIFY)

```text
You are NOT writing a new document from scratch.

Your task is to:
1. Read the template file:
   docs/templates/reviews/Review_Template_v0.1.md

2. Create a NEW review document by copying the template structure exactly.

3. Output the FULL CONTENT of the new file,
   as if it were saved to:
   docs/reviews/Review_<YYYYMMDD>_<context>.md

STRICT RULES:
- Do NOT modify section structure or headings
- Do NOT remove any sections
- Do NOT add new sections
- Fill sections ONLY when facts are explicitly known
- If information is unknown, write "UNKNOWN"
- Do NOT infer or guess
- Do NOT explain your reasoning
- Do NOT include commentary outside the markdown

CONTENT RULES:
- Section 3 (Codex 提出一次情報):
  - Use ONLY information directly observed from code, diffs, or execution
- pytest section:
  - If not executed, state who must execute it and why
- Reviewer judgement sections:
  - Leave empty unless explicitly instructed by Web

OUTPUT FORMAT:
- Markdown only
- No code fences
- No preamble, no epilogue
```

---

## Usage

1. Ensure `docs/templates/reviews/Review_Template_v0.1.md` exists
2. Copy the prompt text above
3. Paste into Codex with context
4. Verify generated file path and structure

※ プロンプト本文は **コードブロック内にそのまま固定**  
※ 説明文と混ぜない

---

## ルール（重要）

- プロンプトは **直接編集しない**
- 修正が必要になったら：
  - 新バージョンを切る（v0.2）
  - CHANGELOG に理由を書く
- Webチャット内の「便利プロンプト」は  
  **必ずこのファイルに昇格させる**

---
