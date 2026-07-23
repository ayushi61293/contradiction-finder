"""
The orchestrator — this IS the agent loop:
  plan -> search -> extract -> detect -> repeat per sub-question -> report

Run: python main.py "your topic here"
"""
import sys
from rich.console import Console
from rich.progress import track

from agents.planner import plan_research
from tools.search_tool import search_web
from agents.extractor import extract_claims
from agents.detector import detect_contradictions
from agents.report import generate_report

console = Console()


def run_contradiction_finder(topic: str) -> str:
    console.print(f"\n[bold cyan]Researching:[/bold cyan] {topic}\n")

    # 1. PLAN — agent decides what to actually research
    sub_questions = plan_research(topic)
    console.print(f"[yellow]Planned {len(sub_questions)} sub-questions:[/yellow]")
    for q in sub_questions:
        console.print(f"  - {q}")

    all_contradictions = []
    all_sources_seen = []

    for question in sub_questions:
        console.print(f"\n[bold]--> Researching:[/bold] {question}")

        # 2. SEARCH — fetch multiple real sources
        sources = search_web(question)
        if len(sources) < 2:
            console.print("   [dim]Not enough sources found, skipping.[/dim]")
            continue

        # 3. EXTRACT — pull structured claims from each source
        claims_by_source = {}
        for src in sources:
            claims = extract_claims(src["title"], src["content"])
            if claims:
                label = f"{src['title']} ({src['url']})"
                claims_by_source[label] = claims
                all_sources_seen.append(label)

        # 4. DETECT — compare claims across sources for real disagreement
        if len(claims_by_source) >= 2:
            contradictions = detect_contradictions(claims_by_source)
            all_contradictions.extend(contradictions)
            console.print(f"   [green]Found {len(contradictions)} contradiction(s)[/green]")

    # De-duplicate: the same pair of claims can surface more than once if
    # sub-questions overlap and pull in the same sources. We key on the
    # actual claim text (not just source names), normalized, so near-identical
    # findings collapse into one.
    seen_keys = set()
    deduped_contradictions = []
    for c in all_contradictions:
        key = (
            " ".join(c.get("claim_a", "").lower().split()),
            " ".join(c.get("claim_b", "").lower().split()),
        )
        # a pair is a duplicate of its reverse too (A vs B == B vs A)
        reverse_key = (key[1], key[0])
        if key in seen_keys or reverse_key in seen_keys:
            continue
        seen_keys.add(key)
        deduped_contradictions.append(c)

    if len(all_contradictions) != len(deduped_contradictions):
        console.print(
            f"[dim]Removed {len(all_contradictions) - len(deduped_contradictions)} "
            f"duplicate contradiction(s) found across overlapping sub-questions.[/dim]"
        )

    # 5. REPORT — turn findings into a readable output
    report = generate_report(topic, deduped_contradictions, all_sources_seen)
    return report


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print('Usage: python main.py "your topic here"')
        sys.exit(1)

    topic = " ".join(sys.argv[1:])
    final_report = run_contradiction_finder(topic)

    console.print("\n\n[bold magenta]===== FINAL REPORT =====[/bold magenta]\n")
    console.print(final_report)

    with open("report_output.md", "w") as f:
        f.write(final_report)
    console.print("\n[dim]Saved to report_output.md[/dim]")
