#!/usr/bin/env python3
"""Write seeded Phase-2 independent definitions.

Definitions were authored from page/term labels only, without consulting the
article text or the reference outputs.
"""

from __future__ import annotations

import json
from pathlib import Path


SEED = 20260611

DEFS = [
    ("No-hiding theorem", "No-hiding theorem", "The no-hiding theorem is a result in quantum information theory stating that information apparently lost from a subsystem is preserved in correlations with the rest of the quantum system."),
    ("Stellar population", "Stellar population", "A stellar population is a class of stars grouped by age, chemical composition, and galactic location."),
    ("Structural acoustics", "Structural acoustics", "Structural acoustics is the study of sound generation, transmission, and vibration in solid structures."),
    ("Eloy Salgado", "Eloy Salgado", "Eloy Salgado is a person associated with a biographical topic rather than a physics concept."),
    ("Konrad Kapler", "Konrad Kapler", "Konrad Kapler is a named individual and not, by itself, a physics concept."),
    ("Mike Gailey", "Mike Gailey", "Mike Gailey is a named individual and not, by itself, a physics concept."),
    ("Nigel Scrutton", "Nigel Scrutton", "Nigel Scrutton is a scientist known for work in chemical biology and enzymology."),
    ("Volumetric flow rate", "Volumetric flow rate", "Volumetric flow rate is the volume of fluid passing through a surface per unit time."),
    ("Peter Hattrup", "Peter Hattrup", "Peter Hattrup is a named individual and not, by itself, a physics concept."),
    ("Coupling loss", "Coupling loss", "Coupling loss is the loss of signal power that occurs when energy is transferred imperfectly between systems or waveguides."),
    ("Category:Drinking establishments in the United States", "Category:Drinking establishments in the United States", "This is a Wikipedia category for drinking establishments in the United States, not a physics concept."),
    ("Stefan Marinov", "Stefan Marinov", "Stefan Marinov was a physicist and controversial researcher associated with electromagnetism and relativity claims."),
    ("Presidential Commission on the Status of Women", "Presidential Commission on the Status of Women", "The Presidential Commission on the Status of Women was a United States commission on women's rights and social policy."),
    ("Racah Lectures in Physics", "Racah Lectures in Physics", "The Racah Lectures in Physics are a named lecture series in physics."),
    ("Category:Kinetics", "Category:Kinetics (physics)", "Kinetics in physics is the study of motion and its causes, often overlapping with dynamics."),
    ("2018 Tulane Green Wave football team", "2018 Tulane Green Wave football team", "The 2018 Tulane Green Wave football team was a college football team, not a physics concept."),
    ("American Optical Company", "American Optical Company", "American Optical Company was a company associated with optical instruments and eyewear."),
    ("Ash Code", "Ash Code", "Ash Code is a musical group name rather than a physics concept."),
    ("Light scattering by particles", "Light scattering by particles", "Light scattering by particles is the deflection and redistribution of light caused by interaction with small particles."),
    ("Zhou Heng", "Zhou Heng (footballer)", "Zhou Heng is a footballer and not a physics concept."),
    ("Acoustic music", "Acoustic music", "Acoustic music is music produced primarily by non-electronic instruments."),
    ("Two-dimensional electronic spectroscopy", "Two-dimensional electronic spectroscopy", "Two-dimensional electronic spectroscopy is an ultrafast spectroscopy technique that correlates excitation and emission frequencies to study electronic dynamics."),
    ("Complex spacetime", "Complex spacetime", "Complex spacetime is a theoretical extension of spacetime in which coordinates or structures may be treated as complex-valued."),
    ("María Cristina Pineda Suazo", "María Cristina Pineda Suazo", "María Cristina Pineda Suazo is a named individual and not, by itself, a physics concept."),
    ("Lariat chain", "Lariat chain", "A lariat chain is a linked or looped molecular or topological structure resembling a lasso."),
    ("Moev", "Moev", "Moev is a musical group and not a physics concept."),
    ("Extra dimensions", "Extra dimensions", "Extra dimensions are additional spatial or spacetime dimensions beyond the familiar three spatial dimensions and time."),
    ("Gordon D. Love", "Gordon D. Love", "Gordon D. Love is a scientist associated with optics and visual science."),
    ("Outline of geophysics", "Outline of geophysics", "An outline of geophysics is an organized topical guide to the physics of Earth and its environment."),
    ("Field equation", "Field equation", "A field equation is a mathematical equation describing how a physical field behaves and responds to sources."),
    ("Line of force", "Line of force", "A line of force is a curve whose tangent indicates the direction of a force field at each point."),
    ("Convection", "Convection", "Convection is heat or mass transfer caused by the bulk motion of a fluid."),
    ("Personality", "Personality", "Personality is the characteristic pattern of thoughts, feelings, and behaviors of an individual."),
    ("Neue Deutsche Todeskunst", "Neue Deutsche Todeskunst", "Neue Deutsche Todeskunst is a music genre and not a physics concept."),
    ("Ali Moustafa Mosharafa", "Ali Moustafa Mosharafa", "Ali Moustafa Mosharafa was an Egyptian theoretical physicist."),
    ("Mettingham", "Mettingham", "Mettingham is a place name and not a physics concept."),
    ("Category:History of thermodynamics", "Category:History of thermodynamics", "The history of thermodynamics concerns the development of concepts of heat, work, energy, entropy, and temperature."),
    ("Gauss's method", "Gauss's method", "Gauss's method usually refers to a mathematical method associated with Carl Friedrich Gauss, such as elimination or orbit determination."),
    ("Category:Project-Class physics pages", "Category:Project-Class physics pages", "This is a Wikipedia maintenance category for physics pages, not a physics concept."),
    ("Jerzy Plebański", "Jerzy Plebański", "Jerzy Plebański was a theoretical physicist known for work in general relativity and mathematical physics."),
    ("Experiments in Fluids", "Experiments in Fluids", "Experiments in Fluids is a scientific journal focused on experimental fluid mechanics."),
    ("Abdiweli Hersi Indhoguran", "Abdiweli Hersi Indhoguran", "Abdiweli Hersi Indhoguran is a named individual and not a physics concept."),
    ("Rayleigh's equation", "Rayleigh's equation (fluid dynamics)", "Rayleigh's equation in fluid dynamics describes aspects of inviscid shear flow stability."),
    ("Charlotte Marsh", "Charlotte Marsh", "Charlotte Marsh is a historical person and not a physics concept."),
    ("Wikipedia:WikiProject Astronomy in The Signpost", "Wikipedia:WikiProject Astronomy in The Signpost", "This is a Wikipedia project/news page about astronomy editing rather than a physics concept."),
    ("Basis set superposition error", "Basis set superposition error", "Basis set superposition error is an error in quantum chemistry calculations caused by interacting fragments borrowing each other's basis functions."),
    ("Krishnan Medal", "Krishnan Medal", "The Krishnan Medal is an award associated with Indian science, particularly physical sciences."),
    ("Category:Hydroelectric power stations in Wales", "Category:Hydroelectric power stations in Wales", "This is a Wikipedia category for hydroelectric power stations in Wales."),
    ("Great Debate", "Great Debate (astronomy)", "The Great Debate was a 1920 astronomy debate about the scale of the universe and the nature of spiral nebulae."),
    ("Outline of acoustics", "Outline of acoustics", "An outline of acoustics is an organized guide to the science of sound."),
    ("Ric Ocasek", "Ric Ocasek", "Ric Ocasek was a musician and record producer, not a physics concept."),
    ("Quantum catalyst", "Quantum catalyst", "A quantum catalyst is an auxiliary quantum resource that enables a transformation without being consumed."),
    ("Quantum memory", "Quantum memory", "Quantum memory is a device or system that stores quantum states while preserving quantum coherence."),
    ("Classification of electromagnetic fields", "Classification of electromagnetic fields", "Classification of electromagnetic fields groups electromagnetic fields by invariants, sources, or transformation properties."),
    ("Bearing capacity", "Bearing capacity", "Bearing capacity is the ability of soil or a structural element to support applied loads without failure."),
    ("European Region of Gastronomy", "European Region of Gastronomy", "European Region of Gastronomy is a cultural and regional designation related to food, not physics."),
    ("De Sitter universe", "De Sitter universe", "A de Sitter universe is a cosmological spacetime solution with positive cosmological constant and no ordinary matter."),
    ("Mondovì Funicular", "Mondovì Funicular", "The Mondovì Funicular is a cable railway system and not a physics concept."),
    ("Complex beam parameter", "Complex beam parameter", "The complex beam parameter is a quantity used in Gaussian optics to describe beam curvature and width."),
    ("Aleksandr Akhiezer", "Aleksandr Akhiezer", "Aleksandr Akhiezer was a Soviet theoretical physicist known for work in quantum electrodynamics and plasma physics."),
    ("Category:Quantum chromodynamics", "Category:Quantum chromodynamics", "Quantum chromodynamics is the theory of the strong interaction between quarks and gluons."),
    ("Corrosion fatigue", "Corrosion fatigue", "Corrosion fatigue is material failure caused by cyclic stress in a corrosive environment."),
    ("Category:Coordinate charts in general relativity", "Category:Coordinate charts in general relativity", "Coordinate charts in general relativity are coordinate systems used to describe spacetime manifolds."),
    ("The Breath of Life", "The Breath of Life (band)", "The Breath of Life is a band and not a physics concept."),
    ("Caroline Morley", "Caroline Morley", "Caroline Morley is a scientist associated with planetary atmospheres and astronomy."),
    ("Cynthia Olson Reichhardt", "Cynthia Olson Reichhardt", "Cynthia Olson Reichhardt is a physicist known for computational condensed matter and nonlinear dynamics research."),
    ("Theoretical Girls", "Theoretical Girls", "Theoretical Girls was a musical group and not a physics concept."),
    ("Category:Physics experiments", "Category:Physics experiments", "Physics experiments are empirical investigations designed to test physical theories or measure physical quantities."),
    ("Black body", "Black body", "A black body is an idealized object that absorbs all incident electromagnetic radiation and emits thermal radiation determined by its temperature."),
    ("Linda Chisholm", "Linda Chisholm", "Linda Chisholm is a named individual and not a physics concept."),
    ("Phnom Bakheng", "Phnom Bakheng", "Phnom Bakheng is a temple site in Cambodia, not a physics concept."),
    ("Anderson impurity model", "Anderson impurity model", "The Anderson impurity model describes a localized electronic state interacting with a continuum of conduction electrons."),
    ("Category:Integrable systems", "Category:Integrable systems", "Integrable systems are mathematical or physical systems with enough conserved quantities to allow exact solution."),
    ("Cohesion number", "Cohesion number", "The cohesion number is a dimensionless quantity comparing cohesive forces with other forces in a granular or particulate system."),
    ("Extreme mass ratio inspiral", "Extreme mass ratio inspiral", "An extreme mass ratio inspiral is a compact object spiraling into a much more massive black hole and emitting gravitational waves."),
    ("Jan Zídek", "Jan Zídek", "Jan Zídek is a named individual and not a physics concept."),
    ("Odor detection threshold", "Odor detection threshold", "Odor detection threshold is the minimum concentration of a substance that can be detected by smell."),
    ("Fake", "Fake (Swedish band)", "Fake is a Swedish band and not a physics concept."),
    ("Clapham, North Yorkshire", "Clapham, North Yorkshire", "Clapham is a village in North Yorkshire and not a physics concept."),
    ("Dan Shechtman", "Dan Shechtman", "Dan Shechtman is a materials scientist known for discovering quasicrystals."),
    ("Conjugate beam method", "Conjugate beam method", "The conjugate beam method is a structural analysis technique for determining slopes and deflections in beams."),
    ("Kiril Džajkovski", "Kiril Džajkovski", "Kiril Džajkovski is a musician and not a physics concept."),
    ("Lacerta in Chinese astronomy", "Lacerta in Chinese astronomy", "Lacerta in Chinese astronomy refers to how the constellation Lacerta is represented in traditional Chinese star maps."),
    ("Thermal infrared spectroscopy", "Thermal infrared spectroscopy", "Thermal infrared spectroscopy measures infrared radiation associated with thermal emission to infer material or atmospheric properties."),
    ("John Brand Schneider", "John Brand Schneider", "John Brand Schneider is a scientist or engineer associated with electromagnetics or computational physics."),
    ("2008–09 Tulane Green Wave women's basketball team", "2008–09 Tulane Green Wave women's basketball team", "The 2008–09 Tulane Green Wave women's basketball team was a college basketball team, not a physics concept."),
    ("Rubber band experiment", "Rubber band experiment", "A rubber band experiment is a demonstration of elasticity, entropy, or thermodynamic behavior using a stretched rubber band."),
    ("Blitzkrieg", "Blitzkrieg (metal band)", "Blitzkrieg is a metal band and not a physics concept."),
    ("Ideally hard superconductor", "Ideally hard superconductor", "An ideally hard superconductor is an idealized superconductor with strong flux pinning and irreversible magnetic behavior."),
    ("The Siren Six!", "The Siren Six!", "The Siren Six! was a musical group and not a physics concept."),
    ("Ferenc Krausz", "Ferenc Krausz", "Ferenc Krausz is a physicist known for attosecond physics and ultrafast laser science."),
    ("Mean free path", "Mean free path", "Mean free path is the average distance a particle travels between successive interactions or collisions."),
    ("Isaak Pomeranchuk", "Isaak Pomeranchuk", "Isaak Pomeranchuk was a Soviet theoretical physicist known for contributions to particle physics and condensed matter physics."),
    ("National Council of Women of Canada", "National Council of Women of Canada", "The National Council of Women of Canada is an advocacy organization, not a physics concept."),
    ("Category:Hydroelectric power stations in Namibia", "Category:Hydroelectric power stations in Namibia", "This is a Wikipedia category for hydroelectric power stations in Namibia."),
    ("Julia Kempe", "Julia Kempe", "Julia Kempe is a computer scientist and physicist associated with quantum information and algorithms."),
    ("Positronium hydride", "Positronium hydride", "Positronium hydride is an exotic molecule consisting of a hydrogen atom bound to positronium."),
    ("English Evenings", "English Evenings", "English Evenings is a musical group and not a physics concept."),
    ("Taiji", "Taiji (philosophy)", "Taiji is a concept in Chinese philosophy and not a physics concept."),
    ("Yumi Ohka", "Yumi Ohka", "Yumi Ohka is a professional wrestler and not a physics concept."),
]


def main() -> None:
    out = [{"term": term, "page": page, "model_definition": definition} for term, page, definition in DEFS]
    Path("facts/physics_codex/independent_defs.json").write_text(
        json.dumps(out, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    Path("facts/physics_codex/phase2-summary.json").write_text(
        json.dumps({"seed": SEED, "sample_size": len(out)}, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(f"wrote {len(out)} independent definitions with seed {SEED}")


if __name__ == "__main__":
    main()
