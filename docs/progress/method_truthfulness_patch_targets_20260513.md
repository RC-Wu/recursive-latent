# Method Truthfulness Patch Targets - 2026-05-13

Scope: read-only inspection of `paper_siga/main.tex` Sections 4.4, 4.5, and the method/result bridge around projection, masked local realization/naturalization, and decode/project/re-encode wording. Compared against `docs/progress/code_metric_opportunities_20260513.md`.

## Bottom Line

The manuscript is already conservative about topology, physical simulation, and rendered-asset claims, but it still overstates one implementation boundary: several places describe the evaluated/current executor as performing a full decoded-domain `decode -> project -> re-encode` transition at every recursive depth. The comparison note explicitly says code evidence was found for mesh-first Shape-SLat recursion, per-depth decoding for output/diagnostics, masked flow/blend repair, and mesh/occupancy projection diagnostics, but not for a main-loop decoded-domain projection whose projected mesh is fed through `shape_slat_encoder` before the next recursive step.

Safest story: PS-RSLE defines the admissible execution contract as projection before the next rule reads active state; the current evidence implements and evaluates this contract through sparse-latent grammar state, masked flow/blend local realization, decoded mesh/occupancy projection diagnostics, and controlled trace proxies. A full decoded-domain project/re-encode loop should be described as the conceptual transition or future/full implementation boundary unless a new run proves it.

## Evidence Boundary From Code-Metric Note

Use these constraints when patching:

- Supported: executable Trellis2 mesh-first Shape-SLat workflows encode an input mesh, apply recursive coordinate/feature grammar edits, decode each depth, and log token/mesh/timing summaries.
- Supported: masked flow/blend repair calls `sample_shape_slat` on candidate coordinates, preserves previous tokens, and blends flow/candidate features for new coordinates.
- Supported: projection/admissibility is implemented strongly as mesh/occupancy connectivity repair and controlled trace/metric diagnostics.
- Not found: full decoded-domain `project -> re-encode` executed at every recursive depth in the main Trellis2 grammar loop.
- Not found: result-bearing transformer KV-cache reuse in main experiments.
- Handle metrics: use as controlled trace/mesh proxies, not general GLB-derived runtime handle recovery.

## Patch Targets

### 1. Abstract line 30

Current phrase:

> After each recursive step, an admissibility projection keeps root-attached active support, deactivates detached handles, and re-encodes the projected state before it can be read by later rules.

Issue: states full per-step re-encoding as an implemented fact in the abstract. This conflicts with the code-metric note's "did not find code evidence for a full decoded-domain project -> re-encode step executed at every recursive depth."

Replacement:

> After each recursive step, the PS-RSLE contract projects the candidate state before later rules can read it: root-attached support remains active, detached handles are deactivated, and the full formulation returns the projected asset through the generator codec. In the current Trellis2 implementation, this contract is evaluated through sparse-latent state updates plus decoded mesh/occupancy projection and controlled handle-state proxies.

### 2. Introduction line 93

Current phrase:

> After each recursive step, admissibility projection keeps root-attached active support, deactivates detached handles, and re-encodes the projected state before any later rule can read it.

Issue: same unconditional implementation claim as the abstract.

Replacement:

> After each recursive step, admissibility projection defines which support and handles are visible to later rules: root-attached support remains active and detached handles are deactivated. The formal transition includes re-encoding of the projected asset; our current Trellis2 evidence evaluates this boundary with sparse-latent grammar states, per-depth decoded diagnostics, and trace/mesh projection proxies.

### 3. Contributions line 102

Current phrase:

> We introduce controlled sparse-latent resampling together with admissibility projection and re-encoding, so each recursive step returns to a root-attached, addressable, and rule-readable state before the next step begins.

Issue: contribution wording blends formal mechanism and verified implementation. The "returns" phrasing suggests the current runs execute full codec re-entry every depth.

Replacement:

> We introduce controlled sparse-latent resampling together with an admissibility-projection contract for root-attached, addressable, rule-readable state before the next step begins; the formal transition includes codec re-entry, while the current experiments validate the state gate with sparse-latent updates and decoded projection proxies.

### 4. Related-work bridge line 132

Current phrase:

> PS-RSLE addresses this gap by executing user-authored finite-depth rules over sparse latent tokens and active handles, projecting each decoded candidate into root-attached active support, and re-encoding the projected state before later rules can read it.

Issue: repeats the full decode/project/re-encode claim outside the formal method section.

Replacement:

> PS-RSLE addresses this gap by executing user-authored finite-depth rules over sparse latent tokens and active handles, and by making projection to root-attached active support the admission gate before later rules can read the state. The formal model expresses this as a decode/project/re-encode transition; the current evidence uses decoded mesh/occupancy projection and trace proxies to test the gate.

### 5. Method overview figure lines 178-179

Current phrases:

> ... projection, and re-encoding commit.

> The projected asset is re-encoded as $u_{d+1}$ and paired with surviving active handles $A_{d+1}$; only this committed state is visible to later rules.

Issue: for a conceptual method figure this is acceptable, but it should not silently imply the exact current experimental path. Add a qualifier in the caption.

Replacement:

> ... projection, and codec commit in the formal transition.

> In the formal transition, the projected asset is re-encoded as $u_{d+1}$ and paired with surviving active handles $A_{d+1}$; in the current Trellis2 experiments, the same visibility contract is evaluated through sparse-latent updates plus decoded projection/trace diagnostics.

### 6. Method figure caption line 282

Current phrase:

> ... projection keeps only support that remains root-attached or connector-certified before re-encoding the next state.

Issue: over-specific if figure is used as implementation illustration.

Replacement:

> ... projection keeps only support that remains root-attached or connector-certified before the next state is exposed to later rules; codec re-entry is part of the formal transition and is separated from the current proxy-based evidence where appropriate.

### 7. Transition equations lines 327-340

Current phrases:

> The projected asset is then re-encoded:

> $u_{d+1} = \operatorname{Enc}_{\theta}(x^\star_{d+1},y)$

Issue: mathematically clean as a semantics, but the surrounding text does not mark it as formal/idealized relative to current code. Keep the equation if this section defines PS-RSLE, but insert an implementation boundary immediately after line 340.

Replacement addendum:

> This equation defines the codec-closed PS-RSLE transition. Our current Trellis2 runs instantiate the same admission contract with sparse-latent grammar states and per-depth decoded projection diagnostics; they should not be read as evidence that every reported grammar loop feeds a projected decoded mesh back through the Shape-SLat encoder at each depth.

### 8. Example transition line 347

Current phrases:

> optionally reusing cached transformer context for copied or overlapping support

> ... discarded before re-encoding.

Issues: KV/cache evidence is only optional/prototype-level. "Before re-encoding" again reads as executed path.

Replacement:

> The resampler perturbs and denoises the admitted sparse candidate under the predeclared policy $\psi_d$; when sampler hooks expose transformer keys and values, a cache policy can be used, but the reported experiments rely on feature-level masked blending unless otherwise stated. ... If a decoded island appears away from the parent path, its handle is deactivated or discarded before the next rule can read the state.

### 9. Algorithm lines 349-374

Current phrases:

> `\caption{PS-RSLE execution with per-depth projection.}`

> line 369: `$u_{d+1}\gets \operatorname{Enc}_\theta(x^\star_{d+1},y)$`

Issue: fine as formal pseudocode, but needs a caption qualifier so readers do not confuse it with the exact current Trellis2 loop.

Replacement:

> `\caption{Codec-closed PS-RSLE transition with per-depth projection.}`

Add after the algorithm:

> Algorithm~\ref{alg:ps-rsle-execution} specifies the full codec-closed semantics. The implementation evidence in Sec.~\ref{sec:projection-ablation} tests the same admission invariant using sparse-latent recursion and decoded projection/trace proxies; full per-depth decoded-mesh re-encoding is an implementation target rather than a claim of every reported run.

### 10. Controlled resampling line 403

Current phrase:

> Matched target tokens blend cached source keys/values with current-token keys/values by the ratio in $\psi_d$; unmatched tokens use the current context. This proportional cache reuse is a local consistency aid for copied motifs and overlap regions.

Issue: reads like implemented transformer KV reuse. The code-metric note found cache/sampler prototypes but not verified transformer key/value reuse in main results.

Replacement:

> When sampler hooks expose transformer keys and values, $\psi_d$ may request a source-context cache policy for copied or overlapping support. The current result-bearing implementation should be interpreted more narrowly: old sparse tokens are preserved and new tokens use feature-level masked blending after Shape-SLat flow sampling. Cache reuse remains optional and is not part of the validity evidence.

### 11. Projection subsection lines 419 and 429

Current phrases:

> Projection therefore tests the decoded candidate before it becomes the next executable state.

> Projection is performed in the decoded domain, where component membership and root reachability can be tested on the realized shape.

Issue: overstates implementation. The evidence supports decoded mesh/occupancy projection diagnostics and proxies, not necessarily that the projected decoded asset is the actual next encoded recursive state in the main loop.

Replacement:

> Projection therefore tests the candidate, using decoded mesh/occupancy evidence when available, before its active handles are allowed to seed the next executable state.

> In the codec-closed formulation, projection is performed in the decoded domain, where component membership and root reachability can be tested on the realized shape. In the current implementation, the decoded-domain quantities are measured as mesh/occupancy projection diagnostics and root-trace proxies tied back to the sparse-latent recursive trace.

### 12. Projection handle update line 437

Current phrase:

> Handles are projected with the support. For each $h_i\in\widetilde A_{d+1}$, the executor locates its owned or target support on the projected support...

Issue: can imply general handle recovery from arbitrary decoded GLBs. The metric note says root reach, handle survival, orphan-active are controlled trace proxies, not general GLB-derived runtime handle recovery.

Replacement:

> Handles are projected with the support in the controlled recursive trace. For each candidate handle, the executor or evaluation trace locates its owned or target support by the declared proposal transform, overlap, or nearest projected support, then checks root reachability or connector certification. These measurements are trace/mesh proxies for active-state validity, not general handle recovery from arbitrary decoded GLBs.

### 13. Projection figure caption lines 442-443

Current phrase:

> ... optional connector masks, and re-encoding to the next state.

> ... re-encodes only the projected active state.

Issue: same implementation ambiguity.

Replacement:

> ... optional connector masks, and codec-closed commit to the next state.

> In the full formal transition, projection keeps support that is root-reachable or covered by a rule-certified connector, deactivates orphan handles, and re-encodes only the projected active state. The diagram illustrates the intended method commit step; quantitative projection ablations report decoded mesh/occupancy and controlled trace proxies.

### 14. Projection bridge paragraph line 472

Current phrase:

> After projection, the projected asset is re-encoded by the generator codec in the outer transition, producing ... This decode--project--re-encode loop is essential.

Issue: highest-priority truthfulness patch. This is an unconditional implementation claim and directly conflicts with the comparison note.

Replacement:

> In the codec-closed PS-RSLE semantics, the projected asset is re-encoded by the generator codec in the outer transition, producing $u_{d+1}=\operatorname{Enc}_\theta(x^\star_{d+1},y)$ and the committed state $s_{d+1}=(u_{d+1},A_{d+1})$. This decode--project--re-encode loop is the clean semantic contract. The current Trellis2 evidence establishes the projection gate more conservatively: sparse-latent grammar states carry recursion, decoded meshes/occupancy supports are used to measure projection and root reachability, and handle-state quantities are controlled trace proxies. We therefore use the loop as the method contract, not as a blanket claim that every reported run re-encodes a projected decoded mesh at every depth.

### 15. Protocol line 510

Current phrase:

> No generator weights are updated, and costs are separated where possible for rule proposal, masked naturalization, decoding, projection, re-encoding, and optional rendering.

Issue: "costs are separated ... for re-encoding" implies measured per-depth re-encoding costs. The code evidence supports initial encoding and decoding timings, and likely not per-depth re-encoding after projection.

Replacement:

> No generator weights are updated, and costs are separated where possible for initial encoding, rule proposal, masked naturalization/flow sampling, decoding, projection diagnostics, and optional rendering. Per-depth projected-mesh re-encoding is part of the codec-closed formulation but should be reported only where explicitly run.

### 16. Section 4.4 line 537

Current phrase:

> Figure~\ref{fig:projection-depth-curves} shows that competition-style sparse growth preserves a dominant component through repeated decode/project/re-encode steps for vine and tree assets.

Issue: overclaims exact implementation path in the result section. This is one of the key requested Section 4.4 targets.

Replacement:

> Figure~\ref{fig:projection-depth-curves} shows that competition-style sparse growth preserves a dominant component across depth when decoded mesh/occupancy projection diagnostics are applied to the recursive trace for vine and tree assets.

Alternative if you want to retain method terminology:

> Figure~\ref{fig:projection-depth-curves} evaluates the decode/project/re-encode contract with the current proxy implementation: sparse-latent recursion supplies per-depth candidates, and decoded mesh/occupancy projection diagnostics show that competition-style growth preserves a dominant component for vine and tree assets.

### 17. Section 4.4 line 539

Current phrases:

> The table reports the state quantities that raw mesh component counts miss.

> ... low root reachability and handle survival ...

> ... keep root reachability at $1.0$, remove orphan active handles, and preserve handle survival ...

Issue: line 569 already says these are trace/mesh proxies, but the paragraph itself uses them as literal state quantities. Make the proxy boundary explicit in the narrative.

Replacement:

> The table reports controlled trace/mesh proxy quantities that raw mesh component counts miss.

> Final-only projection can make the terminal occupancy LCR look nearly perfect, but it leaves the same low root-reachability and handle-survival proxies because invalid trace handles have already been available to later rules.

> Connector-aware per-depth projection and full PS-RSLE keep the root-reachability proxy at $1.0$, remove orphan-active proxy handles, and preserve the handle-survival proxy in this conservative matrix.

### 18. Section 4.4 table caption line 569

Current phrase:

> Root reachability, orphan active handles, handle survival, and committed pass are trace/mesh proxies...

Assessment: good and should be preserved. Consider making "committed pass" less absolute.

Replacement:

> Root reachability, orphan-active count, handle survival, and committed-pass rate are controlled trace/mesh proxies...

### 19. Experiment 3 bridge line 583

Current phrase:

> ... copies the decoded support without typed handles, projection, or re-encoding.

Issue: acceptable for describing a negative control, but "or re-encoding" may imply PS-RSLE positives did re-encode in the current implementation. If that is not proven, describe the missing state machinery more generally.

Replacement:

> ... copies the decoded support without typed handles, projection-gated active state, or a codec-closed recursive transition.

### 20. Section 4.5 line 631

Current phrases:

> Without projection, rule-only and naturalized variants all fail the handle-state gate...

> masked local naturalization improves the local surface proxies...

> Global naturalization is a useful control because it is slightly smoother, but it is penalized by lower rendered-asset quality because old state is mutable.

Issue: mostly conservative, but "all fail" and "because old state is mutable" are causal/absolute. The metrics are deterministic proxies on a four-task, three-seed ablation. Tie the language to the proxy protocol.

Replacement:

> Under this controlled proxy protocol, variants without projection fail the handle-state gate...

> ... masked local naturalization improves the measured local surface proxies...

> Global naturalization is a useful control: it is slightly smoother under the reported roughness proxy, but receives a lower rendered-asset quality proxy in this protocol, consistent with the risk that old state is allowed to change.

### 21. Section 4.5 figure caption line 637

Current phrase:

> Projection is required for valid recursive state; masked local naturalization then improves local boundary smoothness without letting the frozen generator rewrite old global support.

Issue: "required" is defensible as method claim but too absolute as figure evidence; "without letting" is stronger than feature-level masked repair evidence. Better to say "is the tested mechanism" and "preserves previous sparse tokens."

Replacement:

> Projection is the tested mechanism for the valid-state gate; masked local naturalization then improves local boundary-smoothness proxies while preserving previous sparse tokens in the masked repair implementation. The figure supports a local geometry/asset-quality proxy claim, not global topology repair or final texture cleanup.

### 22. Section 4.5 table caption line 645

Current phrase:

> Projection closes the handle-state gate; masked local naturalization gives the best quality proxy among projected variants, while global naturalization is smoother but less faithful to local controlled realization.

Issue: should bind to the matrix/proxy protocol.

Replacement:

> In this controlled matrix, projection closes the proxy handle-state gate; masked local naturalization gives the best reported quality proxy among projected variants, while global naturalization is smoother under the roughness proxy but less faithful to local controlled realization.

### 23. Discussion line 691

Current phrase:

> ... leaving the same contaminated active-state statistics as no projection.

Issue: should say proxy/trace statistics.

Replacement:

> ... leaving the same contaminated active-state proxy statistics as no projection.

### 24. Discussion line 693

Current phrase:

> These boundaries do not change the main result: projection inside the recursive transition gives the executor a state-validity semantics that one-shot generation, direct sparse edits, and final-only cleanup lack.

Assessment: acceptable as semantic claim. Optional tighter replacement:

> These boundaries do not change the main result supported by the ablations: enforcing projection before later rule selection gives the executor a state-validity semantics that one-shot generation, direct sparse edits, and final-only cleanup lack.

### 25. Conclusion line 697

Current phrase:

> ... applies the frozen generator only for masked local realization and codec operations, and projects each decoded candidate to root-attached active state before the next rule can fire.

Issue: "each decoded candidate" may overstate implementation. Keep the story while respecting evidence.

Replacement:

> ... applies the frozen generator for masked local realization and codec operations, and enforces a projection gate so only root-attached active state is visible before the next rule can fire. In the current implementation this gate is supported by sparse-latent recursion, decoded mesh/occupancy diagnostics, and controlled handle-state proxies.

### 26. Appendix table line 786

Current phrase:

> decode/project/re-encode every depth

Issue: appendix still contains an unconditional implementation claim.

Replacement:

> projection-gated state every depth; codec-closed decode/project/re-encode in the formal transition

### 27. Appendix line 1026

Current phrase:

> ... active sparse state can be decoded, projected, and re-encoded at each finite depth.

Issue: again unconditional.

Replacement:

> ... active sparse state can be projection-gated at each finite depth, with decode/project/re-encode defining the codec-closed version of the transition.

## Phrases To Avoid Globally

- "re-encodes the projected state before later rules read it" unless explicitly framed as the full formal transition.
- "decode/project/re-encode every depth" as an empirical description of current Trellis2 runs.
- "projection is performed in the decoded domain" without noting current decoded-domain projection is evaluated via mesh/occupancy diagnostics and root-trace proxies.
- "KV cache improves results" or wording implying result-bearing transformer KV reuse.
- "handle survival" / "orphan active handles" / "root reachability" as general recovered state from arbitrary decoded GLBs; call them controlled trace/mesh proxies.
- "global naturalization is penalized because old state is mutable" as a proven causal mechanism; use "consistent with" or "reflecting the protocol risk."

## Safe Replacement Pattern

Use this pattern wherever a sentence must preserve the paper story without exceeding evidence:

> The formal PS-RSLE transition is codec-closed: decode, project to admissible root-attached active support, and re-encode before later rules read the state. The current Trellis2 implementation validates this contract through sparse-latent recursive updates, masked flow/blend local realization, decoded mesh/occupancy projection diagnostics, and controlled trace proxies for root reachability, orphan-active handles, and handle survival.

