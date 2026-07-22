"""
Takes a broad user topic and decides what specific sub-questions are
worth researching separately. This is the "autonomous decision-making"
part of the agent — it's not a fixed pipeline, the LLM decides the plan.
"""
from llm_client import ask_llm_json

SYSTEM_PROMPT = """You are a research planner. Given a broad topic, break it down into
2-4 specific, well-scoped sub-questions that are worth researching separately to find
where expert/source opinion might genuinely differ.

Pick sub-questions likely to have real debate or disagreement in the real world —
not settled, uncontroversial facts.

Respond ONLY in this JSON format:
{"sub_questions": ["specific question 1", "specific question 2", ...]}
"""


def plan_research(topic: str) -> list[str]:
    result = ask_llm_json(SYSTEM_PROMPT, f"Topic: {topic}")
    return result.get("sub_questions", [])


if __name__ == "__main__":
    print(plan_research("Is intermittent fasting healthy?"))
