# Physics Codex Replication Agreement Report

## Blind-Protocol Attestation

I held to the blind protocol for Phases 1 and 2: I did not open `facts/physics/*` or `books/ai1-cli/facts/wiki-mine.py` before independent extraction and seeded model-definition generation. In Phase 3, I read the reference outputs and imported `facts_store.py` for the comparison metric.

## Method and Determinism

- Phase 1 method: pure deterministic Python using regex/light wikitext cleanup, category-keyword filtering, wikilink extraction, and media filename/context heuristics. No language model was used in Phase 1.

- Physics scope: included pages with at least one category containing a chosen physics/subfield keyword: `physics`, `mechanics`, `classical mechanics`, `quantum`, `relativity`, `thermodynamics`, `statistical mechanics`, `electromagnetism`, `electrodynamics`, `optics`, `acoustics`, `fluid dynamics`, `fluid mechanics`, `particle physics`, `nuclear physics`, `atomic physics`, `molecular physics`, `condensed matter`, `solid state`, `plasma physics`, `geophysics`, `astrophysics`, `cosmology`, `physical cosmology`, `astronomy`, `spectroscopy`, `wave`, `magnetism`, `electricity`, `gravitation`.

- Exclusion method: redirects plus category strings suggesting works/culture were filtered, but namespace pages and biography/music/sports leakage were not fully removed; that is a real source of disagreement.

- Phase 2 method: seeded random sample (`seed=20260611`) and definitions authored from page/term labels only, not article text.

- Determinism: two full runs were byte-identical for `terms.json`, `graph.json`, `facts.json`, and `phase1-summary.json`.

- Metric: Imported facts_store.wording_similarity and facts_store.MERGE_THRESHOLD.

## Phase-1 Headline Counts

| Run | Terms | Edges | Media | Facts |
| --- | --- | --- | --- | --- |
| Reference context | 9,792 | 15,500 | 2,028 | 4,686 |
| Codex independent | 26,071 | 52,432 | 5,404 | 11,252 |

One-line Phase 1 summary: 26071 terms, 52432 edges, 5404 media, 11252 facts

## A. Term-Set Agreement

- Both: 9,544
- Only reference: 248
- Only Codex: 16,527
- Jaccard: 0.3626

Reference-only examples:

- 1964 PRL symmetry breaking papers
- A Dynamical Theory of the Electromagnetic Field
- Absorption refrigerator
- Activity coefficient
- Adiabatic conductivity
- Air separation
- Albert Einstein Archives
- Alice Golsen
- Alice and Bob
- Allam power cycle
- Alpher–Bethe–Gamow paper
- An Introduction to Mechanics
- Annus mirabilis papers
- Antimatter
- Antoine equation

Codex-only examples:

- 'Til Tuesday
- (α/Fe) versus (Fe/H) diagram
- 1-Butyl-3-methylimidazolium tetrachloroferrate
- 1757 heatwave
- 1783 Great Meteor
- 1808 United Kingdom heatwave
- 1874 Transit of Venus Expedition to Campbell Island
- 1874 Transit of Venus Expedition to Hawaii
- 1888 Northwest United States cold wave
- 1893 Tulane Olive and Blue football team
- 1894 Tulane Olive and Blue football team
- 1895 Tulane Olive and Blue football team
- 1896 Eastern North America heat wave
- 1896 Tulane Olive and Blue football team
- 1898 Tulane Olive and Blue football team

## B. Definition Agreement on Shared Terms

- Shared terms scored: 9,544
- Mean wording similarity: 0.2733
- Median wording similarity: 0.0000
- Fraction >= MERGE_THRESHOLD (0.82): 0.0363 (346/9,544)

Closest matches:

| Score | Page | Codex | Reference | Cause |
| --- | --- | --- | --- | --- |
| 1.000 | Z-scan technique | z-scan technique is used to measure the non-linear index n ==Eclipsing z-scan== This method is similar to the closed z-scan method, however the sensitivity of the system is increased by only looking at the outer edges of the beam by blocking out the central... | z-scan technique is used to measure the non-linear index n ==Eclipsing z-scan== This method is similar to the closed z-scan method, however the sensitivity of the system is increased by only looking at the outer edges of the beam by blocking out the central... | mostly same lead with cleanup/truncation differences |
| 1.000 | X-ray diffraction | X-ray diffraction is a generic term for phenomena associated with changes in the direction of X-ray beams due to interactions with the electrons around atoms. | X-ray diffraction is a generic term for phenomena associated with changes in the direction of X-ray beams due to interactions with the electrons around atoms. | mostly same lead with cleanup/truncation differences |
| 1.000 | Wykeham Professor | Wykeham Professorship in Logic was established in 1859, although it was not known as the Wykeham chair until later. | Wykeham Professorship in Logic was established in 1859, although it was not known as the Wykeham chair until later. | mostly same lead with cleanup/truncation differences |
| 1.000 | Wladyslaw Opechowski | Wladyslaw Opechowski (Polish: Władysław Opęchowski, 10 March 1911 – 27 September 1993) was a Polish and Canadian theoretical physicist. | Wladyslaw Opechowski (Polish: Władysław Opęchowski, 10 March 1911 – 27 September 1993) was a Polish and Canadian theoretical physicist. | mostly same lead with cleanup/truncation differences |
| 1.000 | Weak localization | Weak localization is a physical effect which occurs in disordered electronic systems at very low temperatures. | Weak localization is a physical effect which occurs in disordered electronic systems at very low temperatures. | mostly same lead with cleanup/truncation differences |
| 1.000 | Waveguide | waveguide is a structure that guides waves by restricting the direction of transmission of energy. | waveguide is a structure that guides waves by restricting the direction of transmission of energy. | mostly same lead with cleanup/truncation differences |
| 1.000 | Vogel–Fulcher–Tammann equation | Vogel–Fulcher–Tammann equation, also known as Vogel–Fulcher–Tammann–Hesse equation or Vogel–Fulcher equation (abbreviated: VFT equation), is used to describe the viscosity of liquids as a function of temperature, and especially its strongly temperature... | Vogel–Fulcher–Tammann equation, also known as Vogel–Fulcher–Tammann–Hesse equation or Vogel–Fulcher equation (abbreviated: VFT equation), is used to describe the viscosity of liquids as a function of temperature, and especially its strongly temperature... | mostly same lead with cleanup/truncation differences |
| 1.000 | Viscoelasticity | Viscoelasticity is a material property that combines both viscous and elastic characteristics. | Viscoelasticity is a material property that combines both viscous and elastic characteristics. | mostly same lead with cleanup/truncation differences |
| 1.000 | Vector meson dominance | vector meson dominance (VMD) was a model developed by J. | vector meson dominance (VMD) was a model developed by [[J. | different parsed lead sentence or wording |
| 1.000 | VSim | VSim is a cross-platform computational framework for multi-physics, compatible with Windows, Linux, and macOS. | VSim is a cross-platform computational framework for multi-physics, compatible with Windows, Linux, and macOS. | mostly same lead with cleanup/truncation differences |

Widest disagreements:

| Score | Page | Codex | Reference | Cause |
| --- | --- | --- | --- | --- |
| 0.000 | (−1)F |  |  | both definitions missing |
| 0.000 | 1/N expansion |  |  | both definitions missing |
| 0.000 | 1901 Nobel Prize in Physics |  |  | both definitions missing |
| 0.000 | 1QBit |  |  | both definitions missing |
| 0.000 | 2011 OPERA faster-than-light neutrino anomaly |  |  | both definitions missing |
| 0.000 | 2019 revision of the SI |  |  | both definitions missing |
| 0.000 | 331 model |  |  | both definitions missing |
| 0.000 | 4D N = 1 global supersymmetry | 4D Rather than working with superfields, this approach works with multiplets, which are sets of fields on which the supersymmetry algebra is realized. |  | reference has no parsed definition |
| 0.000 | 4D N = 1 supergravity | 4D In all these theories, the particular properties of the resulting supergravity theory such as the Kähler potential and the superpotential are fixed by the geometry of the compact manifold. ==Notes== ==References== Category:Supersymmetric quantum field... |  | reference has no parsed definition |
| 0.000 | 5GBioShield |  |  | both definitions missing |

## C. Graph Agreement

- Codex edges: 52,432
- Reference edges: 15,500
- Shared edges: 14,888
- Edge-set Jaccard: 0.2807
- Top-20 in-degree overlap: 6/20
- Spearman rank correlation over shared nodes: 0.9332

Top-20 overlap nodes:

- Condensed matter physics
- Optics
- Particle physics
- Physics
- Quantum mechanics
- Theoretical physics

Reference top 20 by in-degree:

- Physics (302)
- List of physics awards (106)
- Theoretical physics (87)
- CERN (83)
- Quantum mechanics (77)
- Standard Model (72)
- Spin (physics) (68)
- Moscow Institute of Physics and Technology (67)
- Nobel Prize in Physics (61)
- Condensed matter physics (59)
- Institute of Physics (59)
- Optics (55)
- INSPIRE-HEP (51)
- Particle physics (51)
- American Institute of Physics (50)
- Nuclear physics (44)
- Quantum computing (40)
- Hamiltonian (quantum mechanics) (38)
- Plasma (physics) (37)
- Atomic nucleus (33)

Codex top 20 by in-degree:

- Physics (1021)
- New wave music (628)
- Quantum mechanics (451)
- Astronomy (370)
- Theoretical physics (302)
- Particle physics (285)
- General relativity (275)
- Electron (251)
- Tulane Green Wave football (243)
- Fluid dynamics (241)
- Quantum field theory (219)
- Optics (207)
- Astrophysics (201)
- Condensed matter physics (190)
- Magnetic field (176)
- Energy (149)
- Spectroscopy (138)
- Thermodynamics (135)
- Photon (131)
- Star (130)

## D. Consensus Test

- Phase-2 sample seed: 20260611
- Sample size: 100
- Compared to reference definitions/facts: 12
- Missing reference definition/fact: 88
- Agreement (>= 0.82): 0
- Conflict (< 0.82): 12

Agreement examples:

None reached the merge threshold.

Conflict examples:

| Score | Page | Model | Reference |
| --- | --- | --- | --- |
| 0.081 | Field equation | A field equation is a mathematical equation describing how a physical field behaves and responds to sources. | field equation is a [partial differential equation](https://en.wikipedia.org/wiki/Partial_differential_equation) which determines the dynamics of a [physical field](https://en.wikipedia.org/wiki/Physical_field), specifically the time evolution and spatial... |
| 0.094 | American Optical Company | American Optical Company was a company associated with optical instruments and eyewear. | American Optical Company, also known as AO Eyewear, is an American luxury [eyewear](https://en.wikipedia.org/wiki/Eyewear) and [sunglass](https://en.wikipedia.org/wiki/Sunglass) company based in [Vernon Hills,... |
| 0.103 | Anderson impurity model | The Anderson impurity model describes a localized electronic state interacting with a continuum of conduction electrons. | Anderson impurity model, named after [Philip Warren Anderson](https://en.wikipedia.org/wiki/Philip_Warren_Anderson), is a [Hamiltonian](https://en.wikipedia.org/wiki/Hamiltonian_(quantum_mechanics)) that is used to describe [magnetic... |
| 0.130 | Classification of electromagnetic fields | Classification of electromagnetic fields groups electromagnetic fields by invariants, sources, or transformation properties. | classification of electromagnetic fields is a [pointwise](https://en.wikipedia.org/wiki/Pointwise) classification of [bivector](https://en.wikipedia.org/wiki/Bivector)s at each point of a [[Pseudo-Riemannian manifold#Lorentzian manifold|Lorentzian manifold]]. |
| 0.152 | Coupling loss | Coupling loss is the loss of signal power that occurs when energy is transferred imperfectly between systems or waveguides. | Coupling loss, also known as connection loss, is the loss that occurs when [energy](https://en.wikipedia.org/wiki/Energy) is transferred from one [circuit](https://en.wikipedia.org/wiki/Electrical_circuit), circuit element, or medium to another. |
| 0.157 | Extra dimensions | Extra dimensions are additional spatial or spacetime dimensions beyond the familiar three spatial dimensions and time. | extra dimensions are proposed additional [space](https://en.wikipedia.org/wiki/Space) or [time](https://en.wikipedia.org/wiki/Time) [dimension](https://en.wikipedia.org/wiki/Dimension)s beyond the (3 * [Universal extra... |
| 0.234 | No-hiding theorem | The no-hiding theorem is a result in quantum information theory stating that information apparently lost from a subsystem is preserved in correlations with the rest of the quantum system. | no-hiding theorem denotes the fact that one may augment the unused dimension of the environment Hilbert space by zero vectors. |
| 0.245 | Quantum catalyst | A quantum catalyst is an auxiliary quantum resource that enables a transformation without being consumed. | quantum catalyst is a special [ancillary](https://en.wikipedia.org/wiki/Ancilla_bit) [quantum state](https://en.wikipedia.org/wiki/Quantum_state) whose presence enables certain local [transformations](https://en.wikipedia.org/wiki/Transformation_(function))... |
| 0.273 | Lariat chain | A lariat chain is a linked or looped molecular or topological structure resembling a lasso. | lariat chain is a loop of chain that hangs off, and is spun by a wheel. |
| 0.281 | Quantum memory | Quantum memory is a device or system that stores quantum states while preserving quantum coherence. | quantum memory is the [quantum-mechanical](https://en.wikipedia.org/wiki/Quantum_mechanics) version of ordinary [computer memory](https://en.wikipedia.org/wiki/Computer_memory). |

Missing-reference examples:

- Stellar population: A stellar population is a class of stars grouped by age, chemical composition, and galactic location.
- Structural acoustics: Structural acoustics is the study of sound generation, transmission, and vibration in solid structures.
- Eloy Salgado: Eloy Salgado is a person associated with a biographical topic rather than a physics concept.
- Konrad Kapler: Konrad Kapler is a named individual and not, by itself, a physics concept.
- Mike Gailey: Mike Gailey is a named individual and not, by itself, a physics concept.
- Nigel Scrutton: Nigel Scrutton is a scientist known for work in chemical biology and enzymology.
- Volumetric flow rate: Volumetric flow rate is the volume of fluid passing through a surface per unit time.
- Peter Hattrup: Peter Hattrup is a named individual and not, by itself, a physics concept.
- Category:Drinking establishments in the United States: This is a Wikipedia category for drinking establishments in the United States, not a physics concept.
- Stefan Marinov: Stefan Marinov was a physicist and controversial researcher associated with electromagnetism and relativity claims.

## Conclusion

1. Could Codex do the extraction at all? Yes: it streamed the local dump, produced the required schemas, and generated deterministic outputs.

2. How much did it reproduce Wikipedia extraction? Only partially: exact wording agreement is high where page scope overlaps, but term-set and graph agreement are strongly affected by my broader category filter and namespace/person/culture leakage.

3. How much did independent model knowledge corroborate Wikipedia? The Phase-2 model-definition agreement is a separate, lower-bar corroboration test; it measures whether an independently authored definition matches Wikipedia, not whether two extractors parsed the same source the same way.
