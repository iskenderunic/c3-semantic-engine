# C3 Engine & Algorithmic Framework — Specification & Prior-Art Dossier

# C3 Motoru ve Algoritmik Çerçevesi — Teknik Şartname ve Literatür Dosyası

> **Author / Mimar:** Mustafa İskender
> **Ecosystem / Ekosistem:** Wise-Tech OS (WTOS) / Runix Multi-Agent Architecture
> **Package / Paket:** `c3-semantic-engine` · `@wisetech/c3-engine`
> **Version / Sürüm:** 2.0
> **License / Lisans:** Documentation → CC BY-SA 4.0 · Code → MIT (see [Licensing](#licensing--lisanslama))

> **Disambiguation:** This is **not** Python's *C3 linearization* (Method Resolution Order),
> nor Ohmae's *3C* business model, nor *C3.js*. See §6.

---

## What changed in v2 / v2'de ne değişti

This revision hardens the framework for public/technical scrutiny:

1. **Honest framing.** The multiplicative relation is presented as an **operational model
   (a modeling choice / heuristic)**, not a proven mathematical "invariant" or law.
2. **Real scoring, not null-checks.** §4 now specifies **how** the Concept (α) and Content (β)
   scores are actually produced (LLM-as-judge / embedding / validator strategies) with a
   pluggable scorer interface — the placeholder truthiness checks of v1 are gone.
3. **Constrained inversion.** Claim 2 (semantic inversion) is downgraded from "exact recovery"
   to a **directional diagnostic**, with explicit division-by-zero and lossiness caveats (§9).
4. **Agentic prior art added.** §7.4 now covers self-correction / LLM-judge literature
   (Reflexion, Self-Refine, Constitutional AI) — the area where the "decision gate" novelty
   is actually contested.

---

## Table of Contents

- [1. Executive Summary](#1-executive-summary)
- [Install & Use](#install--use)
- [2. The Operational Model](#2-the-operational-model)
- [The C3 Triad — Three Modes](#the-c3-triad--three-operating-modes-conceptual-layer)
- [3. Structural Decomposition](#3-structural-decomposition)
- [4. Agentic Integration & Scoring](#4-agentic-integration--scoring)
- [5. System Dynamics & Feedback Loops](#5-system-dynamics--feedback-loops)
- [6. Namespace Collision Analysis](#6-namespace-collision-analysis)
- [7. Prior Art & Related Work](#7-prior-art--related-work)
- [8. Comparative Matrix](#8-comparative-matrix)
- [9. Claims (Scoped)](#9-claims-scoped)
- [10. Verification Checklist](#10-verification-checklist)
- [Türkçe Özet](#türkçe-özet)
- [Licensing / Lisanslama](#licensing--lisanslama)

---

## 1. Executive Summary

The **C3 model** is a *multiplicative context-synthesis and decision-gating pattern* for
autonomous agents. Where conventional pipelines treat context as **additively concatenated**
attributes, C3 models the realized utility (**Context**) as the **interaction product** of
strategic intent (**Concept**) and material payload (**Content**):

```
Context = Concept × Content
```

The value of the pattern is not a new mathematical operation — element-wise multiplicative
composition is well studied (see §7.2). Its contribution is **systemic**: applying a
zero-collapsing product as an explicit, deterministic **execution gate** in an agent loop,
with a diagnostic to attribute failures to either the intent or the payload.

> **Framing.** Treat `Context = Concept × Content` as an **operational model** — a useful,
> falsifiable heuristic for gating agent actions — not as a physical law. It earns its keep
> if it improves gating decisions in practice, not because the algebra is profound.

---

## Install & Use

Zero dependencies, either way:

**A — pip install (from GitHub):**

```bash
pip install git+https://github.com/iskenderunic/c3-semantic-engine
```

**B — drop-in single file:** copy [`c3_semantic_engine.py`](c3_semantic_engine.py) into your project.

Then:

```python
from c3_semantic_engine import C3Engine, keyword_alignment_scorer, validator_fidelity_scorer

engine = C3Engine(
    concept_scorer=lambda cand, ref: keyword_alignment_scorer(cand, ref),   # α: intent alignment
    content_scorer=lambda cand, ref: validator_fidelity_scorer(cand, ref),  # β: payload fidelity
    tau=0.70,                                                                # acceptance threshold
)

d = engine.decide(
    candidate="Deploy with an idempotent migration and a rollback point.",
    concept_ref=["idempotent", "rollback"],                      # required invariants
    content_ref=[lambda x: isinstance(x, str) and len(x) > 20],  # validators
)

# d.context == d.concept * d.content
# d.action  == "EXECUTE" | "REFINE"
# d.deficit == "concept" | "content" | None   → routes self-correction
```

Run the bundled demo: `python -m c3_semantic_engine` (or `python examples/demo.py`).
Swap the example scorers for a real one (LLM judge / embeddings / validators) — see §4.

---

## 2. The Operational Model

### 2.1 Core relation

Let the three quantities be scalar scores in `[0, 1]` (or, in the vector formulation, points
in an embedding space that are reduced to a scalar by a scoring head):

```
Context = Concept × Content
```

| Symbol   | Meaning                                                        | Range   |
| -------- | ------------------------------------------------------------- | ------- |
| Concept  | Strategic intent / objective / invariants / guardrails        | [0, 1]  |
| Content  | Payload: data, syntax, code, factual tokens                   | [0, 1]  |
| Context  | Realized pragmatic utility / situational fit / action-worthiness | [0, 1]  |

### 2.2 Zero-Product behavior (Multiplicative Semantic Annihilation)

Because the relation is a product, if either factor collapses the output collapses:

```
Concept → 0  ⇒  Context → 0        (directionless data = high-entropy noise / drift)
Content → 0  ⇒  Context → 0        (ungrounded intent = non-executable abstraction)
```

This is the property the pattern exploits: a strong plan with empty payload, or rich payload
with no plan, are both treated as **non-actionable** — the gate refuses to fire.

> **Scope note.** The "annihilation" is exact only at 0. Near zero it is ordinary
> multiplication; the useful consequence is monotone attenuation, not a discontinuity.

---

## The C3 Triad — Three Operating Modes (conceptual layer)

The single **computable** relation is `Context = Concept × Content` (§2). But C3 is originally
conceived as a **symmetric triad**: three vertices — Concept, Content, Context — where any two
generate the third. Depending on which two you hold, you solve for a different unknown. These are
three *operating modes*, not three simultaneous equations.

| Variation | Mode | You have → you seek | Question |
| --------- | ---- | ------------------- | -------- |
| `Concept × Content = Context` | **Synthesis** | intent + payload → meaning | *What fit emerges?* |
| `Concept × Context = Content` | **Manifestation** | intent + situation → payload | *What should be produced here?* |
| `Context × Content = Concept` | **Distillation** | meaning + payload → intent | *What was the underlying intent?* |

```
                Concept
               /        \
       Synthesis        Manifestation
             /              \
        Content —— Distillation —— Context
```

A **meaning triangle**: each edge is one mode; the two vertices it connects produce the third.

> **Honest note (see §9).** Written as products, these three cannot all hold for the same values
> (except the trivial 0/1 case) — so this is a **conceptual / design** layer, not simultaneous
> algebra. In the **computable** engine only *Synthesis* is an exact forward product;
> *Manifestation* and *Distillation* are recovered by division (`known → sought`) and are **lossy**
> — directional diagnostics, not exact reconstructions. The math layer stays rigorous; the triad is
> the framing that makes the three generative directions legible.

---

## 3. Structural Decomposition

| Dimension | Metric              | Agentic Function                    | Failure Mode (X→0)              |
| --------- | ------------------- | ----------------------------------- | ------------------------------- |
| Concept   | Alignment score α   | System prompt, guardrails, objective | Semantic drift / aimless output |
| Content   | Fidelity score β    | Data, syntax, code, factual tokens  | Empty / speculative execution   |
| Context   | Pragmatic value γ   | Final gate, tool call, delivery     | Rejected / irrelevant action    |

`γ = α · β`, and the gate fires iff `γ ≥ τ` for an acceptance threshold `τ`.

---

## 4. Agentic Integration & Scoring

In an agent loop (e.g. the Runix / WTOS cluster) C3 is a **deterministic decision gate**:

```
   Objective ──▶ Concept score α ─┐
                                   ├──▶ γ = α·β ──▶ (γ ≥ τ ?) ──▶ EXECUTE
   Input/Payload ─▶ Content score β┘                   │
                                                       └─▶ REFINE (self-correction loop)
```

### 4.1 The scoring problem is the real work

The gate is trivial; **producing calibrated α and β in `[0,1]` is the substantive part.**
C3 does not prescribe a single scorer — it defines the *interface* and offers three
concrete strategies:

1. **LLM-as-judge.** Prompt a model to rate alignment/fidelity against the stated invariants,
   returning a normalized score (optionally with rationale). Best for open-ended intent.
2. **Embedding proximity.** Cosine similarity between the candidate and a set of invariant
   anchors (for Concept) or ground-truth references (for Content), squashed to `[0,1]`.
3. **Deterministic validators.** Schema/lint/test pass-rates, type checks, citation presence —
   ideal for Content fidelity of code or structured output.

Scores from multiple strategies can be combined (e.g. min, weighted mean) per dimension.

### 4.2 Reference implementation

A runnable, dependency-free reference with a **pluggable scorer interface** lives in
[`c3_semantic_engine.py`](c3_semantic_engine.py). The engine is intentionally agnostic:
you inject `concept_scorer` and `content_scorer` callables (an LLM judge, an embedder, or a
validator). The v1 truthiness placeholders have been removed in favor of this contract.

---

## 5. System Dynamics & Feedback Loops

1. **Deficit attribution.** When `γ < τ`, compare α and β: the smaller factor localizes the
   deficit (weak intent vs. weak payload).
2. **Targeted self-correction.** If α is low → refine the prompt/objective. If β is low →
   trigger retrieval / regeneration of the payload. Re-score and re-gate until `γ ≥ τ`
   (or a max-iteration budget is hit — see §9, no guarantee of convergence).

---

## 6. Namespace Collision Analysis

| Identifier          | Domain                              | Risk | Note |
| ------------------- | ----------------------------------- | ---- | ---- |
| **C3 linearization** | CS — Python/Dylan MRO               | High (name only) | Computes method resolution order in class inheritance. Unrelated to semantics. Use `c3-semantic-engine`. |
| **3C Model (Ohmae)** | Business strategy (1982)            | Medium | Corporation/Customer/Competitors. Qualitative, non-computational. |
| **3C Architecture**  | Robotics / cybernetics              | Low  | Command, Control, Communication. |
| **C3.js**            | Frontend charting                   | Low  | D3-based visualization library. |

**Disambiguation strategy:** package/repo named `c3-semantic-engine`; docs state the MRO
distinction explicitly.

---

## 7. Prior Art & Related Work

### 7.1 Semiotics
- **Ogden–Richards triangle of meaning (1923):** Symbol / Thought / Referent.
  *Difference:* descriptive & philosophical; C3 operationalizes a triad into a runtime gate.
- **Peirce's triadic semiosis:** Signifier / Signified / Interpretant.
  *Difference:* C3 adds the zero-collapse gating rule.

### 7.2 Vector composition in NLP
- **Mitchell & Lapata (2008), *Vector-based Models of Semantic Composition*:** studied
  **element-wise multiplicative** composition `p_i = u_i · v_i` for phrases.
  *Difference (honest):* the **operation is the same**; C3's contribution is the *level of
  application* (macro agent-orchestration, treating Concept as an invariant objective and
  Content as an empirical payload) and the *gating semantics*, not a new algebra.

### 7.3 Transformer attention
- Attention mixes values via scaled dot products, bounded only by the context window.
  *Difference:* C3 uses the product as an **accept/reject validation gate**, not as an
  internal mixing weight.

### 7.4 Agentic self-correction & evaluation (the contested neighborhood)
This is where the "decision gate + self-correct" idea overlaps existing work, and where C3's
originality must be argued honestly:
- **Reflexion (Shinn et al., 2023):** verbal self-reflection to improve subsequent attempts.
- **Self-Refine (Madaan et al., 2023):** iterative self-feedback and revision.
- **LLM-as-a-judge (e.g. Zheng et al., 2023):** using a model to score outputs.
- **Constitutional AI / guardrails (Bai et al., 2022):** rule-conditioned filtering.

*Difference:* those methods are largely **learned or heuristic and unidirectional**. C3's
distinguishing choices are (a) a **deterministic multiplicative gate** with an explicit
zero-collapse, and (b) **factor attribution** (α vs. β) to route self-correction. It is a
*composition and framing* of known parts, not a claim to have invented self-correction.

---

## 8. Comparative Matrix

| Feature            | RAG / heuristics        | Mitchell & Lapata (2008) | Reflexion / Self-Refine | Business 3C | **C3**                     |
| ------------------ | ----------------------- | ------------------------ | ----------------------- | ----------- | -------------------------- |
| Operational basis  | Cosine / top-k          | Lexical vector product   | Learned self-feedback   | Qualitative | Multiplicative gate        |
| Zero-state         | Soft penalty            | Vector attenuation       | N/A                     | Subjective  | Explicit collapse (`×0=0`) |
| Failure attribution| No                      | No                       | Implicit                | Conceptual  | Explicit (α vs. β)         |
| Runtime target     | Retrieval               | Static embeddings        | Agent trajectory        | Slides      | Agent execution gate       |

---

## 9. Claims (Scoped)

1. **Multiplicative gating.** Using `γ = α·β` with a zero-collapse as an explicit execution
   gate — where either a weak objective **or** weak payload blocks the action — is a coherent,
   implementable agent-control pattern. *(Novelty is in the systemic composition, not the
   product operation itself; see §7.2, §7.4.)*
2. **Directional deficit diagnostic (was: "semantic inversion").** Given `γ` and one known
   factor, the other can be *estimated* as `γ / known`. **Caveats:**
   - The product is **lossy** — many `(α, β)` pairs yield the same `γ`, so exact recovery of a
     latent factor is **not** possible in general.
   - Division by a near-zero known factor is **numerically unstable / undefined**.
   Therefore this is a **directional diagnostic** ("which factor is likely deficient"), not a
   reconstruction. Use it to *route* correction, not to *recover* hidden intent.
3. **Prompt-space partitioning.** Keeping strategic constraints (Concept), payload (Content),
   and realized utility (Context) as separately scored channels reduces prompt pollution and
   makes failures attributable.

> No convergence guarantee: the self-correction loop (§5) may not reach `γ ≥ τ`; bound it with
> a max-iteration budget.

---

## 10. Verification Checklist

- [ ] **Name disambiguation** — docs distinguish from Python C3 linearization.
- [ ] **Bounds** — scorers return values in `[0,1]`; `γ = α·β` reproduces zero-collapse at 0/1 edges.
- [ ] **Deterministic gating** — `C3Engine.decide()` routes sub-threshold payloads to correction.
- [ ] **Scorer honesty** — α/β come from a real scorer (LLM/embedding/validator), not a truthiness check.
- [ ] **Inversion caveats** — any use of `γ / known` guards against near-zero denominators and treats output as diagnostic only.

---

## Türkçe Özet

**C3**, otonom ajanlar için *çarpımsal bir bağlam sentezi ve karar-geçidi desenidir*. Bağlamı
parçaların **toplamı** olarak gören klasik yaklaşımların aksine, nihai faydayı (**Context**)
stratejik niyet (**Concept**) ile somut yükün (**Content**) **çarpımı** olarak modeller:

```
Context = Concept × Content
```

Katkı yeni bir matematiksel işlem değildir (çarpımsal bileşim literatürde vardır — §7.2);
katkı **sistemseldir**: sıfırda çöken bu çarpımı bir ajan döngüsünde **deterministik bir eylem
geçidi** olarak kullanmak ve hatayı niyete mi yoksa yüke mi bağlanacağını **teşhis** etmek.

**Dürüst çerçeve:** Bunu bir *fizik yasası* değil, gating kararlarını iyileştiriyorsa değerli
olan bir **operasyonel model / sezgisel yöntem** olarak ele alın.

- **Sıfır-Çarpım:** Concept=0 → yönsüz gürültü; Content=0 → temelsiz soyutluk; ikisinde de geçit
  ateşlenmez.
- **Skorlama işin özü:** α (niyet hizası) ve β (yük doğruluğu) skorları LLM-judge / embedding /
  doğrulayıcı stratejileriyle üretilir (§4). Motor bu skorlayıcıları *enjekte* eder.
- **Teşhis (eski "tersine mühendislik"):** `γ/known` ancak **yönlü bir teşhistir** — çarpım
  kayıplı olduğu ve sıfıra bölme tanımsız olduğu için gizli faktör kesin geri-türetilemez (§9).
- **C3 Üçlemesi (anlam üçgeni):** Çekirdek tek denklem olsa da C3 simetrik bir üçgen olarak
  tasarlanmıştır — her iki köşe üçüncüyü üretir: **Sentez** (Concept×Content=Context), **Tezahür**
  (Concept×Context=Content), **Öz** (Context×Content=Concept). Bu üç *mod* aynı anda geçerli bir
  cebir değil, **kavramsal bir katmandır**; hesaplanabilir motorda yalnızca Sentez tam çarpım,
  diğerleri kayıplı bölmeyle türetilir.

Ayrıntılı bölümler için yukarıdaki İngilizce şartnameye bakın; referans uygulama
[`c3_semantic_engine.py`](c3_semantic_engine.py).

---

## Licensing / Lisanslama

This project is **dual-licensed** to fit its two kinds of content:

- **Documentation** (this `README.md` and all prose/specs) →
  **Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)** — see
  [`LICENSE-DOCS`](LICENSE-DOCS).
- **Source code** ([`c3_semantic_engine.py`](c3_semantic_engine.py) and [`examples/`](examples/)) →
  **MIT License** — see [`LICENSE`](LICENSE).

Attribution: **Mustafa İskender** — Wise-Tech OS (WTOS) / Runix.

> Note: CC BY-SA protects the *text* (copyleft for the writing); it is not a patent grant and
> does not cover the underlying idea. The defensible originality here is the **specific system
> and framing**, not the multiplicative operation (which is prior art — §7.2).
