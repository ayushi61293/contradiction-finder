"""
The heart of the project: compares claims from different sources and
flags genuine contradictions — while explicitly trying to avoid
false positives where sources just phrase the same fact differently.
"""
from llm_client import ask_llm_json

SYSTEM_PROMPT = """You are a rigorous fact-comparison analyst. You will be given claims
from multiple different sources on the same topic. Your job is to find genuine
contradictions between them.

IMPORTANT — be strict about what counts as a real contradiction:
- A real contradiction: Source A says "X reduces risk by 30%", Source B says "X has no effect on risk."
- NOT a contradiction: Source A says "X is very effective", Source B says "X works well." (same meaning, different words)
- NOT a contradiction: two claims about different sub-topics that don't actually overlap.

For each genuine contradiction found, also give a confidence label:
- "high": clear factual conflict, hard to explain away
- "medium": likely conflict, but could be due to different contexts/timeframes
- "low": possible tension, worth a human double-checking

Respond ONLY in this exact JSON format:
{
  "contradictions": [
    {
      "topic": "short label for what this is about",
      "claim_a": "the claim from source A",
      "source_a": "source A name/title",
      "claim_b": "the claim from source B",
      "source_b": "source B name/title",
      "why_conflicting": "1-2 sentence explanation of why these actually conflict",
      "confidence": "high" | "medium" | "low"
    }
  ]
}

If you find no genuine contradictions, return {"contradictions": []}. Do not force a
contradiction if there isn't a real one — that's a failure, not a success.
"""


def detect_contradictions(claims_by_source: dict[str, list[str]]) -> list[dict]:
    """
    claims_by_source looks like:
    {"Source Title 1": ["claim1", "claim2"], "Source Title 2": ["claim1", ...]}
    """
    if len(claims_by_source) < 2:
        return []  # need at least 2 sources to compare

    formatted = ""
    for source, claims in claims_by_source.items():
        formatted += f"\nSource: {source}\n"
        for c in claims:
            formatted += f"  - {c}\n"

    result = ask_llm_json(SYSTEM_PROMPT, formatted)
    return result.get("contradictions", [])


if __name__ == "__main__":
    sample = {
        "Study A": ["Coffee does not cause dehydration in regular drinkers."],
        "Health Blog B": ["Coffee is a diuretic and leads to dehydration if you drink too much."],
    }
    print(detect_contradictions(sample))
