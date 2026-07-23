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

STEP 1 — before comparing two claims, sanity-check that they're actually about a
similar enough entity/condition that comparing them makes sense. Use judgment, not
a rigid checklist: "ballet" vs "hip-hop" are different enough activities that their
calorie numbers aren't comparable. "150 lb person" vs "70 kg adult" ARE comparable
(roughly the same weight). "30 minutes" vs "45 minutes" are close enough that if the
numbers still clash badly, it's worth flagging (at lower confidence) rather than
auto-discarding. When in doubt about whether two claims are close enough to compare,
lean toward including it with a "low" confidence label rather than silently dropping it.

STEP 2 — once you've judged the claims comparable, check whether they actually
disagree in substance.

IMPORTANT — be strict about what counts as a real contradiction, but don't be so
strict that you end up finding nothing. A real, useful project finds a handful of
genuine tensions per topic, not necessarily zero:
- A real contradiction: Source A says "X reduces risk by 30%", Source B says "X has no effect on risk" — same X, opposite conclusions.
- A real contradiction: Source A says "a 30-min moderate session burns 150-250 kcal", Source B says "a 30-min moderate session burns 200-350 kcal" — same activity, same duration, same intensity, genuinely different numeric ranges. FLAG THIS.
- A real contradiction: two health/fitness authorities recommend different specific thresholds for the same goal (e.g. one says 300 min/week, another says 150 min/week, for the same outcome) — FLAG THIS, even if one source frames it as "for substantial weight loss" and another as "for health benefits," as long as they're both presented as guidance for the same underlying question.
- NOT a contradiction: Source A says "X is very effective", Source B says "X works well." (same meaning, different words)
- NOT a contradiction: two claims about clearly different activities (ballet vs hip-hop) or wildly different timeframes (per hour vs per week) where the numbers were never meant to be compared directly.
- NOT a contradiction: one claim gives a specific number and the other gives only a vague qualitative statement with no number at all — nothing to compare.
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
