"""
Turns the raw list of detected contradictions into a clean, readable
markdown report — the actual deliverable a user reads.
"""


def generate_report(topic: str, all_contradictions: list[dict], sources_used: list[str]) -> str:
    lines = [f"# Contradiction Report: {topic}\n"]

    if not all_contradictions:
        lines.append("No genuine contradictions were found across the sources checked. "
                      "This can mean the topic is well-settled, or that the search didn't "
                      "surface conflicting viewpoints — try a more specific or more debated angle.\n")
    else:
        lines.append(f"Found **{len(all_contradictions)}** genuine contradiction(s) across sources.\n")
        for i, c in enumerate(all_contradictions, 1):
            lines.append(f"## {i}. {c['topic']}  \n*Confidence: {c['confidence'].upper()}*\n")
            lines.append(f"- **{c['source_a']}** says: {c['claim_a']}")
            lines.append(f"- **{c['source_b']}** says: {c['claim_b']}")
            lines.append(f"\n**Why this is a real conflict:** {c['why_conflicting']}\n")

    lines.append("\n---\n### Sources checked\n")
    for s in sources_used:
        lines.append(f"- {s}")

    return "\n".join(lines)
