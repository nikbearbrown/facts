You are an independent implementer running a blind replication experiment. We have a
deterministic pipeline that extracts a physics knowledge slice from a Wikipedia dump
(glossary terms + definitions, a concept graph, a media list, and candidate facts). I
want to find out two things, honestly and quantitatively:

  1. Can you independently perform the same extraction from the same raw data?
  2. How much do your results agree with the existing pipeline's results — and *where
     and why* do they disagree?

Treat this as a scientific replication, not a code-porting task. Work in three phases and
do not skip the blind protocol.

================================================================================
PATHS — locate these yourself before doing anything; print what you found and stop to
confirm if any are missing. Do NOT guess.
================================================================================
- REPO root: /Users/bear/Documents/CoWork/bear-textbooks
- RAW INPUT: the English Wikipedia dump, a JSON-Lines file (one article per line, with at
  least "title" and "text" wikitext fields). Find it by globbing for
  `*pages-articles*.jsonl` at or under REPO (or one directory above it). It is large
  (~25M lines); stream it, never load it whole.
- REFERENCE OUTPUTS (the pipeline you are being compared against) live in
  REPO/facts/physics/ : terms.json, graph.json, facts.json, preview.md
- REFERENCE CODE: REPO/books/ai1-cli/facts/wiki-mine.py and facts_store.py
- YOUR OUTPUT DIR: create REPO/facts/physics_codex/ and write everything there.

================================================================================
BLIND PROTOCOL — read carefully
================================================================================
During PHASE 1 you may NOT open any of these:
  - REPO/facts/physics/*          (the reference outputs)
  - REPO/books/ai1-cli/facts/wiki-mine.py   (the reference extractor)
You may look at facts_store.py ONLY in Phase 3, and ONLY to reuse its comparison helpers.
The point is an independent implementation, not a re-derivation of ours. If you peek, the
agreement number is meaningless. State at the top of your final report whether you held to
this.

================================================================================
PHASE 1 — Independent extraction (your method, your code)
================================================================================
Build your own extractor from the dump and write these three files to physics_codex/.
Match this schema exactly so the outputs are comparable:

terms.json — JSON array, each element:
  {
    "term": <article title with any trailing "(...)" qualifier removed>,
    "page": <article title>,
    "url":  "https://en.wikipedia.org/wiki/<Title_With_Underscores>",
    "definition": <the article's lead sentence, verbatim, marks stripped; null if none parses>,
    "related": [<up to 8 in-physics article titles this page links to>],
    "categories": [<up to 6 of the page's physics categories>],
    "media": [{"file": <filename>, "type": <"diagram"|"chart"|"photo"|"image">,
               "strategy": <"redraw-svg"|"d3-from-data"|"use-if-free-else-omit"|"review">}]
  }

graph.json — {"nodes":[{"term","page","url","in_degree"}], "edges":[[src_page,tgt_page], ...]}
  Edges = wikilinks from one in-physics article to another in-physics article.
  in_degree = number of in-physics pages linking to that node.

facts.json — JSON array of candidate facts, one per usable definition:
  {"canonical": <definition, plain text>, "verbatim": <definition, plain text>,
   "source": "codex", "publisher": null, "url": <page url>,
   "domain": ["physics"], "category": "DEFINITION", "tier": "low"}

Scope / definitions of "physics":
  - Include an article iff at least one of its Wikipedia categories names a physics
    subfield (decide your own keyword set; document it). Exclude redirects and
    works/culture (books, manuscripts, fiction, mythology, films, art, games, songs).
  - A "definition" is the first complete sentence of the lead, starting from the bolded
    subject, with templates/refs/markup removed. If it has no copula (is/are/was/refers
    to/…), treat it as unparsed → null.

Method is YOUR choice, but you MUST document it and you MUST test determinism:
  - Write down whether your extractor is pure code (regex/parse) or uses a language model
    for any step, and exactly which steps.
  - Run your full pipeline TWICE on the same input and diff the outputs. Report whether
    they are byte-identical. If they are not, you used a non-deterministic step — say so
    and quantify the variation.

Print a one-line summary: "<N terms, E edges, M media, F facts>".

================================================================================
PHASE 2 — Independent-knowledge cross-check (this is the scientifically interesting one)
================================================================================
Phase 1 likely agrees with the reference simply because you both read the same Wikipedia
lead sentences — that is reproducibility of one source, not corroboration by a second.
So additionally:

  - Take a RANDOM sample of 100 terms from your terms.json (seed the RNG, record the seed).
  - For each, write a one-sentence definition FROM YOUR OWN MODEL KNOWLEDGE, without
    reading that article's text. Save to physics_codex/independent_defs.json as
    {"term", "page", "model_definition"}.
  - This is a genuinely independent second source (tier "low", source "codex"). We will
    later test how often it agrees with Wikipedia's definition for the same term.

================================================================================
PHASE 3 — Agreement analysis (now you may read the reference outputs + facts_store)
================================================================================
Load REPO/facts/physics/{terms.json,graph.json,facts.json} and your physics_codex/ files.
For an apples-to-apples wording comparison, import the reference's own metric:
    import sys; sys.path.insert(0, "REPO/books/ai1-cli/facts")
    import facts_store as fs   # use fs.wording_similarity and fs.MERGE_THRESHOLD
(If import fails, reimplement token-sort + Jaccard with numbers stripped, threshold 0.82,
and note that you did.)

Compute and report:

A. TERM-SET agreement (match on page title):
   - counts: both, only-reference, only-codex; Jaccard = |both| / |union|.
   - list 15 example titles each side has that the other lacks (to expose scope/filter
     differences).

B. DEFINITION agreement, for the terms present in BOTH:
   - wording_similarity for each shared term; report mean, median, and the fraction
     ≥ MERGE_THRESHOLD (i.e. "the same definition").
   - show the 10 closest matches and the 10 widest disagreements, with both texts side by
     side, and a one-line note on the cause (parsing diff? different lead sentence? page
     ambiguity?).

C. GRAPH agreement:
   - edge-set Jaccard.
   - take the top-20 nodes by in_degree from each side; report the overlap of those two
     sets and the Spearman rank correlation of in_degree over all shared nodes. (Does the
     "foundational core" agree even where the long tail doesn't?)

D. CONSENSUS test (the payoff):
   - For the 100 Phase-2 model_definitions, look up the matching reference fact and run
     fs.wording_similarity against the reference (Wikipedia) definition. Report how many
     would reach "agreement" (independent second source concurs) vs "conflict", with 10
     examples of each. This is the number that tells us whether a *different model's own
     knowledge* corroborates Wikipedia, which is what the checking system actually needs.

================================================================================
DELIVERABLE
================================================================================
Write physics_codex/AGREEMENT-REPORT.md containing, in this order:
  1. Blind-protocol attestation (did you avoid the reference outputs/code in Phases 1–2?).
  2. Your method, stated plainly, and the determinism result (identical on re-run? y/n).
  3. The Phase-1 headline counts next to the reference's
     (reference physics run, for context: 9,792 terms · 15,500 edges · 2,028 media ·
     4,686 facts — do not tune toward these; just report yours beside them).
  4. Sections A–D with the numbers and the concrete examples requested.
  5. A short, honest conclusion in three parts: (i) could you do the extraction at all;
     (ii) how much you agree on reproducing Wikipedia (Phases 1/3A–C); (iii) how much
     your independent knowledge corroborates Wikipedia (Phase 2 / 3D) — and call out, in
     one sentence, the difference between those last two, because they are not the same
     claim.

Constraints: do not modify anything outside physics_codex/. Do not fetch from the network
(the dump is local; Phase-2 definitions come from your own weights, not browsing). Keep
memory bounded by streaming the dump.
