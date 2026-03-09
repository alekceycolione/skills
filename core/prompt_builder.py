_PROMPT_TEMPLATE = """\
# SKILL INSTRUCTIONS
{instructions}

# CONTEXT
{context}

# USER QUERY
{query}
"""

_EXPORT_TEMPLATE = """\
## SKILL PROMPT
{prompt}

---

## AI RESPONSE
{response}
"""


def build_prompt(instructions: str, context: str, query: str) -> str:
    """Concatenate skill instructions, optional context, and user query."""
    ctx_block = context.strip() if context.strip() else "(none)"
    return _PROMPT_TEMPLATE.format(
        instructions=instructions.strip(),
        context=ctx_block,
        query=query.strip(),
    )


def build_export_text(prompt: str, response: str) -> str:
    """Produce a universal plain-text block ready for clipboard."""
    return _EXPORT_TEMPLATE.format(prompt=prompt, response=response)
