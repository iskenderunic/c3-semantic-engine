"""
c3_semantic_engine — the C3 decision gate.

Single-file, dependency-free. Use it two ways:
  1. Drop-in: copy this file into your project → `from c3_semantic_engine import C3Engine`.
  2. Install: `pip install git+https://github.com/iskenderunic/c3-semantic-engine`.

A deterministic decision gate for autonomous agents:

    context = concept * content        # both scores in [0, 1]
    fire the gate iff context >= tau

The engine is intentionally *agnostic about scoring*: you inject a `concept_scorer`
and a `content_scorer`. The scorers are where the real work lives (an LLM-as-judge,
an embedding-similarity function, or deterministic validators). This file ships
transparent example scorers so the gate is runnable, and a `RegistryScorer` that
composes several signals.

License: MIT (see LICENSE).
Author: Mustafa İskender — Wise-Tech OS (WTOS) / Runix.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Iterable, Protocol

__version__ = "2.0.0"
__all__ = [
    "C3Engine",
    "Decision",
    "Scorer",
    "RegistryScorer",
    "keyword_alignment_scorer",
    "validator_fidelity_scorer",
    "estimate_missing_factor",
    "clamp01",
]


# --------------------------------------------------------------------------- #
# Scorer contract
# --------------------------------------------------------------------------- #

class Scorer(Protocol):
    """Return a calibrated score in [0, 1] for a candidate against a reference."""

    def __call__(self, candidate: Any, reference: Any) -> float: ...


def clamp01(x: float) -> float:
    """Clamp to the valid score range; a scorer that leaves [0,1] is a bug."""
    return 0.0 if x < 0.0 else 1.0 if x > 1.0 else float(x)


# --------------------------------------------------------------------------- #
# Example scorers (replace with an LLM judge / embedder / validator in prod)
# --------------------------------------------------------------------------- #

def keyword_alignment_scorer(candidate: str, invariants: Iterable[str]) -> float:
    """
    Example CONCEPT scorer: fraction of required invariants present in the candidate.

    This is a transparent stand-in. In production, swap for an LLM judge that rates
    alignment to the objective, or embedding proximity to invariant anchors.
    """
    invs = [i.strip().lower() for i in invariants if i.strip()]
    if not invs:
        # No invariants declared → alignment is undefined; treat as fully unconstrained.
        return 1.0
    text = (candidate or "").lower()
    hits = sum(1 for i in invs if i in text)
    return clamp01(hits / len(invs))


def validator_fidelity_scorer(candidate: Any, validators: Iterable[Callable[[Any], bool]]) -> float:
    """
    Example CONTENT scorer: pass-rate over deterministic validators
    (schema checks, lint, type checks, citation presence, test results).
    """
    checks = list(validators or [])
    if not checks:
        # No validators → fidelity is asserted by mere presence (weak signal).
        return 1.0 if candidate not in (None, "", [], {}) else 0.0
    passed = 0
    for check in checks:
        try:
            passed += 1 if check(candidate) else 0
        except Exception:
            pass  # a throwing validator counts as a failed check
    return clamp01(passed / len(checks))


@dataclass
class RegistryScorer:
    """
    Compose several scorers for one dimension. `combine` defaults to `min`
    (a single weak signal drags the score down — matching the zero-collapse ethos).
    """
    scorers: list[Callable[[Any, Any], float]]
    combine: Callable[[Iterable[float]], float] = min

    def __call__(self, candidate: Any, reference: Any) -> float:
        if not self.scorers:
            return 1.0
        return clamp01(self.combine(clamp01(s(candidate, reference)) for s in self.scorers))


# --------------------------------------------------------------------------- #
# The gate
# --------------------------------------------------------------------------- #

@dataclass
class Decision:
    concept: float
    content: float
    context: float
    approved: bool
    action: str          # "EXECUTE" | "REFINE"
    deficit: str | None  # which factor to fix when refining: "concept" | "content" | None


@dataclass
class C3Engine:
    """
    concept_scorer(candidate, concept_reference) -> [0,1]
    content_scorer(candidate, content_reference) -> [0,1]
    """
    concept_scorer: Callable[[Any, Any], float]
    content_scorer: Callable[[Any, Any], float]
    tau: float = 0.70  # acceptance threshold — tune per task; no universal value.

    def score(self, candidate: Any, concept_ref: Any, content_ref: Any) -> Decision:
        alpha = clamp01(self.concept_scorer(candidate, concept_ref))
        beta = clamp01(self.content_scorer(candidate, content_ref))
        gamma = alpha * beta  # Context = Concept × Content
        approved = gamma >= self.tau
        deficit = None if approved else ("concept" if alpha <= beta else "content")
        return Decision(
            concept=alpha,
            content=beta,
            context=gamma,
            approved=approved,
            action="EXECUTE" if approved else "REFINE",
            deficit=deficit,
        )

    def decide(self, candidate: Any, concept_ref: Any, content_ref: Any) -> Decision:
        """Alias for `score` — the public gate entry point."""
        return self.score(candidate, concept_ref, content_ref)


# --------------------------------------------------------------------------- #
# Directional deficit diagnostic (NOT exact inversion — see README §9)
# --------------------------------------------------------------------------- #

def estimate_missing_factor(gamma: float, known: float, *, floor: float = 1e-3) -> float | None:
    """
    Estimate the unknown factor as gamma / known.

    WARNING: the product is lossy, so this does NOT recover a unique latent factor —
    it only indicates a *plausible magnitude*. Returns None when `known` is below
    `floor` (division is numerically unstable / undefined near zero).
    Use only to route self-correction, never to reconstruct hidden intent.
    """
    if known < floor:
        return None
    return clamp01(gamma / known)


# --------------------------------------------------------------------------- #
# Demo
# --------------------------------------------------------------------------- #

if __name__ == "__main__":
    engine = C3Engine(
        concept_scorer=lambda c, ref: keyword_alignment_scorer(c, ref),
        content_scorer=lambda c, ref: validator_fidelity_scorer(c, ref),
        tau=0.70,
    )

    candidate = "Deploy the headless CMS with an idempotent migration and a rollback point."
    concept_ref = ["idempotent", "rollback"]                 # required invariants
    content_ref = [lambda x: isinstance(x, str) and len(x) > 20]  # validators

    d = engine.decide(candidate, concept_ref, content_ref)
    print(f"concept α = {d.concept:.2f}")
    print(f"content β = {d.content:.2f}")
    print(f"context γ = {d.context:.2f}  (τ = {engine.tau})")
    print(f"→ {d.action}" + (f" (fix: {d.deficit})" if d.deficit else ""))
