"""
Central config — every other file imports from here.
Keeping this separate means if you switch LLM providers later,
you change ONE file, not every file that calls the LLM.
"""
import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

# Groq model to use for all reasoning steps
LLM_MODEL = "llama-3.1-8b-instant"

# How many sources to fetch per sub-question
SEARCH_RESULTS_PER_QUERY = 4

if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY missing. Copy .env.example to .env and fill it in.")
if not TAVILY_API_KEY:
    raise ValueError("TAVILY_API_KEY missing. Copy .env.example to .env and fill it in.")
