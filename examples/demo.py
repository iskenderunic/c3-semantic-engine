"""
Minimal usage example — works after `pip install .` or as a drop-in file.

    python3 examples/demo.py
"""

from c3_semantic_engine import (
    C3Engine,
    keyword_alignment_scorer,
    validator_fidelity_scorer,
    estimate_missing_factor,
)


def main() -> None:
    engine = C3Engine(
        concept_scorer=lambda cand, ref: keyword_alignment_scorer(cand, ref),   # α: intent alignment
        content_scorer=lambda cand, ref: validator_fidelity_scorer(cand, ref),  # β: payload fidelity
        tau=0.70,                                                                # acceptance threshold
    )

    # A candidate action, the invariants it must satisfy, and validators for the payload.
    candidate = "Deploy the headless CMS with an idempotent migration and a rollback point."
    concept_ref = ["idempotent", "rollback"]
    content_ref = [lambda x: isinstance(x, str) and len(x) > 20]

    d = engine.decide(candidate, concept_ref, content_ref)
    print(f"α (concept) = {d.concept:.2f}")
    print(f"β (content) = {d.content:.2f}")
    print(f"γ (context) = {d.context:.2f}   (τ = {engine.tau})")
    print(f"→ {d.action}" + (f"  (fix: {d.deficit})" if d.deficit else ""))

    # A failing case: one invariant missing → gate refuses, and tells you which factor to fix.
    weak = "Deploy with only a rollback point."  # 'idempotent' missing
    d2 = engine.decide(weak, concept_ref, content_ref)
    print(f"\nweak candidate → γ = {d2.context:.2f} → {d2.action} (fix: {d2.deficit})")

    # Directional diagnostic (NOT exact inversion — see spec §9).
    print("estimate missing factor (γ=0.4, known β=0.8):", estimate_missing_factor(0.4, 0.8))


if __name__ == "__main__":
    main()
