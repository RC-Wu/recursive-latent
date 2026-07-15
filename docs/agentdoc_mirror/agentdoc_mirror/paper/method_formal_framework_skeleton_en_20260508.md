# Method Formal Framework Skeleton for SIGGRAPH Asia Draft

Created: 2026-05-08  
Purpose: English method-section skeleton distilled from the strengthened PS-RSLG v2 formalism. This file is not a replacement for `paper_siga/main.tex`; it is a structured source block for rewriting the Method section.

## Recommended Method Claim

We should frame the method as:

> Projection-Stabilized Sparse-Latent Recursive Grammar (PS-RSLG), an operational semantics for finite-depth recursive 3D asset generation in the sparse state space of a frozen native 3D generator.

The safe main contribution is not an unconditional infinite generator and not a guaranteed topology-preserving flow sampler. The safe contribution is a grammar/state formalism plus a projection-stabilized recursive loop.

## 1. Problem Setting

Let \(x_0\) be a root mesh or a generated root asset, \(y\) be an optional condition, and \(D\) be a finite recursion depth. We seek a finite-depth asset

\[
x_D = \mathcal{O}(S_D),\qquad
S_{d+1}\sim \mathbb{T}_{\mathcal{G},\theta,d}(\cdot\mid S_d,y,\xi_d),
\]

where \(\mathcal{G}\) is a recursive grammar, \(\theta\) is a frozen Trellis2/Trellis-style native 3D generator, and \(\xi_d\) denotes stochasticity from grammar choices or local generative sampling.

Suggested prose:

> Unlike image-guided one-shot generation, the grammar is not a final loss or a prompt. It is the program that evolves the 3D state. Unlike classical procedural modeling, the state is not only curves, cylinders, or mesh templates; it is a sparse latent asset state that can be decoded, projected, re-encoded, and optionally exported with material information.

## 2. Recursive State

Use:

\[
S_d=(C_d,F_d,U_d,A_d,B_d,M_d,H_d,K_d).
\]

Definitions for main text:

- \(C_d\subset\{0\}\times h\mathbb{Z}^3\): active sparse O-Voxel/SLAT support.
- \(F_d:C_d\rightarrow\mathbb{R}^{q_s}\times\mathbb{R}^{q_m}\): shape and optional material latent features.
- \(U_d\): typed grammar symbols and anchors, including tips, patches, portals, tiles, crystal faces, attractor cells, and LOD chunks.
- \(A_d\): auxiliary fields, including occupancy, attractors, frontiers, component graphs, attachment graphs, collision fields, quality scores, and symmetry/lattice metadata.
- \(B_d\): edit masks, boundary regions, and blend kernels.
- \(M_d\): material intent, texture/PBR latent state, and local naturalization schedule.
- \(H_d\): recursion depth, random seeds, rule trace, transform trace, projection parameters, and diagnostics.
- \(K_d\): motif, latent, transform, LOD, window, and sampler caches.

Suggested prose:

> The state deliberately separates structural ownership from visual naturalization. The grammar owns support, anchors, and constraints; the frozen generator supplies a mesh-derived sparse representation, local latent priors, decoding, re-encoding, and optional material export.

## 3. Grammar Definition

Define:

\[
\mathcal{G}=
(\Sigma,\mathcal{T},\mathcal{R},\mathcal{I},\mathcal{S},
\Pi,\mathcal{N}_\theta,\mathcal{D}_\theta,\mathcal{E}_\theta,
\mathcal{P},\mathcal{C},\mathcal{O}).
\]

Main-text definitions:

- \(\Sigma\): typed symbol alphabet.
- \(\mathcal{T}\): transform group or semigroup, including rigid transforms, scaling, mirroring, portal embeddings, lattice translations, contraction maps, and LOD transforms.
- \(\mathcal{R}\): stochastic context-sensitive rewrite rules.
- \(\mathcal{I}\): interpretation map from symbols and frames to sparse support, features, masks, or mesh regions.
- \(\mathcal{S}\): scheduler for synchronous, asynchronous, priority, frontier, or group-orbit rule application.
- \(\Pi\): occupancy, attachment, topology, competition, symmetry, renderability, and token-budget constraints.
- \(\mathcal{N}_\theta\): frozen masked flow/SDE naturalization kernel.
- \(\mathcal{D}_\theta,\mathcal{E}_\theta\): frozen decoder and mesh-to-sparse re-encoder.
- \(\mathcal{P}\): projection family onto admissible recursive asset states.
- \(\mathcal{C}\): cache lookup/update semantics.
- \(\mathcal{O}\): observable/export map to mesh, GLB, renders, and metrics.

Rule schema:

\[
r:\;X(\omega,\Omega,\ell,a,h)
\Rightarrow
\{(X_j,T_j,\Omega_j,\rho_j,\mu_j,\beta_j,\psi_j,\zeta_j,\tau_j,\pi_j)\}_{j=1}^{m}.
\]

Suggested explanation:

> The right-hand side emits typed symbols, transforms, target edit regions, proposal kernels, masks, blend kernels, preconditions, random seeds, sampler schedules, and local constraints. A proposal kernel may be a deterministic transform-copy, an attractor-directed growth rule, a DLA hitting kernel, a shape split, a cache lookup, or a masked generative sampler.

Rule choice:

\[
\Pr(r\mid S_d,u_i)=
\frac{\exp a_r(S_d,u_i)}
\sum_{r'\in\mathcal{R}(u_i)}\exp a_{r'}(S_d,u_i)}.
\]

For the current paper, state that most experiments use deterministic or low-entropy rule choices, while the formalism also supports stochastic variants.

## 4. Operational Semantics

This is the central equation:

\[
S_{d+1}
=
\mathcal{C}_{d+1}\circ
\mathcal{E}_\theta\circ
\mathcal{P}_{\lambda_d}\circ
\mathcal{D}_\theta\circ
\mathcal{N}_{\theta,\Omega_d}^{\tau_d\rightarrow0}\circ
\Theta_{\Pi_d}\circ
\operatorname{Merge}_{B_d}\circ
\operatorname{Prop}_{R_d^\star}(S_d).
\]

Suggested prose:

> A recursive step first proposes sparse patches from selected rules, merges them with mask and blend weights, applies competition and constraints, optionally naturalizes the local edited region with a frozen masked sampler, decodes the candidate, projects it to an admissible recursive asset, re-encodes the projected mesh, and updates caches. Projection is therefore inside the recursive map, not a post-hoc cleanup step.

Algorithm block skeleton:

```text
Algorithm: Projection-Stabilized Sparse-Latent Recursive Grammar
Input: root asset x0, grammar G, frozen generator N_theta, depth D
S0 <- E_theta(x0)
initialize symbols, fields, masks, history, caches
for d = 0 ... D-1:
    R*_d <- Scheduler(S_d, R)
    P_d <- Prop_{R*_d}(S_d)
    S^+ <- Merge_B(S_d, P_d)
    S^c <- CompetitionAndConstraints(S^+, Pi_d)
    S^n <- MaskedNaturalization(S^c, N_theta, masks, y, tau_d)
    x_raw <- D_theta(S^n)
    x_proj <- Project(x_raw, lambda_d, fields, history)
    S_{d+1} <- E_theta(x_proj)
    K_{d+1} <- UpdateCaches(K_d, S_{d+1}, R*_d)
return O(S_D)
```

## 5. Proposal and Merge Details

Transform-copy:

\[
\hat C_j=Q_h(T_j(C_d\cap\Omega)),\qquad
\hat F_j(Q_h(T_jc))=\mathcal{T}_j^F F_d(c).
\]

Merge:

\[
C^+=C_d\cup\bigcup_j\hat C_j,
\]

\[
F^+(c)=
\frac{w_0(c)F_d(c)+\sum_j w_j(c)\hat F_j(c)}
{w_0(c)+\sum_jw_j(c)+\epsilon},
\qquad
w_j(c)=\mu_j(c)\beta_j(c).
\]

Sparse competition score:

\[
\psi(a,c;S_d)=
\lambda_{\mathrm{att}}\phi_{\mathrm{att}}
-\lambda_{\mathrm{occ}}\phi_{\mathrm{occ}}
-\lambda_{\mathrm{col}}\phi_{\mathrm{collision}}
+\lambda_{\mathrm{front}}\phi_{\mathrm{frontier}}
+\lambda_{\mathrm{grp}}\phi_{\mathrm{orbit}}
+\epsilon_\theta(c,\xi).
\]

Suggested prose:

> The first terms reproduce classical attractor, occupancy, collision, and frontier logic. The optional \(\epsilon_\theta\) term represents stochastic preference from the frozen generator, but in the current implementation the competition operator is mostly conservative and deterministic.

## 6. Masked Naturalization

SDE/flow form:

\[
dZ_t=v_\theta(Z_t,t,y,\Omega)\,dt+\sigma(t)\,dW_t,\qquad t:\tau\rightarrow0.
\]

Masked clamp:

\[
Z_{t-\Delta t}\leftarrow
(1-\mu_\Omega)\odot Z_{\mathrm{anchor}}
+\mu_\Omega\odot \Phi_{\theta,t}(Z_t,y).
\]

Sample selection:

\[
k^\star=
\arg\min_k
\left[
V_{\mathrm{frag}}(P(D_\theta(S^{(k)})))
+\lambda_aV_{\mathrm{attach}}(P(D_\theta(S^{(k)})))
+\lambda_sV_{\mathrm{sym}}(P(D_\theta(S^{(k)})))
-\lambda_qQ_{\mathrm{nat}}(S^{(k)})
\right].
\]

Safe prose:

> The frozen sampler is used as a local naturalization prior under masks and constraints. It does not own the global recursive scaffold. Our experiments show that global flow repair can overwrite recursive topology; therefore the current paper treats masked local naturalization as a controlled component with mixed evidence rather than as a solved topology-preserving sampler.

## 7. Projection-Stabilized Recursion

Admissible asset set:

\[
\mathcal{S}_{\mathrm{adm}}(\lambda)=
\{S:
V_{\mathrm{frag}}\leq\epsilon_f,\,
V_{\mathrm{attach}}\leq\epsilon_a,\,
V_{\mathrm{occ}}\leq\epsilon_o,\,
V_{\mathrm{sym}}\leq\epsilon_g,\,
V_{\mathrm{render}}\leq\epsilon_r,\,
|C|\leq T_{\max}\}.
\]

Projection:

\[
\mathcal{P}_{\lambda}(x)=
\arg\min_{y\in\mathcal{X}_{\mathrm{adm}}}
d_{\mathrm{mesh}}(x,y)
+\lambda_1V_{\mathrm{frag}}(y)
+\lambda_2V_{\mathrm{attach}}(y)
+\lambda_3V_{\mathrm{render}}(y)
+\lambda_4V_{\mathrm{sym}}(y)
+\lambda_5d_{\mathrm{support}}(E_\theta(x),E_\theta(y)).
\]

Per-depth:

\[
S_{d+1}=E_\theta\circ P_{\lambda_d}\circ D_\theta\circ G_d(S_d).
\]

Final-only baseline:

\[
S_D^{\mathrm{final}}
=E_\theta\circ P_{\lambda_D}\circ D_\theta
\circ G_{D-1}\circ\cdots\circ G_0(S_0).
\]

Projection proposition, safe main-text version:

> If each per-depth projection suppresses invalid fragment mass to \(\epsilon_P\), and the decode/re-encode loop adds at most \(\epsilon_E\) invalid mass, then every projected recursive state satisfies \(e(S_d)\leq\epsilon_P+\epsilon_E\) for \(1\leq d\leq D\). Final-only cleanup does not provide this per-depth state invariant, because invalid components may influence later frontier, sampler, and history states before they are removed.

Short proof:

\[
e(P_{\lambda_d}(X))\leq\epsilon_P,\qquad
e(E_\theta(Y))\leq e(Y)+\epsilon_E
\Rightarrow
e(S_{d+1})\leq\epsilon_P+\epsilon_E.
\]

Do not claim that final-only projection always fails. Claim only that it lacks the same invariant and can allow intermediate invalid states to affect subsequent recursion.

## 8. Coverage of Classical Procedural Systems

Use a compact table in the main paper and move proof details to supplementary material.

| Family | PS-RSLG specialization | Main-text status |
|---|---|---|
| IFS | One symbol, transform-copy rules, union merge, identity sampler/projection | Safe |
| L-system | Ordered symbol sequence or graph, synchronous rewriting, turtle/frame interpretation | Safe |
| Space colonization | Tip symbols, attractor field, nearest-tip assignment, occupancy exclusion | Safe and central |
| DLA/frontier accretion | Frontier symbol and hitting distribution proposal | Safe as coverage, experiments as stress test |
| Shape grammar/CGA | Finite local scope symbols with split/extrude/repeat/replace transforms | Safe only for finite local subfamily |
| Symmetry/crystal | Group/lattice action, orbit expansion, approximate commutation conditions | Conditional |
| Infinite recursion | Contractive IFS limit or bounded visible-window/LOD cache | Extension, not achieved infinite mesh |

Suggested coverage proposition:

> By choosing identity sampler/projection variants and restricting the scheduler and interpretation map, PS-RSLG reduces to finite-step instances of IFS, L-systems, space colonization, DLA-like frontier accretion, and finite local shape grammars. Symmetry and crystal programs are represented by group or lattice actions, with exact equivariance only under exact commutation and approximate symmetry controlled by accumulated commutation errors.

## 9. Symmetry, Crystal, and Cache

Symmetry condition:

\[
\forall g\in G,\ r\in R,\qquad g\circ r\circ g^{-1}\in R.
\]

Approximate commutation statement:

\[
d_{\mathcal S}(\mathbb{T}(gS),g\mathbb{T}(S))
\leq
\epsilon_{\mathrm{rule}}
\epsilon_{\mathrm{merge}}
\epsilon_{\mathrm{sampler}}
\epsilon_{\mathrm{proj}}
\epsilon_{\mathrm{codec}}
\quad\text{up to Lipschitz factors}.
\]

Crystal/window:

\[
C_{d+1}=C_d\cup\bigcup_{\lambda\in\Lambda\cap W_d}Q_h(T_\lambda C_{\mathrm{cell}}).
\]

Cache:

\[
K_d=(K_d^{\mathrm{motif}},K_d^{\mathrm{latent}},K_d^{\mathrm{transform}},
K_d^{\mathrm{LOD}},K_d^{\mathrm{window}},K_d^{\mathrm{sampler}}).
\]

Bounded visible-window claim:

\[
\sum_{\Omega\in W_t}|C_{\Omega,t}^{\mathrm{active}}|\leq T_{\max}.
\]

Safe prose:

> We output finite-depth assets. Unbounded logical recursion can be approximated by contractive transforms or by decoding only a bounded visible window and representing off-window regions with LOD/cache descriptors. This is an extension target in the current system rather than a demonstrated unbounded generator.

## 10. Claims Suitable for Main Paper

Use these in the main Method or Contributions:

1. PS-RSLG defines recursive 3D asset generation as typed rewriting over sparse mesh-derived latent states.
2. Classical recursive/procedural systems are recovered as special cases or finite-step degenerations.
3. Trellis2/frozen 3D generation enters as representation, local masked naturalization, decoder, re-encoder, and optional material export; it does not replace the grammar.
4. Projection is part of the recursive transition, not a final cleanup step.
5. Under explicit assumptions, per-depth projection bounds invalid fragment mass at every recursive depth.
6. Space competition is a concrete operator that bridges classical attractor growth and sparse latent recursive growth.

## 11. Claims for Appendix or Risk Notes

Put these in appendix, limitation, or future work:

1. Full constructive proofs for IFS and L-system coverage.
2. DLA Markov-kernel coverage and frontier stress-test discussion.
3. Finite local shape-grammar coverage proof.
4. Approximate equivariance error bound for symmetry/crystal rules.
5. Visible-window/LOD/cache active-memory proposition.
6. Contractive recursion limit via standard Hutchinson/IFS theory.
7. Explanation that final-only cleanup lacks the per-depth invariant but is not theoretically guaranteed to fail in every case.

Avoid these as main claims:

1. The implementation guarantees exact symmetry or crystal equivariance.
2. Full flow/SDE repair preserves recursive topology.
3. The system implements true infinite 3D generation.
4. The grammar covers all possible shape grammars.
5. Trellis2 texture/PBR quality is uniformly solved across categories.

## 12. Suggested Method Section Order

1. Problem setting and finite-depth asset objective.
2. Recursive sparse-latent state.
3. Grammar definition and rule schema.
4. Operational semantics with the central composed operator and algorithm block.
5. Classical procedural systems as special cases.
6. Sparse competition and masked naturalization.
7. Projection-stabilized recursion and the weak stability proposition.
8. Symmetry, crystal, cache, and infinite-recursion boundary.

## 13. One-Paragraph Method Summary

Projection-Stabilized Sparse-Latent Recursive Grammar represents a recursive asset as a typed sparse state \(S_d=(C,F,U,A,B,M,H,K)\) in the mesh-derived latent space of a frozen native 3D generator. A grammar rule proposes transformed or newly grown sparse patches, merges them under masks, filters them through competition and attachment constraints, optionally naturalizes edited regions with a masked frozen flow/SDE sampler, decodes the candidate to a mesh, projects the mesh to an admissible recursive asset state, re-encodes it, and updates caches. Classical IFS, L-systems, space-colonization, DLA-like frontier accretion, and finite local shape grammars arise as special cases by choosing identity sampler/projection and appropriate schedulers. The central design choice is per-depth projection: decoded errors are removed before they can seed the next recursive step, giving a state invariant under explicit projection and codec assumptions.
