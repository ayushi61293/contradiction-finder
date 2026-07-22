# Contradiction Finder Agent

An AI agent that researches a topic and specifically surfaces where different
sources **genuinely disagree** — instead of just summarizing what they say.

Most research tools tell you "here's what's out there." This one tells you
"here's where the experts actually contradict each other, and why" — which is
more useful for critical thinking and due diligence.

## How it works (agent loop)

```
Topic
  |
  v
[Planner Agent] --> decides 2-4 specific sub-questions worth researching
  |
  v
[Search Tool] --> fetches real, live sources per sub-question (Tavily)
  |
  v
[Extractor Agent] --> pulls structured factual claims out of each source
  |
  v
[Detector Agent] --> compares claims across sources, flags REAL contradictions
  |                   (with a confidence score, not just a binary flag)
  v
[Report Generator] --> clean markdown report with citations
```

This is a genuine multi-step agent, not a single prompt — the planner makes
autonomous decisions about what to research, and the pipeline branches based
on what's actually found.

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env
# then edit .env and add your free Groq + Tavily API keys
```

- Groq (free): https://console.groq.com
- Tavily (free, 1000 searches/month): https://tavily.com

## Run it

```bash
python main.py "is intermittent fasting healthy"
```

Try genuinely contentious topics for the most interesting output — nutrition
science, economic policy debates, or tech predictions tend to have real,
documented disagreement.

## Known limitations (important — read before demoing)

- The detector is tuned to avoid flagging "different wording of the same
  fact" as a contradiction, but it isn't perfect — it can occasionally miss
  subtle disagreement or, rarer, flag something borderline.
- It surfaces disagreement between sources — it does **not** independently
  verify which source is actually correct. Think of it as a first-pass
  filter for a human researcher, not a final judge of truth.
- Search quality depends on what's publicly indexed; very niche or very new
  topics may not have enough sources to compare.

## Possible extensions

- Add few-shot examples to the detector prompt to further reduce false positives
- Add a "severity" ranking across all found contradictions, not just per-pair confidence
- Cache search results to avoid re-fetching the same sources on repeated runs
