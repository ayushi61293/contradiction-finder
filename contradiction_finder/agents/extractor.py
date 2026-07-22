"""
Given raw article text, pulls out a short list of concrete, checkable claims.
This is what turns messy paragraphs into structured data we can compare later.
"""
from llm_client import ask_llm_json

SYSTEM_PROMPT = """You are a careful research assistant. Extract concrete, checkable factual claims from the given article text.

Rules:
- Only extract claims that state something as fact (not questions, not opinions phrased as opinions).
- Keep each claim short (one sentence).
- Extract at most 5 claims — the most important/central ones only.
- Respond ONLY in this exact JSON format, nothing else:
{"claims": ["claim 1", "claim 2", ...]}
"""


def extract_claims(source_title: str, source_content: str) -> list[str]:
    if not source_content or len(source_content.strip()) < 50:
        return []  # not enough content to extract anything meaningful

    user_prompt = f"Article title: {source_title}\n\nArticle text:\n{source_content[:3000]}"
    result = ask_llm_json(SYSTEM_PROMPT, user_prompt)
    return result.get("claims", [])


if __name__ == "__main__":
    # Quick manual test
    sample = """
    A recent study found that drinking coffee does not cause dehydration
    in regular coffee drinkers, contrary to popular belief. Researchers
    tracked hydration levels and found no significant difference compared
    to water intake alone.
    """
    claims = extract_claims("Coffee and Hydration Study", sample)
    print(claims)
