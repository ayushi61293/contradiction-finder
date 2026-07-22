"""
One shared function every agent step uses to talk to the LLM.
Centralizing it means consistent error handling and easy provider swaps.
"""
import json
from groq import Groq
from config import GROQ_API_KEY, LLM_MODEL

client = Groq(api_key=GROQ_API_KEY)


def ask_llm_json(system_prompt: str, user_prompt: str) -> dict | list:
    """
    Calls the LLM and forces it to return valid JSON.
    Raises a clear error if the model returns something unparseable,
    instead of silently failing later.
    """
    response = client.chat.completions.create(
        model=LLM_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        response_format={"type": "json_object"},
        temperature=0.2,  # low temperature: we want consistent, focused reasoning here
    )
    raw = response.choices[0].message.content
    try:
        return json.loads(raw)
    except json.JSONDecodeError as e:
        raise ValueError(f"LLM did not return valid JSON:\n{raw}") from e


def ask_llm_text(system_prompt: str, user_prompt: str) -> str:
    """For steps where we just want plain readable text back (e.g., final report)."""
    response = client.chat.completions.create(
        model=LLM_MODEL,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.4,
    )
    return response.choices[0].message.content
