# C3 Engine — Reference Implementation

A dependency-free Python reference for the C3 decision gate. See the
[project spec](../README.md) for the model and rationale.

## Run the demo

```bash
python3 c3_engine.py
```

## Use it

Inject your own scorers — an LLM judge, an embedder, or deterministic validators.
The engine only cares that they return a score in `[0, 1]`.

```python
from c3_engine import C3Engine, keyword_alignment_scorer, validator_fidelity_scorer

engine = C3Engine(
    concept_scorer=lambda cand, ref: keyword_alignment_scorer(cand, ref),   # α: intent alignment
    content_scorer=lambda cand, ref: validator_fidelity_scorer(cand, ref),  # β: payload fidelity
    tau=0.70,                                                                # acceptance threshold
)

decision = engine.decide(
    candidate="Deploy with an idempotent migration and a rollback point.",
    concept_ref=["idempotent", "rollback"],                 # required invariants
    content_ref=[lambda x: isinstance(x, str) and len(x) > 20],  # validators
)

# decision.context == decision.concept * decision.content
# decision.action  == "EXECUTE" or "REFINE"
# decision.deficit == "concept" | "content" | None   → routes self-correction
```

## Swapping in a real scorer

- **LLM-as-judge:** `concept_scorer=lambda cand, ref: llm_rate_alignment(cand, ref)` returning a
  normalized `[0,1]` score.
- **Embedding proximity:** cosine similarity to invariant anchors, squashed to `[0,1]`.
- **Validators:** schema/lint/type/test pass-rate for structured or code payloads.

`RegistryScorer` composes several signals per dimension (default `combine=min`).

## Diagnostic, not inversion

`estimate_missing_factor(gamma, known)` returns `gamma / known` **only as a directional hint**
(returns `None` when `known` is near zero). The product is lossy — it does not recover a unique
hidden factor. See spec §9.

License: MIT (see [../LICENSE](../LICENSE)).
