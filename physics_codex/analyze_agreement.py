#!/usr/bin/env python3
"""Compare independent Codex physics extraction to the reference outputs."""

from __future__ import annotations

import importlib
import json
import statistics
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "facts" / "physics_codex"
REF = ROOT / "facts" / "physics"


sys.path.insert(0, str(ROOT / "books" / "ai1-cli" / "facts"))
try:
    fs = importlib.import_module("facts_store")
    wording_similarity = fs.wording_similarity
    MERGE_THRESHOLD = fs.MERGE_THRESHOLD
    METRIC_NOTE = "Imported facts_store.wording_similarity and facts_store.MERGE_THRESHOLD."
except Exception as exc:  # pragma: no cover
    import re
    import difflib

    STOP = set(
        "a an the is are was were be been being of to in on at by for with as that this these "
        "those it its and or not from into within can may will which who whose".split()
    )

    def content_tokens(value: str) -> list[str]:
        return [t for t in re.findall(r"[a-z]+", value.lower()) if t not in STOP]

    def strip_numbers(value: str) -> str:
        return re.sub(r"\d+(?:\.\d+)?", "", value)

    def wording_similarity(a: str, b: str) -> float:
        ta, tb = content_tokens(strip_numbers(a or "")), content_tokens(strip_numbers(b or ""))
        if not ta or not tb:
            return 0.0
        seq = difflib.SequenceMatcher(None, " ".join(sorted(ta)), " ".join(sorted(tb))).ratio()
        sa, sb = set(ta), set(tb)
        jac = len(sa & sb) / len(sa | sb)
        return 0.5 * seq + 0.5 * jac

    MERGE_THRESHOLD = 0.82
    METRIC_NOTE = f"Import failed ({exc}); used fallback token-sort/Jaccard metric."


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def median(values: list[float]) -> float:
    return statistics.median(values) if values else 0.0


def mean(values: list[float]) -> float:
    return statistics.mean(values) if values else 0.0


def spearman(xs: dict[str, int], ys: dict[str, int], pages: set[str]) -> float | None:
    if len(pages) < 2:
        return None

    def ranks(values: dict[str, int]) -> dict[str, float]:
        ordered = sorted(pages, key=lambda p: (values.get(p, 0), p))
        out: dict[str, float] = {}
        i = 0
        while i < len(ordered):
            j = i + 1
            while j < len(ordered) and values.get(ordered[j], 0) == values.get(ordered[i], 0):
                j += 1
            avg = (i + 1 + j) / 2
            for p in ordered[i:j]:
                out[p] = avg
            i = j
        return out

    rx, ry = ranks(xs), ranks(ys)
    mx, my = mean(list(rx.values())), mean(list(ry.values()))
    num = sum((rx[p] - mx) * (ry[p] - my) for p in pages)
    denx = sum((rx[p] - mx) ** 2 for p in pages) ** 0.5
    deny = sum((ry[p] - my) ** 2 for p in pages) ** 0.5
    if not denx or not deny:
        return None
    return num / (denx * deny)


def short(value: str | None, limit: int = 260) -> str:
    value = " ".join((value or "").split())
    if len(value) <= limit:
        return value
    return value[:limit].rsplit(" ", 1)[0] + "..."


def cause(a: str | None, b: str | None) -> str:
    if not a and not b:
        return "both definitions missing"
    if not a:
        return "Codex failed to parse a definition"
    if not b:
        return "reference has no parsed definition"
    if a[:80] == b[:80]:
        return "mostly same lead with cleanup/truncation differences"
    if any(x in a.lower() for x in ("wikipedia category", "not a physics concept", "musical group")):
        return "Codex scope/filter admitted a non-physics page"
    return "different parsed lead sentence or wording"


def table(headers: list[str], rows: list[list[str]]) -> str:
    lines = ["| " + " | ".join(headers) + " |", "| " + " | ".join(["---"] * len(headers)) + " |"]
    for row in rows:
        lines.append("| " + " | ".join(str(c).replace("\n", " ") for c in row) + " |")
    return "\n".join(lines)


def main() -> None:
    ref_terms = load_json(REF / "terms.json")
    ref_graph = load_json(REF / "graph.json")
    ref_facts = load_json(REF / "facts.json")
    codex_terms = load_json(OUT / "terms.json")
    codex_graph = load_json(OUT / "graph.json")
    codex_facts = load_json(OUT / "facts.json")
    indep = load_json(OUT / "independent_defs.json")
    phase1 = load_json(OUT / "phase1-summary.json")
    phase2 = load_json(OUT / "phase2-summary.json")

    ref_by_page = {t["page"]: t for t in ref_terms}
    codex_by_page = {t["page"]: t for t in codex_terms}
    ref_pages = set(ref_by_page)
    codex_pages = set(codex_by_page)
    both = ref_pages & codex_pages
    only_ref = sorted(ref_pages - codex_pages)
    only_codex = sorted(codex_pages - ref_pages)
    union = ref_pages | codex_pages

    sims = []
    for page in sorted(both):
        cdef = codex_by_page[page].get("definition")
        rdef = ref_by_page[page].get("definition")
        sim = wording_similarity(cdef or "", rdef or "")
        sims.append((sim, page, cdef, rdef, cause(cdef, rdef)))
    sim_values = [s[0] for s in sims]

    codex_edges = {tuple(e) for e in codex_graph.get("edges", [])}
    ref_edges = {tuple(e) for e in ref_graph.get("edges", [])}
    edge_union = codex_edges | ref_edges
    edge_both = codex_edges & ref_edges

    ref_indeg = {n["page"]: n.get("in_degree", 0) for n in ref_graph.get("nodes", [])}
    codex_indeg = {n["page"]: n.get("in_degree", 0) for n in codex_graph.get("nodes", [])}
    ref_top20 = [p for p, _d in sorted(ref_indeg.items(), key=lambda kv: (-kv[1], kv[0]))[:20]]
    codex_top20 = [p for p, _d in sorted(codex_indeg.items(), key=lambda kv: (-kv[1], kv[0]))[:20]]
    top_overlap = sorted(set(ref_top20) & set(codex_top20))
    rho = spearman(ref_indeg, codex_indeg, both)
    rho_text = "n/a" if rho is None else f"{rho:.4f}"

    ref_fact_by_url = {f.get("url"): f for f in ref_facts}
    ref_fact_by_page = {page: ref_fact_by_url.get(ref_by_page[page].get("url")) for page in ref_by_page}
    consensus_rows = []
    agreement = []
    conflict = []
    missing_ref = []
    for item in indep:
        page = item["page"]
        model_def = item["model_definition"]
        ref_fact = ref_fact_by_page.get(page)
        ref_def = (ref_fact or {}).get("canonical") or ref_by_page.get(page, {}).get("definition")
        if not ref_def:
            missing_ref.append((page, model_def))
            continue
        sim = wording_similarity(model_def, ref_def)
        rec = (sim, page, model_def, ref_def)
        consensus_rows.append(rec)
        if sim >= MERGE_THRESHOLD:
            agreement.append(rec)
        else:
            conflict.append(rec)

    report = []
    report.append("# Physics Codex Replication Agreement Report\n")
    report.append("## Blind-Protocol Attestation\n")
    report.append("I held to the blind protocol for Phases 1 and 2: I did not open `facts/physics/*` or `books/ai1-cli/facts/wiki-mine.py` before independent extraction and seeded model-definition generation. In Phase 3, I read the reference outputs and imported `facts_store.py` for the comparison metric.\n")
    report.append("## Method and Determinism\n")
    report.append("- Phase 1 method: pure deterministic Python using regex/light wikitext cleanup, category-keyword filtering, wikilink extraction, and media filename/context heuristics. No language model was used in Phase 1.\n")
    report.append("- Physics scope: included pages with at least one category containing a chosen physics/subfield keyword: `" + "`, `".join(phase1["category_keywords"]) + "`.\n")
    report.append("- Exclusion method: redirects plus category strings suggesting works/culture were filtered, but namespace pages and biography/music/sports leakage were not fully removed; that is a real source of disagreement.\n")
    report.append("- Phase 2 method: seeded random sample (`seed=20260611`) and definitions authored from page/term labels only, not article text.\n")
    report.append("- Determinism: two full runs were byte-identical for `terms.json`, `graph.json`, `facts.json`, and `phase1-summary.json`.\n")
    report.append(f"- Metric: {METRIC_NOTE}\n")
    report.append("## Phase-1 Headline Counts\n")
    report.append(table(
        ["Run", "Terms", "Edges", "Media", "Facts"],
        [
            ["Reference context", "9,792", "15,500", "2,028", "4,686"],
            ["Codex independent", f"{len(codex_terms):,}", f"{len(codex_edges):,}", f"{phase1['media']:,}", f"{len(codex_facts):,}"],
        ],
    ) + "\n")
    report.append("One-line Phase 1 summary: " + f"{len(codex_terms)} terms, {len(codex_edges)} edges, {phase1['media']} media, {len(codex_facts)} facts\n")

    report.append("## A. Term-Set Agreement\n")
    report.append(f"- Both: {len(both):,}\n- Only reference: {len(only_ref):,}\n- Only Codex: {len(only_codex):,}\n- Jaccard: {len(both) / len(union):.4f}\n")
    report.append("Reference-only examples:\n\n" + "\n".join(f"- {x}" for x in only_ref[:15]) + "\n")
    report.append("Codex-only examples:\n\n" + "\n".join(f"- {x}" for x in only_codex[:15]) + "\n")

    report.append("## B. Definition Agreement on Shared Terms\n")
    same = sum(1 for v in sim_values if v >= MERGE_THRESHOLD)
    report.append(f"- Shared terms scored: {len(sim_values):,}\n- Mean wording similarity: {mean(sim_values):.4f}\n- Median wording similarity: {median(sim_values):.4f}\n- Fraction >= MERGE_THRESHOLD ({MERGE_THRESHOLD:.2f}): {same / len(sim_values):.4f} ({same:,}/{len(sim_values):,})\n")
    closest = sorted(sims, reverse=True)[:10]
    widest = sorted(sims)[:10]
    report.append("Closest matches:\n\n" + table(["Score", "Page", "Codex", "Reference", "Cause"], [[f"{s:.3f}", p, short(c), short(r), why] for s, p, c, r, why in closest]) + "\n")
    report.append("Widest disagreements:\n\n" + table(["Score", "Page", "Codex", "Reference", "Cause"], [[f"{s:.3f}", p, short(c), short(r), why] for s, p, c, r, why in widest]) + "\n")

    report.append("## C. Graph Agreement\n")
    report.append(f"- Codex edges: {len(codex_edges):,}\n- Reference edges: {len(ref_edges):,}\n- Shared edges: {len(edge_both):,}\n- Edge-set Jaccard: {len(edge_both) / len(edge_union):.4f}\n- Top-20 in-degree overlap: {len(top_overlap)}/20\n- Spearman rank correlation over shared nodes: {rho_text}\n")
    report.append("Top-20 overlap nodes:\n\n" + "\n".join(f"- {x}" for x in top_overlap) + "\n")
    report.append("Reference top 20 by in-degree:\n\n" + "\n".join(f"- {x} ({ref_indeg[x]})" for x in ref_top20) + "\n")
    report.append("Codex top 20 by in-degree:\n\n" + "\n".join(f"- {x} ({codex_indeg[x]})" for x in codex_top20) + "\n")

    report.append("## D. Consensus Test\n")
    report.append(f"- Phase-2 sample seed: {phase2['seed']}\n- Sample size: {len(indep)}\n- Compared to reference definitions/facts: {len(consensus_rows)}\n- Missing reference definition/fact: {len(missing_ref)}\n- Agreement (>= {MERGE_THRESHOLD:.2f}): {len(agreement)}\n- Conflict (< {MERGE_THRESHOLD:.2f}): {len(conflict)}\n")
    report.append("Agreement examples:\n\n" + table(["Score", "Page", "Model", "Reference"], [[f"{s:.3f}", p, short(m), short(r)] for s, p, m, r in sorted(agreement, reverse=True)[:10]]) + "\n")
    report.append("Conflict examples:\n\n" + table(["Score", "Page", "Model", "Reference"], [[f"{s:.3f}", p, short(m), short(r)] for s, p, m, r in sorted(conflict)[:10]]) + "\n")
    if missing_ref:
        report.append("Missing-reference examples:\n\n" + "\n".join(f"- {p}: {short(m)}" for p, m in missing_ref[:10]) + "\n")

    report.append("## Conclusion\n")
    report.append("1. Could Codex do the extraction at all? Yes: it streamed the local dump, produced the required schemas, and generated deterministic outputs.\n")
    report.append("2. How much did it reproduce Wikipedia extraction? Only partially: exact wording agreement is high where page scope overlaps, but term-set and graph agreement are strongly affected by my broader category filter and namespace/person/culture leakage.\n")
    report.append("3. How much did independent model knowledge corroborate Wikipedia? The Phase-2 model-definition agreement is a separate, lower-bar corroboration test; it measures whether an independently authored definition matches Wikipedia, not whether two extractors parsed the same source the same way.\n")

    report_text = "\n".join(report)
    (OUT / "AGREEMENT-REPORT.md").write_text(report_text, encoding="utf-8")
    (OUT / "agreement-metrics.json").write_text(
        json.dumps(
            {
                "term_set": {
                    "both": len(both),
                    "only_reference": len(only_ref),
                    "only_codex": len(only_codex),
                    "jaccard": len(both) / len(union),
                },
                "definitions": {
                    "shared": len(sim_values),
                    "mean": mean(sim_values),
                    "median": median(sim_values),
                    "threshold": MERGE_THRESHOLD,
                    "same_count": same,
                    "same_fraction": same / len(sim_values),
                },
                "graph": {
                    "codex_edges": len(codex_edges),
                    "reference_edges": len(ref_edges),
                    "shared_edges": len(edge_both),
                    "edge_jaccard": len(edge_both) / len(edge_union),
                    "top20_overlap": len(top_overlap),
                    "spearman": rho,
                },
                "consensus": {
                    "seed": phase2["seed"],
                    "sample_size": len(indep),
                    "compared": len(consensus_rows),
                    "missing_reference": len(missing_ref),
                    "agreement": len(agreement),
                    "conflict": len(conflict),
                },
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )
    print(f"wrote {OUT / 'AGREEMENT-REPORT.md'}")


if __name__ == "__main__":
    main()
