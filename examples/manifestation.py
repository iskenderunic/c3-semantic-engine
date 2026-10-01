"""
Manifestation mode (Concept × Context = Content) — applied example.

The computable engine (``c3_semantic_engine.py``) scores a *candidate* in the
**Synthesis** direction (Concept × Content → Context, as an EXECUTE/REFINE gate).
**Manifestation** is the *generative* direction: hold a fixed Context, read a
Concept from source material, and *produce* new Content.

This file shows the PIPELINE SHAPE, dependency-free. The ``extract_concept`` and
``generate`` steps are mocked; swap them for a real LLM + generative model (see the
note at the bottom). A live instance is "Single Prompt Shot" on mustafaiskender.com.

    python3 examples/manifestation.py
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable


# --- A Context instance: a "CODNA" — brand / aesthetic genetic code --------------
# The Context is held fixed across runs; it steers and constrains generation but
# does not uniquely determine the output (Manifestation is lossy / generative).
CODNA = {
    "mood": "minimalist, premium, cinematic wise-tech",
    "palette": ["#8775d3", "#5833ff", "#2563eb"],
    # Derived from the concept at run time, not fixed to one key:
    "tonal_range": "light / mid / dark — chosen from the concept",
    "composition_range": "abstract OR representational — fit to the content",
    # Explicit anti-cliché list: keeps a fixed Context from collapsing into one
    # repeated output.
    "avoid": ["glowing orb / energy core", "hologram HUD", "circuit texture",
              "robot face", "single floating crystal on foggy dark"],
}


@dataclass
class Manifestation:
    """Concept × Context = Content, as a three-stage pipeline."""

    context: dict
    extract_concept: Callable[[str], str]   # source material -> core Concept
    generate: Callable[[str], str]          # fused prompt    -> Content

    def run(self, source: str) -> dict:
        concept = self.extract_concept(source)   # 1) read Concept from the source
        prompt = self._compose(concept)          # 2) inject Context  (Concept × Context)
        content = self.generate(prompt)          # 3) produce Content
        return {"concept": concept, "prompt": prompt, "content": content}

    def _compose(self, concept: str) -> str:
        c = self.context
        return (
            f"{concept}. "
            f"Style: {c['mood']}; palette {', '.join(c['palette'])}; "
            f"tonal range: {c['tonal_range']}; composition: {c['composition_range']}; "
            f"avoid clichés: {', '.join(c['avoid'])}; no text, 16:9."
        )


# --- Mock stages (replace with real models) -------------------------------------
def mock_extract_concept(source: str) -> str:
    """A real impl prompts an LLM: 'extract ONE core visual concept from this text.'"""
    first = source.strip().split(".")[0].strip().lower()
    return f"An original visual metaphor for: {first}"


def mock_generate(prompt: str) -> str:
    """A real impl calls a generative (image) model and returns the artifact / URL."""
    return f"<artifact generated from prompt: {prompt[:72]}...>"


def main() -> None:
    engine = Manifestation(CODNA, mock_extract_concept, mock_generate)
    source = (
        "C3 defines context as the multiplicative product of concept and content; "
        "if either factor collapses to zero, the context collapses with it."
    )
    out = engine.run(source)
    for key, value in out.items():
        print(f"{key}:\n  {value}\n")


if __name__ == "__main__":
    main()


# Real wiring (mustafaiskender.com "Single Prompt Shot"):
#   extract_concept -> a text LLM reading a blog post
#   generate        -> an image model, returning the featured image
#   context (CODNA) -> loaded from a JSON genetic-code file that also powers a
#                      public /codna showcase (one source of truth)
