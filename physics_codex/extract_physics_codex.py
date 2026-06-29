#!/usr/bin/env python3
"""Independent Wikipedia physics-slice extractor.

This intentionally does not import or inspect the reference extractor. It streams a
JSONL Wikipedia dump and emits terms.json, graph.json, and facts.json.
"""

from __future__ import annotations

import argparse
import html
import json
import re
from collections import Counter
from pathlib import Path
from urllib.parse import quote


CATEGORY_RE = re.compile(r"\[\[Category:([^\]|]+)")
LINK_RE = re.compile(r"\[\[([^#\]|]+)(?:#[^\]|]*)?(?:\|([^\]]+))?\]\]")
FILE_RE = re.compile(r"\[\[(?:File|Image):([^\]|]+)(?:\|[^\]]*)?\]\]", re.I)
REF_RE = re.compile(r"<ref\b[^>/]*(?:/>|>.*?</ref>)", re.I | re.S)
COMMENT_RE = re.compile(r"<!--.*?-->", re.S)
TEMPLATE_RE = re.compile(r"\{\{[^{}]*\}\}", re.S)
BOLD_RE = re.compile(r"'''")

PHYSICS_CATEGORY_KEYWORDS = [
    "physics",
    "mechanics",
    "classical mechanics",
    "quantum",
    "relativity",
    "thermodynamics",
    "statistical mechanics",
    "electromagnetism",
    "electrodynamics",
    "optics",
    "acoustics",
    "fluid dynamics",
    "fluid mechanics",
    "particle physics",
    "nuclear physics",
    "atomic physics",
    "molecular physics",
    "condensed matter",
    "solid state",
    "plasma physics",
    "geophysics",
    "astrophysics",
    "cosmology",
    "physical cosmology",
    "astronomy",
    "spectroscopy",
    "wave",
    "magnetism",
    "electricity",
    "gravitation",
]

EXCLUDE_CATEGORY_KEYWORDS = [
    "books",
    "novels",
    "fiction",
    "films",
    "television",
    "video games",
    "songs",
    "albums",
    "paintings",
    "sculptures",
    "mythology",
    "manuscripts",
    "works",
]

COPULA_RE = re.compile(
    r"\b(is|are|was|were|refers to|describes|denotes|means|consists of|comprises)\b",
    re.I,
)


def strip_qualifier(title: str) -> str:
    return re.sub(r"\s+\([^)]*\)\s*$", "", title).strip()


def page_url(title: str) -> str:
    return "https://en.wikipedia.org/wiki/" + quote(title.replace(" ", "_"), safe="_()%',:")


def normalize_page(raw: str) -> str:
    page = html.unescape(raw).strip()
    page = page.split("#", 1)[0]
    page = page.replace("_", " ")
    if not page:
        return ""
    if ":" in page:
        prefix = page.split(":", 1)[0].lower()
        if prefix in {"file", "image", "category", "template", "help", "wikipedia", "portal", "special"}:
            return ""
    return page[0].upper() + page[1:]


def remove_templates(text: str) -> str:
    prev = None
    while prev != text:
        prev = text
        text = TEMPLATE_RE.sub(" ", text)
    return text


def clean_markup(text: str) -> str:
    text = COMMENT_RE.sub(" ", text)
    text = REF_RE.sub(" ", text)
    text = remove_templates(text)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\[\[(?:File|Image):[^\]]+\]\]", " ", text, flags=re.I)
    text = re.sub(r"\[\[[^|\]]+\|([^\]]+)\]\]", r"\1", text)
    text = re.sub(r"\[\[([^\]]+)\]\]", r"\1", text)
    text = text.replace("'''", "").replace("''", "")
    text = re.sub(r"\[https?://[^\s\]]+\s*([^\]]*)\]", r"\1", text)
    text = re.sub(r"&nbsp;", " ", text)
    text = html.unescape(text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def first_sentence(text: str) -> str | None:
    text = text.strip()
    if not text:
        return None
    for match in re.finditer(r"(?<=[.!?])\s+(?=[A-Z0-9\"'])", text):
        sentence = text[: match.start()].strip()
        if 40 <= len(sentence) <= 600:
            return sentence
    sentence = text.strip()
    if 40 <= len(sentence) <= 600:
        return sentence
    return None


def lead_definition(wikitext: str) -> str | None:
    start = wikitext.find("'''")
    if start == -1:
        return None
    lead = wikitext[start:]
    for marker in ("\n==", "\n[[Category:"):
        idx = lead.find(marker)
        if idx != -1:
            lead = lead[:idx]
    lead = clean_markup(lead)
    sent = first_sentence(lead)
    if not sent or not COPULA_RE.search(sent):
        return None
    return sent


def categories_for(text: str) -> list[str]:
    out = []
    seen = set()
    for cat in CATEGORY_RE.findall(text):
        cat = clean_markup(cat).strip()
        if cat and cat not in seen:
            out.append(cat)
            seen.add(cat)
    return out


def is_physics_categories(categories: list[str]) -> bool:
    blob = " | ".join(categories).lower()
    if any(key in blob for key in EXCLUDE_CATEGORY_KEYWORDS):
        return False
    return any(key in blob for key in PHYSICS_CATEGORY_KEYWORDS)


def is_redirect(text: str) -> bool:
    return text.lstrip().lower().startswith("#redirect") or "#REDIRECT" in text[:300]


def links_for(text: str) -> list[str]:
    links = []
    seen = set()
    for target, _label in LINK_RE.findall(text):
        page = normalize_page(target)
        if page and page not in seen:
            links.append(page)
            seen.add(page)
    return links


def media_type(filename: str, context: str = "") -> tuple[str, str]:
    blob = f"{filename} {context}".lower()
    if any(k in blob for k in ("chart", "graph", "plot", "histogram")):
        return "chart", "d3-from-data"
    if any(k in blob for k in ("diagram", "schematic", "feynman", "free body", "ray diagram")):
        return "diagram", "redraw-svg"
    if filename.lower().endswith((".jpg", ".jpeg", ".png", ".tif", ".tiff")):
        if any(k in blob for k in ("photo", "portrait", "image", "picture")):
            return "photo", "use-if-free-else-omit"
        return "image", "review"
    if filename.lower().endswith(".svg"):
        return "diagram", "redraw-svg"
    return "image", "review"


def media_for(text: str) -> list[dict]:
    out = []
    seen = set()
    for filename in FILE_RE.findall(text):
        filename = filename.strip()
        if not filename or filename in seen:
            continue
        seen.add(filename)
        typ, strategy = media_type(filename, text[max(0, text.find(filename) - 100) : text.find(filename) + 160])
        out.append({"file": filename, "type": typ, "strategy": strategy})
    return out


def write_json(path: Path, value) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def extract(dump: Path, outdir: Path) -> dict:
    pages: dict[str, dict] = {}
    outlinks: dict[str, list[str]] = {}

    with dump.open("r", encoding="utf-8") as fh:
        for line_no, line in enumerate(fh, 1):
            try:
                article = json.loads(line)
            except json.JSONDecodeError:
                continue
            title = str(article.get("title") or "").strip()
            text = str(article.get("text") or "")
            if not title or is_redirect(text):
                continue
            cats = categories_for(text)
            if not cats or not is_physics_categories(cats):
                continue
            definition = lead_definition(text)
            pages[title] = {
                "term": strip_qualifier(title),
                "page": title,
                "url": page_url(title),
                "definition": definition,
                "categories": cats[:6],
                "media": media_for(text),
            }
            outlinks[title] = links_for(text)

    included = set(pages)
    edges = sorted(
        {
            (src, tgt)
            for src, links in outlinks.items()
            for tgt in links
            if tgt in included and tgt != src
        }
    )
    indeg = Counter(tgt for _src, tgt in edges)

    terms = []
    for page in sorted(pages):
        rec = pages[page]
        related = [t for t in outlinks.get(page, []) if t in included and t != page][:8]
        terms.append({**rec, "related": related})

    nodes = [
        {
            "term": pages[page]["term"],
            "page": page,
            "url": pages[page]["url"],
            "in_degree": int(indeg.get(page, 0)),
        }
        for page in sorted(pages)
    ]
    facts = [
        {
            "canonical": rec["definition"],
            "verbatim": rec["definition"],
            "source": "codex",
            "publisher": None,
            "url": rec["url"],
            "domain": ["physics"],
            "category": "DEFINITION",
            "tier": "low",
        }
        for rec in terms
        if rec.get("definition")
    ]

    outdir.mkdir(parents=True, exist_ok=True)
    write_json(outdir / "terms.json", terms)
    write_json(outdir / "graph.json", {"nodes": nodes, "edges": [[a, b] for a, b in edges]})
    write_json(outdir / "facts.json", facts)
    summary = {
        "terms": len(terms),
        "edges": len(edges),
        "media": sum(len(t["media"]) for t in terms),
        "facts": len(facts),
        "category_keywords": PHYSICS_CATEGORY_KEYWORDS,
    }
    write_json(outdir / "phase1-summary.json", summary)
    return summary


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dump", type=Path, required=True)
    parser.add_argument("--outdir", type=Path, required=True)
    args = parser.parse_args()
    summary = extract(args.dump, args.outdir)
    print(f"{summary['terms']} terms, {summary['edges']} edges, {summary['media']} media, {summary['facts']} facts")


if __name__ == "__main__":
    main()
