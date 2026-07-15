# Appendix rendered-text wording cleanup notes (2026-05-13)

Scope: active rendered appendix text in `main.tex` and active text included from appendix tables. This note intentionally does not edit `main.tex`, because appendix restructuring is happening elsewhere.

Overall recommendation: keep technical uses of "candidate", "projection", "control", "coverage", and "proxy" when they name method objects or metrics. Rewrite terms such as "status", "audit", "diagnostic", "readiness", "warning", "gap", and "supplementary" when they appear in rendered headings, captions, or roadmap prose and sound like internal draft tracking.

## Terms to keep versus rewrite

Keep in method or metrics context:

- "decoded candidate" and "candidate handles" in the projection algorithm. These are algorithmic inputs, not draft-status language.
- "candidate motif handles" in the rule-family table. This names a proposal object.
- "compatibility control", "classical controls", "control variable", and "matched controls". These are experimental-design terms.
- "coverage" in "coverage matrix" and "attractor coverage". These are method/evaluation concepts.
- "root reachability", "orphan active handles", and "handle survival". These are state metrics.

Rewrite or soften in rendered appendix text:

- "status" when used for appendix sections or table roles. Prefer "coverage", "summary", or "evidence scope".
- "audit" in labels is not rendered, but if labels are converted into headings during the appendix split, use "summary" or "measurements".
- "diagnostic" is acceptable for explicit measurement disclosures, but in publication-facing captions prefer "measurement", "metric", "analysis", or "rendered inspection" unless the point is explicitly a diagnostic-only result.
- "proxy" is acceptable only when the metric is explicitly a proxy. Avoid putting it in section names.
- "gap" in metric column names is concise, but prose should expand it as "difference" or "separation".
- "readiness" sounds like internal milestone language. Prefer "local realization quality" or "rendered local quality".
- "render warnings" sounds like a log artifact. Prefer "render checks" or "rendered inspection checks".
- "future evaluation" does not appear in active rendered appendix text. Do not introduce it.

## Operational Projection Routine (`main.tex` around 615-641)

No required wording change.

Acceptable active terms:

- "decoded candidate"
- "candidate handles"
- "projected asset"
- "inactive record for traceability"

Reason: these are formal algorithm objects and state-transition outcomes. Replacing them would make the algorithm less precise.

Optional low-risk polish:

- Current: "Algorithm~\\ref{alg:admissibility-projection} expands the projection operation used in Sec.~\\ref{sec:projection-ablation}."
- Proposed: "Algorithm~\\ref{alg:admissibility-projection} specifies the projection operation used in Sec.~\\ref{sec:projection-ablation}."
- Rationale: "specifies" sounds more formal than "expands" without changing meaning.

## Additional Tables (`main.tex` around 647-754)

### Rule families table

Keep "candidate motif handles" in the transform-copy proposal record. This is a method object.

### Operator-admission gates table

Suggested caption replacement:

- Current: "Operator-admission gates for rule design, specifying the structural, compatibility, projection, and render-readability evidence used to admit rule families into the PS-RSLE scheduler."
- Proposed: "Operator-admission gates for rule design, specifying the structural, compatibility, projection, and rendered-readability evidence required before a rule family is scheduled by PS-RSLE."

Suggested row replacements:

- Current: "Render/readability checks"
- Proposed: "Rendered-readability checks"

- Current: "Material-guided rendering, surface-voxel connectivity, render warnings, and guide sensitivity for projected meshes."
- Proposed: "Material-guided rendering, surface-voxel connectivity, render checks, and guide sensitivity for projected meshes."

- Current: "Render checks provide visual-readability evidence after the structural gates have passed."
- Proposed: "These checks provide visual-readability evidence after the structural gates have passed."

Rationale: "render warnings" sounds like a debugging log rather than a publication metric; "rendered-readability" is closer to the manuscript's claim vocabulary.

### Five-column protocol table

Suggested row replacement:

- Current: "local realization readiness"
- Proposed: "local realization quality"

Rationale: "readiness" reads like a milestone/status label. "Quality" matches the table's metrics row and the main paper's local-realization claim.

Optional row replacement:

- Current: "render checks"
- Proposed: "rendered-inspection checks"

Rationale: This makes clear that the checks concern the rendered artifact rather than renderer logs.

## Supplementary Material Overview (`main.tex` around 756-765)

Suggested paragraph replacement:

- Current: "This appendix starts on a new page and separates supplementary material from the focused experiment section:"
- Proposed: "The appendix organizes material that supports the focused experiment section:"

Rationale: "starts on a new page" is layout/process language, not scientific content.

Suggested item replacements:

- Current: "supplementary galleries, guide sweeps, and method-behavior displays."
- Proposed: "visual galleries, guide sweeps, and method-behavior studies."

- Current: "supplementary ablation tables summarizing evaluated variants and evidence scope."
- Proposed: "ablation coverage tables summarizing evaluated variants and evidence scope."

- Current: "supplementary handle-state summary for projection and masked-local projection variants."
- Proposed: "handle-state summary for projection and masked-local projection variants."

- Current: "supplementary CPU mesh measurements for Experiment~3 and the masked-naturalization manifest subset."
- Proposed: "CPU mesh measurements for Experiment~3 and the masked-naturalization manifest subset."

- Current: "supplementary scope notes for additional operator families."
- Proposed: "scope notes for additional operator families."

Suggested closing sentence replacement:

- Current: "Additional visual panels are grouped with the visual supplement, while tabular measurements are reported in the supplementary appendix."
- Proposed: "Additional visual panels are grouped with the gallery, while tabular measurements are reported with the corresponding appendix sections."

Rationale: repeated "supplementary" makes the roadmap sound like document management rather than a polished appendix.

## Ablation Coverage (`main.tex` around 769-772 plus included table)

Active rendered section title is acceptable: "Ablation Coverage".

Suggested prose replacement:

- Current: "This section reports evaluated ablation coverage and separates supplementary coverage tables from the matched ablation results used in the main text."
- Proposed: "This section reports ablation coverage and distinguishes broad variant coverage from the matched ablation results used in the main text."

Rationale: removes repeated "coverage" and "supplementary" while preserving the evidence hierarchy.

Included file `drafts/ablation_status_tables_20260510.tex` has no active rendered content; the status-table block is commented out. No appendix action needed unless that table is later uncommented. If it is restored, rewrite "status table", "missing", "appendix/status", and "experiment-closure/status table" before publication.

## Handle-State Summary (`main.tex` around 775-785 and included table)

Section title "Handle-State Summary" is good. It is more publication-facing than the internal label `state-proxy-audit`, which is not rendered.

Suggested prose replacement:

- Current: "Table~\\ref{tab:projection-admissible-state-proxy-summary} summarizes handle-state behavior over the twelve-row projection and masked-local blocks. It complements the mean aggregation in Table~\\ref{tab:projection-ablation} by reporting root reachability, orphan active handles, handle survival, strict pass counts, occupancy--state gap, and connector survival gap before later rule selection."
- Proposed: "Table~\\ref{tab:projection-admissible-state-proxy-summary} summarizes handle-state behavior over the twelve-row projection and masked-local blocks. It complements the mean aggregation in Table~\\ref{tab:projection-ablation} by reporting root reachability, orphan active handles, handle survival, strict pass counts, occupancy--state differences, and connector-survival differences before later rule selection."

Suggested caption replacement:

- Current: "Handle-state summary for projection and masked-local variants, reporting strict-pass counts, occupancy--state gap, and connector survival gap across the twelve-row blocks."
- Proposed: "Handle-state summary for projection and masked-local variants, reporting strict-pass counts, occupancy--state differences, and connector-survival differences across the twelve-row blocks."

Included table column replacements in `drafts/projection_admissible_state_proxy_summary_20260513.tex`, if the parent agent later allows table edits:

- Current: "Occ.--state gap"
- Proposed: "Occ.-state diff."

- Current: "Conn. surv. gap"
- Proposed: "Conn. surv. diff."

Rationale: "gap" is understandable but carries audit/status flavor. "difference" is more neutral in prose; abbreviated "diff." fits table columns.

## Supplementary Mesh Measurements (`main.tex` around 790-813 and included table)

Section title "Supplementary Mesh Measurements" is acceptable, but can be cleaner.

Suggested title replacement:

- Current: "Supplementary Mesh Measurements"
- Proposed: "Additional Mesh Measurements"

Suggested prose replacement:

- Current: "These measurements add mesh-level connectivity detail alongside the occupancy, surface-voxel LCR, and recursive-state metrics reported in the main experiments."
- Proposed: "These measurements add mesh-level connectivity detail to the occupancy, surface-voxel LCR, and recursive-state metrics reported in the main experiments."

Suggested table prose replacement:

- Current: "Table~\\ref{tab:masked-naturalization-topology-audit} reports CPU mesh measurements for the masked-naturalization manifest subset."
- Proposed: "Table~\\ref{tab:masked-naturalization-topology-audit} reports CPU mesh-topology measurements for the masked-naturalization manifest subset."

Suggested caption replacement:

- Current: "Mesh-topology measurements for the masked-naturalization manifest subset, reporting median raw and welded components plus counted watertight rows."
- Proposed: keep as-is.

Rationale: the caption is already publication-level. The label contains "audit" but is not rendered.

## Supplementary Gallery and Method Figures (`main.tex` around 857-860)

Suggested title replacement:

- Current: "Supplementary Gallery and Method Figures"
- Proposed: "Additional Gallery and Method Figures"

Suggested prose replacement:

- Current: "This appendix collects supplementary galleries, guide sweeps, method-behavior displays, and stress-case measurements that contextualize the main experiments."
- Proposed: "This appendix collects visual galleries, guide sweeps, method-behavior studies, and stress-case measurements that contextualize the main experiments."

Rationale: avoids repeated "supplementary" and replaces "displays" with the more scientific "studies".

## Classical Procedural Systems as Restricted Rule Families (`main.tex` around 976-990)

No required wording change.

Acceptable active terms:

- "structural baselines"
- "exact equivariance would require..."
- "approximate metric"

These are appropriately scoped and not draft/status language.

## Supplementary Scope Notes (`main.tex` around 992-994)

Suggested title replacement:

- Current: "Supplementary Scope Notes"
- Proposed: "Scope Notes"

Suggested prose replacement:

- Current: "The supplementary measurements cover radial, echo, hard-DLA bridge, texture, material, cache-selection, and render/import cases, illustrating where projection-stabilized execution preserves state and where additional operator design expands the scheduler."
- Proposed: "The additional measurements cover radial, echo, hard-DLA bridge, texture, material, cache-selection, and render/import cases, illustrating where projection-stabilized execution preserves state and where additional operator design expands the scheduler."

Rationale: reduces document-management language while keeping the scope boundary intact.

## Highest-priority low-risk edits for the parent agent

1. Replace layout/process wording in the appendix roadmap: "starts on a new page" and repeated "supplementary".
2. Replace "local realization readiness" with "local realization quality" in the five-column protocol table.
3. Replace "render warnings" with "render checks" in the operator-admission table.
4. Replace prose uses of "gap" with "difference" in the handle-state summary; keep abbreviated column names only if table width requires them.
5. Rename visible headings from "Supplementary ..." to "Additional ..." or shorter section titles where the appendix context already makes the material supplementary.
