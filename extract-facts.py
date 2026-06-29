#!/usr/bin/env python3
"""extract-facts.py — mine vetted textbooks into a shared fact dictionary.

Reads an OpenStax CNXML book (collection.xml + modules), extracts atomic,
decontextualized facts via the Anthropic API, cites each to its source with a
trust tier, and merges them into facts.json with a DERIVED consensus:

  1 supporting source      -> consensus "unverified"  (candidate)
  2+ supporting sources    -> consensus "agreement"   (corroborated)
  same substance, diff precision -> "partial"
  any refuting source      -> consensus "conflict"    (human review queue)

Sources are named and tiered (facts-sources.yaml); weights are deferred.
Nothing is human-verified by extraction — OpenStax facts are "source-attested".

  python extract-facts.py ../books/osbooks-anatomy-physiology            # calibrate: first module, then STOP
  python extract-facts.py ../books/osbooks-anatomy-physiology --module m45981
  python extract-facts.py ../books/osbooks-anatomy-physiology --all
  python extract-facts.py ../books/osbooks-biology-bundle --collection biology-2e --all

Key from .env (this dir or parent) or ANTHROPIC_API_KEY env var.
"""
import argparse
import datetime
import json
import os
import re
import sys
import xml.etree.ElementTree as ET

try:
    import requests, yaml
except ImportError as e:
    print(f"Missing dependency: {e}\nRun: pip install requests pyyaml")
    sys.exit(1)

HERE = os.path.dirname(os.path.abspath(__file__))
FACTS_JSON = os.path.join(HERE, "facts.json")
SOURCES_YAML = os.path.join(HERE, "facts-sources.yaml")
COL = "{http://cnx.rice.edu/collxml}"
MD = "{http://cnx.rice.edu/mdml}"
CN = "{http://cnx.rice.edu/cnxml}"
API_URL = "https://api.anthropic.com/v1/messages"
MODEL = "claude-opus-4-6"
ANTHROPIC_VERSION = "2023-06-01"
TODAY = datetime.date.today().isoformat()

SYSTEM_PROMPT = """You extract atomic, citable FACTS from a vetted textbook section. A fact is a single
declarative claim that is true independent of the surrounding text.

Rules:
- ATOMIC: one claim per fact. Split compound sentences.
- DECONTEXTUALIZED: rewrite into a standalone present-tense statement. Resolve pronouns and
  "this/these" references ("This process needs ATP" -> name the process). A reader must understand
  the fact with no other context.
- GROUNDED: every fact must be directly supported by a sentence in the provided text. Put that exact
  sentence in "verbatim". Do NOT invent facts or add outside knowledge.
- Prefer definitions, constants, quantities, structural/functional relationships, mechanisms, and
  classifications. Skip narrative, motivation, exercises, and figure-only captions.
- Mark "stable": true for definitions, constants, anatomy, historical dates; false for statistics,
  guidelines, approval status, or anything that changes over time.

Return ONLY a JSON array. No preamble, no fences. Schema per fact:
{
  "canonical": "standalone present-tense statement",
  "verbatim": "the exact supporting sentence from the text",
  "domain": ["one or two subject tags"],
  "stable": true,
  "category": "BASIC" | "DEFINITION" | "QUANTITY" | "MECHANISM" | "CLASSIFICATION"
}"""

USER_TEMPLATE = """Book: {book}
Section: {chapter} — {module_title}

Extract the atomic facts from this section text:

{text}"""


# ---------- sources / tiers ----------
def load_sources():
    if os.path.exists(SOURCES_YAML):
        return (yaml.safe_load(open(SOURCES_YAML)) or {}).get("sources", {})
    return {}


def source_meta(name, sources):
    s = sources.get(name, sources.get("unknown", {"tier": "low", "publisher": None}))
    return s.get("tier", "low"), s.get("publisher")


# ---------- env ----------
def load_env():
    for path in (os.path.join(HERE, ".env"), os.path.join(os.path.dirname(HERE), ".env")):
        if os.path.exists(path):
            for line in open(path, encoding="utf-8"):
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


# ---------- collection parsing ----------
def find_collection(book_dir, name=None):
    cdir = os.path.join(book_dir, "collections")
    cols = sorted(f for f in os.listdir(cdir) if f.endswith(".xml"))
    if name:
        cols = [c for c in cols if name in c]
    if not cols:
        sys.exit(f"No collection found in {cdir}" + (f" matching '{name}'" if name else ""))
    return os.path.join(cdir, cols[0])


def parse_collection(path):
    root = ET.parse(path).getroot()
    slug = root.findtext(f".//{MD}slug") or "openstax-book"
    title = root.findtext(f".//{MD}title") or slug
    pairs = []  # (chapter_title, module_id)

    def walk(el, chapter):
        for child in el:
            tag = child.tag.replace(COL, "")
            if tag == "module":
                pairs.append((chapter, child.get("document")))
            elif tag == "subcollection":
                t = child.findtext(f"{MD}title") or chapter
                c = child.find(f"{COL}content")
                if c is not None:
                    walk(c, t)
            elif tag == "content":
                walk(child, chapter)

    content = root.find(f"{COL}content")
    if content is not None:
        walk(content, "(front matter)")
    return slug, title, pairs


def module_text(book_dir, module_id):
    path = os.path.join(book_dir, "modules", module_id, "index.cnxml")
    root = ET.parse(path).getroot()
    mtitle = root.findtext(f"{CN}title") or module_id
    content = root.find(f"{CN}content")
    text = " ".join(t.strip() for t in content.itertext() if t.strip()) if content is not None else ""
    text = re.sub(r"\s+", " ", text).strip()
    return mtitle, text


# ---------- fact model ----------
def slugify(s):
    s = re.sub(r"[^\w\s-]", "", s.lower())
    return re.sub(r"[\s_-]+", "-", s).strip("-")[:60] or "fact"


def normalize(s):
    return re.sub(r"\s+", " ", re.sub(r"[^\w\s]", "", s.lower())).strip()


# ---------- semantic-ish dedup (stdlib: wording similarity + numeric guard) ----------
import difflib

MERGE_THRESHOLD = 0.82   # wording this close (numbers aside) = same claim
NEAR_THRESHOLD = 0.70    # close-but-not-sure = flag possible duplicate for review
_STOP = set("a an the is are was were be been being of to in on at by for with as that this these "
            "those it its and or not from into within can may will which who whose".split())


def _content_tokens(s):
    return [t for t in re.findall(r"[a-z]+", s.lower()) if t not in _STOP]


def numbers(s):
    return set(re.findall(r"\d+(?:\.\d+)?", s))


def _strip_numbers(s):
    return re.sub(r"\d+(?:\.\d+)?", "", s)


def wording_similarity(a, b):
    """0..1 similarity of wording, numbers ignored. Token-sort ratio + Jaccard."""
    ta, tb = _content_tokens(_strip_numbers(a)), _content_tokens(_strip_numbers(b))
    if not ta or not tb:
        return 0.0
    seq = difflib.SequenceMatcher(None, " ".join(sorted(ta)), " ".join(sorted(tb))).ratio()
    A, B = set(ta), set(tb)
    jac = len(A & B) / len(A | B)
    return 0.5 * seq + 0.5 * jac


def recompute_consensus(fact, sources):
    ev = fact["evidence"]
    # a "vote" = a distinct SOURCE (a specific book/page), not a publisher.
    supporters = {e["source"] for e in ev if e.get("verdict") == "SUPPORTS"}
    # same_publisher: do all supporting votes come from one publisher (e.g. all OpenStax)?
    publishers = {(e.get("publisher") or e["source"]) for e in ev if e.get("verdict") == "SUPPORTS"}
    has_refute = any(e.get("verdict") == "REFUTES" for e in ev)
    has_partial = any(e.get("verdict") == "PARTIAL" for e in ev)
    votes = len(supporters)
    if has_refute:
        consensus = "conflict"
    elif votes >= 2:
        consensus = "agreement"
    elif has_partial and votes >= 1:
        consensus = "partial"
    else:
        consensus = "unverified"
    fact["votes"] = votes
    fact["consensus"] = consensus
    fact["same_publisher"] = (len(publishers) <= 1)   # agreement within one publisher is weaker
    fact["needs_review"] = (consensus == "conflict")
    return fact


def make_fact(extracted, citation, tier, sources):
    fact = {
        "fact_id": slugify("-".join(extracted.get("domain", ["gen"])[:1] + [extracted["canonical"]])),
        "canonical": extracted["canonical"].strip(),
        "domain": extracted.get("domain", []),
        "stable": bool(extracted.get("stable", True)),
        "status": "source-attested",        # never human-verified by extraction
        "verified": False,
        "verified_by": None, "verified_at": None, "human_note": None,
        "consensus": "unverified", "votes": 0, "same_publisher": True, "needs_review": False,
        "evidence": [{
            **citation,
            "tier": tier,
            "verbatim": extracted.get("verbatim", "").strip(),
            "retrieved": TODAY,
            "verdict": "SUPPORTS",
        }],
        "books": [],
        "category": extracted.get("category", "BASIC"),
        "expires": None,
    }
    return recompute_consensus(fact, sources)


def _append_evidence(fact, new_fact, sources):
    sig = {(e["source"], e.get("module")) for e in fact["evidence"]}
    for e in new_fact["evidence"]:
        if (e["source"], e.get("module")) not in sig:
            fact["evidence"].append(e)
    recompute_consensus(fact, sources)


def merge_fact(facts, new_fact, sources):
    """Match by wording similarity (numbers aside). Returns the action taken:
      'merged'                  — same claim, same numbers -> evidence appended
      'flagged-numeric-conflict'— same wording, DIFFERENT numbers -> kept separate, review
      'added-near-dup'          — close but uncertain -> kept, flagged possible duplicate
      'added'                   — new distinct fact
    """
    can = new_fact["canonical"]
    best_sim, best = 0.0, None
    for f in facts:
        sim = 1.0 if normalize(f["canonical"]) == normalize(can) else wording_similarity(can, f["canonical"])
        if sim > best_sim:
            best_sim, best = sim, f

    if best is not None and best_sim >= MERGE_THRESHOLD:
        if numbers(can) == numbers(best["canonical"]):
            _append_evidence(best, new_fact, sources)
            return "merged"
        # same wording, different quantity -> likely contradiction, do NOT merge
        new_fact["needs_review"] = True
        new_fact["numeric_conflict_with"] = best["fact_id"]
        facts.append(new_fact)
        return "flagged-numeric-conflict"

    if best is not None and best_sim >= NEAR_THRESHOLD:
        new_fact["needs_review"] = True
        new_fact["possible_duplicate_of"] = best["fact_id"]
        facts.append(new_fact)
        return "added-near-dup"

    facts.append(new_fact)
    return "added"


# ---------- extraction ----------
def call_api(book, chapter, module_title, text):
    key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    if not key:
        print("ERROR: ANTHROPIC_API_KEY not set (needed to extract facts).")
        sys.exit(1)
    body = {"model": MODEL, "max_tokens": 4096, "system": SYSTEM_PROMPT,
            "messages": [{"role": "user", "content": USER_TEMPLATE.format(
                book=book, chapter=chapter, module_title=module_title, text=text)}]}
    headers = {"x-api-key": key, "anthropic-version": ANTHROPIC_VERSION, "content-type": "application/json"}
    resp = requests.post(API_URL, headers=headers, json=body, timeout=120)
    resp.raise_for_status()
    raw = "".join(b.get("text", "") for b in resp.json().get("content", []) if b.get("type") == "text")
    raw = re.sub(r"^```[a-z]*\n?|\n?```$", "", raw.strip())
    return json.loads(raw)


def main():
    ap = argparse.ArgumentParser(description="Extract facts from an OpenStax CNXML book.")
    ap.add_argument("book_dir", help="path to an osbooks-* repo")
    ap.add_argument("--collection", help="collection name substring (for bundles)")
    ap.add_argument("--module", help="extract one module by id")
    ap.add_argument("--limit", type=int, help="first N modules")
    ap.add_argument("--all", action="store_true", help="all modules in the collection")
    args = ap.parse_args()

    load_env()
    sources = load_sources()
    repo = os.path.basename(os.path.normpath(args.book_dir))
    col_path = find_collection(args.book_dir, args.collection)
    slug, title, pairs = parse_collection(col_path)
    print(f"Book: {title}  | slug: {slug} | repo: {repo} | modules: {len(pairs)}")

    if args.module:
        targets = [(c, m) for c, m in pairs if m == args.module] or [("", args.module)]
    elif args.all:
        targets = pairs
    elif args.limit:
        targets = pairs[:args.limit]
    else:
        # calibration: first real content module (skip front matter)
        content = [(c, m) for c, m in pairs if "front" not in c.lower()]
        targets = (content or pairs)[:1]

    facts = json.load(open(FACTS_JSON, encoding="utf-8"))
    actions = {}
    for chapter, module_id in targets:
        mtitle, text = module_text(args.book_dir, module_id)
        if len(text) < 200:
            print(f"  skip {module_id} ({mtitle}): too short")
            continue
        url = f"https://openstax.org/books/{slug}"
        # source = the specific book (so two different OpenStax books = two votes);
        # publisher = openstax (so they're still flagged same_publisher).
        citation = {"source": slug, "publisher": "openstax", "book": slug,
                    "repo": repo, "module": module_id, "url": url}
        tier, _ = source_meta("openstax", sources)
        try:
            extracted = call_api(title, chapter, mtitle, text)
        except Exception as e:
            print(f"  ERROR {module_id}: {e}")
            continue
        for ex in extracted:
            if not ex.get("canonical") or not ex.get("verbatim"):
                continue
            r = merge_fact(facts, make_fact(ex, citation, tier, sources), sources)
            actions[r] = actions.get(r, 0) + 1
        print(f"  {module_id} ({mtitle[:40]}): +{len(extracted)} extracted")

    json.dump(facts, open(FACTS_JSON, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
    review = [f for f in facts if f.get("needs_review")]
    print(f"\nfacts.json now {len(facts)} facts")
    print("  this run: " + ", ".join(f"{k}={v}" for k, v in sorted(actions.items())) or "  (no changes)")
    print(f"  consensus: agreement={sum(1 for f in facts if f['consensus']=='agreement')}"
          f"  partial={sum(1 for f in facts if f['consensus']=='partial')}"
          f"  unverified={sum(1 for f in facts if f['consensus']=='unverified')}"
          f"  conflict={sum(1 for f in facts if f['consensus']=='conflict')}")
    print(f"  human review queue (needs_review): {len(review)}"
          f"  [conflicts, numeric mismatches, possible duplicates]")
    if not args.all and not args.module and not args.limit:
        print("\nCALIBRATION: review the new facts in facts.json — are they atomic, decontextualized,\n"
              "and is each 'verbatim' actually present in the source? Then run --all to batch the book.")


if __name__ == "__main__":
    main()
