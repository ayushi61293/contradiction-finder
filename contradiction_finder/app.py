"""
Streamlit UI for the Contradiction Finder Agent.

Wraps the existing agent pipeline (planner -> search -> extractor -> detector -> report)
in a simple web interface, with live progress updates as the agent works.

Run locally:   streamlit run app.py
Deploy:        push to GitHub, connect repo on share.streamlit.io,
                add GROQ_API_KEY and TAVILY_API_KEY under app Secrets.
"""
import os
import streamlit as st

# --- Load secrets into env vars BEFORE importing agent code, since config.py
# reads keys via os.getenv() at import time. This lets Streamlit Cloud's
# "Secrets" work exactly like a local .env file with zero changes to config.py.
if "GROQ_API_KEY" in st.secrets:
    os.environ["GROQ_API_KEY"] = st.secrets["GROQ_API_KEY"]
if "TAVILY_API_KEY" in st.secrets:
    os.environ["TAVILY_API_KEY"] = st.secrets["TAVILY_API_KEY"]

from agents.planner import plan_research
from tools.search_tool import search_web
from agents.extractor import extract_claims
from agents.detector import detect_contradictions
from agents.report import generate_report

st.set_page_config(page_title="Contradiction Finder Agent", page_icon="🔍", layout="centered")

st.title("🔍 Contradiction Finder Agent")
st.caption(
    "An autonomous research agent that plans sub-questions, searches the live web, "
    "extracts claims, and surfaces where sources genuinely disagree — with confidence scoring."
)

with st.expander("How it works"):
    st.markdown(
        "- **Plan** — the agent breaks your topic into 2-4 specific sub-questions worth researching\n"
        "- **Search** — live web search (Tavily) pulls multiple independent sources per sub-question\n"
        "- **Extract** — an LLM (Groq / Llama 3.1) pulls structured factual claims from each source\n"
        "- **Detect** — claims are compared across sources to find genuine contradictions, "
        "not just different wording of the same fact\n"
        "- **Report** — findings are compiled into a structured, cited report"
    )

topic = st.text_input(
    "Enter a topic to research",
    placeholder="e.g. Is intermittent fasting healthy?",
)

run = st.button("Run Agent", type="primary", disabled=not topic.strip())

if run and topic.strip():
    status_box = st.status("Starting research...", expanded=True)
    all_contradictions = []
    all_sources_seen = []

    try:
        status_box.write(f"**Researching:** {topic}")

        # 1. PLAN
        status_box.update(label="Planning sub-questions...")
        sub_questions = plan_research(topic)
        status_box.write(f"Planned **{len(sub_questions)}** sub-questions:")
        for q in sub_questions:
            status_box.write(f"- {q}")

        # 2-4. SEARCH -> EXTRACT -> DETECT, per sub-question
        for question in sub_questions:
            status_box.update(label=f"Researching: {question}")
            sources = search_web(question)

            if len(sources) < 2:
                status_box.write(f"⚠️ Not enough sources for: *{question}* — skipping.")
                continue

            claims_by_source = {}
            for src in sources:
                claims = extract_claims(src["title"], src["content"])
                if claims:
                    label = f"{src['title']} ({src['url']})"
                    claims_by_source[label] = claims
                    all_sources_seen.append(label)

            if len(claims_by_source) >= 2:
                contradictions = detect_contradictions(claims_by_source)
                all_contradictions.extend(contradictions)
                status_box.write(f"Found **{len(contradictions)}** contradiction(s) for: *{question}*")

        # 5. REPORT
        status_box.update(label="Generating final report...")
        report = generate_report(topic, all_contradictions, all_sources_seen)
        status_box.update(label="Done", state="complete")

        st.markdown("### Final Report")
        st.markdown(report)

        st.download_button(
            "Download report as Markdown",
            data=report,
            file_name="contradiction_report.md",
            mime="text/markdown",
        )

    except Exception as e:
        status_box.update(label="Error", state="error")
        st.error(f"Something went wrong: {e}")
        st.info(
            "If this is an API key error, make sure GROQ_API_KEY and TAVILY_API_KEY "
            "are set in Streamlit Secrets (Settings → Secrets)."
        )

st.divider()
st.caption("Built with Python, Groq (Llama 3.1), and Tavily web search.")
