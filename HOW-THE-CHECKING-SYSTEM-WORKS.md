# The full idea — extraction, image handling, and the checking system

*A reply to Chris's questions, and the clearest statement of what this actually is.
Short version: the part scientists care about uses no language model at all, and the
design doesn't depend on Fable — or on any one model.*

---

## 1. What "deterministic" actually means here

Chris is right to press on this, because I was sloppy. There are two very different
claims, and only one of them is true of the part that matters:

- **"A model produces the same output every time"** — not a claim I'd make. Decoding
  is sampled; routing and versions drift. If that's what "deterministic" meant, the
  skepticism would be correct.
- **"The extraction is produced by ordinary code, with no model in the loop"** — this
  *is* the claim, and it's literally true.

The terms, definitions, concept-graph edges, media list, and candidate facts come out
of a ~200-line Python script that parses the Wikipedia dump with regular expressions.
Same dump in → byte-identical files out. A definition is Wikipedia's own lead sentence,
lifted verbatim; an edge is a `[[wikilink]]` between two in-domain articles; the
"foundational" ranking is just in-degree. **No language model wrote any of it.** That's
the sense in which it's deterministic — not "the model is stable," but "there is no
model."

So Chris's guess ("outputs deterministic once a model generates them") is half right and
undersells it: there's nothing to re-generate, because nothing was generated. This is the
strongest card in the whole project and I buried it under a model name.

## 2. Then what is Fable (or any model) for?

Three jobs, all optional and all quarantined:

1. **Redrawing line diagrams** (see §3).
2. **Proposing candidate facts** the deterministic pass couldn't parse — always entered
   at the lowest trust tier, never as truth.
3. **First-pass moderation** — when a human submits a refutation, a model triages whether
   it's a good-faith correction or noise/an attack, so a person isn't hand-sorting spam.
   It flags; it doesn't decide.

Chris asks what's unique to Fable, and whether Codex 5.5 would do the same. **Honest
answer: nothing is unique to Fable, and yes another model would do these jobs.** The
architecture is deliberately model-agnostic — the model is a swappable component behind a
fixed interface, and for the extraction it's swapped out entirely. I was excited about
the current state of the tooling and let the brand stand in for the system. That was the
error.

This also dissolves most of the Fable-specific worries Chris raised — routing,
distillation carve-outs, 30-day retention. The scholarly core sends **nothing** to a
hosted model: it's local parsing of a public dump. The only model touchpoints are
diagram redraws and candidate suggestions, both of which can run on any model, a local
model, or a human. If a vendor's routing or retention terms are unacceptable for a given
deployment, you change the component; the pipeline doesn't notice. (On the specific
model-card claims — routing to a weaker model on "sensitive" topics, retention across
deployments — I'm not going to relay details I can't verify myself. The point is the
design shouldn't depend on the answer, and it doesn't.)

## 3. Images — Chris is right, and the pipeline already agrees with him

The claim was never "vectorize all of Wikipedia's images," and it shouldn't be. The media
step classifies every image and picks a strategy by type:

| Source type | Strategy | Why |
|---|---|---|
| `.svg` (already a vector diagram) | **redraw as our own SVG** | it's a diagram, not a photo — the information is geometric and checkable |
| chart / plot / spectrum / histogram | **rebuild in D3 from the underlying data** | reproduce the *data*, not trace the pixels |
| `.jpg` / `.jpeg` (photograph) | **use as-is if freely licensed, else omit** | never fake or "vectorize" a real photograph |
| anything else | **flag for human review** | don't guess |

So Chris's test image — the JWST Rho Ophiuchi NIRCam frame — is exactly the case the
pipeline **refuses to vectorize**. It's a NASA/ESA/CSA release (freely usable with
attribution), so the strategy is "use the original as-is," full stop. Trying to turn a
star-forming-region photograph into an SVG would be both impossible to do faithfully and
impossible to validate — which is precisely why it isn't attempted. His instinct (line
drawings yes, photographs no) is the design rule, not a gap in it.

Two honest caveats he'd be right to hold us to:

- **A redrawn diagram still has to be checked against the original by a human, ideally a
  domain expert** — and it goes through the same sign-off as a fact (§4). A subtly wrong
  diagram is worse than no diagram. We don't ship a redraw on the model's say-so.
- **Validation is the hard part, and it's why we only attempt the cases where validation
  is feasible.** We can diff a redrawn circuit or free-body diagram against its source and
  have an expert confirm it. We cannot validate a vectorized nebula, so we don't make one.

I'll send real before/after examples of a line-drawing redraw — that's the only honest way
to answer "can it actually do this," and I'd rather be judged on examples than adjectives.

## 4. The checking system

This is the actual point of the project. The extraction is just raw material; trust is
*earned* through a consensus-and-sign-off process modeled on how Wikipedia itself works —
open contribution, transparent provenance, human authority at the end.

**Every fact carries its evidence, not just an assertion.** A fact record stores the
claim, a normalized canonical form, and a list of evidence items — each with its source,
the verbatim passage, a URL, and a trust tier.

**Trust tiers, fixed in config:**

- **trusted** — OpenStax and other vetted textbooks
- **solid** — PubMed, journals, Wikipedia (curated but tertiary — good for breadth, never
  primary authority)
- **low** — general web, and *every* AI model (Claude, Fable, any other). AI is
  permanently low-tier: a candidate, never authoritative on its own.

**Consensus is derived, never declared.** The system computes a fact's status from its
evidence; no one hand-sets "this is true":

- one source → **unverified** (a candidate)
- two or more *independent* sources agree → **agreement**
- partial overlap → **partial**
- any source **refutes** → **conflict**, and it goes to a human review queue

"Independent" is enforced: a `same_publisher` flag stops two OpenStax books from counting
as two votes, so corroboration means genuinely separate origins.

**Disagreement must be sourced.** You cannot refute a fact with an opinion — a REFUTES or
PARTIAL contribution is rejected unless it cites a URL and/or a verbatim passage. This is
what keeps the commons from devolving into vibes.

**Humans are the only path to "verified."** Consensus among sources gets you to
"agreement," but `verified = true` happens only when a person signs off. Sign-offs are
recorded in sidecar files with a SHA-256 hash of the exact content that was signed; if the
underlying fact later changes, the hash no longer matches and the signature is
automatically invalidated. An expert's name is never attached to something they didn't
actually approve, and never silently carried onto edited content.

**Where the AI is allowed to act, and where it isn't:** it may propose candidates (low
tier), cross-check a claim against sources, and triage incoming refutations for good faith.
It may **not** decide truth, raise its own tier, or sign. Those are human acts by
construction, not by policy we hope holds.

So the pitch to a physicist is small and honest: *here is a deterministically extracted
slice of Wikipedia's own definitions and link structure for your field; nothing here is
asserted as true; please flag what's wrong and, where you're willing, sign what's right.*
Their corrections become trusted-tier evidence, and their signatures become the
verification layer. The model never sits in the seat of authority — at most it hands the
expert a draft to reject.

## 5. What I'd actually claim, stripped of hype

- The extraction is real, deterministic, and model-free. (physics: 9,792 terms, 15,500
  edges, 2,028 media refs, 4,686 candidate definitions.)
- Those 4,686 are **candidate definitions**, single-source and unverified — not "facts" yet.
- The concept graph is sparse (~1.6 edges/term); the value is in the high-in-degree core,
  after a noise pass, not the full dump.
- Diagrams can be redrawn and checked; photographs are used as-is or omitted, never faked.
- Fable is incidental. The design depends on no single model, and the part that matters
  depends on none at all.
- The checking system — tiered sources, derived consensus, sourced refutation, human
  sign-off with hash-pinned signatures — is the product. The extraction just feeds it.

If any of that still sounds too good, the right next step isn't more prose — it's me
sending a redrawn-diagram example and a 30-term signed-vs-unsigned glossary slice so it can
be judged on the artifact.
