"""
The heart of the project: compares claims from different sources and
flags genuine contradictions — while explicitly trying to avoid
false positives where sources just phrase the same fact differently.
"""
from llm_client import ask_llm_json
from config import DETECTOR_MODEL

SYSTEM_PROMPT = """You are a rigorous fact-comparison analyst. You will be given claims
from multiple different sources on the same topic. Your job is to find genuine
contradictions between them.

STEP 1 — before comparing two claims, check they are actually about the SAME specific
entity/condition. Two claims are only comparable if they match on all of these where
applicable: the same specific activity/sub-type (e.g. "ballet" vs "hip-hop" are
DIFFERENT activities, not comparable), the same population/body weight (e.g. "150 lb
person" vs "70 kg adult" are roughly comparable, but "150 lb person" vs "a general
average person" is NOT — a specific figure vs a vague range is not a conflict), and
the same duration/timeframe (e.g. "per hour" vs "per 30 minutes" are NOT directly
comparable unless converted).

STEP 2 — only after confirming the claims are about the same specific thing, check
whether they actually disagree in substance.

IMPORTANT — be strict about what counts as a real contradiction:
- A real contradiction: Source A says "X reduces risk by 30%", Source B says "X has no effect on risk" — same X, opposite conclusions.
- A real contradiction: Source A says "a 30-min moderate session burns 150-250 kcal", Source B says "a 30-min moderate session burns 200-350 kcal" — same activity, same duration, same intensity, genuinely different numeric ranges.
- NOT a contradiction: Source A says "X is very effective", Source B says "X works well." (same meaning, different words)
- NOT a contradiction: two claims about different sub-topics, different specific activities, different populations, or different timeframes that don't actually overlap — even if the topic label sounds similar. A specific figure for one dance style is not a contradiction with a general range covering many styles; it may simply fall within that range.
- NOT a contradiction: one claim gives a specific number and the other gives a vague/general statement with no number — there is nothing to compare, so this is not a conflict, it's just less information.
- Do NOT flag two claims from the exact same source against each other via different phrasings unless you would still flag them if a human read both sentences back to back and called it an inconsistency.

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
      "why_conflicting": "1-2 sentence explanation of why these actually conflict, referencing that they share the same entity/duration/population",
      "confidence": "high" | "medium" | "low"
    }
  ]
}

If you find no genuine contradictions, return {"contradictions": []}. Do not force a
contradiction if there isn't a real one — that's a failure, not a success. It is
completely normal and expected for this to return an empty list most of the time.
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

    # Use the stronger model here — this step needs careful reasoning to avoid
    # false positives, unlike the lighter planning/extraction steps.
    result = ask_llm_json(SYSTEM_PROMPT, formatted, model=DETECTOR_MODEL)
    return result.get("contradictions", [])


if __name__ == "__main__":
    sample = {
        "Study A": ["Coffee does not cause dehydration in regular drinkers."],
        "Health Blog B": ["Coffee is a diuretic and leads to dehydration if you drink too much."],
    }
    print(detect_contradictions(sample))
