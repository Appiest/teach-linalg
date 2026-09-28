# Day 20: Linear transformations between vector spaces

The opening reuses Day 1's arrows v = (3, 2) in yellow and w = (−1, 2) in blue with their teal sum, and Day 5's
quarter turn. The centerpiece reuses Day 10's two-picture habit: each polynomial keeps one color across its graph,
its formula and its derivative. p(t) = 1 + 2t + t² is yellow, q(t) = t − t³ is blue, and anything built from both is
teal. Glow (orange) marks only the sliding tangent, the tracing dot and the stamps where two routes agree.

The centerpiece is a commuting square of four graph panels that fills the frame. The top row holds polynomials and
the bottom row their derivatives. The left column holds the separate pieces and the right column their sum, so
"add then differentiate" runs across the top and down the right, and "differentiate then add" runs down the left
and across the bottom.

| t (s) | State | Trigger |
|---|---|---|
| 0–8 | Title card "Linear transformations between vector spaces", "Day 20"; glowing origin; grid draws | start |
| 8–15 | v, w, the teal sum and a faint teal parallelogram grow | caption "On Day 5, a matrix moved the plane and kept sums." |
| 15–22 | The parallelogram and its arrows turn a quarter turn about the origin; labels T(v), T(w), T(v + w) spring in; an orange ring marks the far corner | captions "A quarter turn carries the whole parallelogram along.", "So $T(\mathbf v + \mathbf w)$ is still $T(\mathbf v) + T(\mathbf w)$." |
| 22–27 | The rules panel writes T(u + v) = T(u) + T(v) and T(cu) = cT(u) | caption "Maps that keep sums and multiples are called linear." |
| 27–40 | Turn undone. The parallelogram and the glowing origin slide by b = (1, −1). Tip-to-tail T(v) + T(w) from the true origin lands at (4, 2), but T(v + w) sits at (3, 3); a dashed orange gap joins them | captions "A translation slides everything, even the origin.", "Now $T(\mathbf v) + T(\mathbf w)$ misses $T(\mathbf v + \mathbf w)$." |
| 40–48 | Panel: T(0) = T(0u) = 0T(u) = 0, one step at a time | captions "Every linear map must send $\mathbf 0$ to $\mathbf 0$.", "A translation moves $\mathbf 0$, so it is not linear." |
| 48–56 | Scrim. Definition card for T : V → W with the two rules for all u, v in V and every scalar c | captions "The same two rules make sense in any vector space.", "Let's test them on the derivative." |
| 56–64 | Square frame draws. Top-left panel: p (yellow) and q (blue) with their formulas | caption "Here are two polynomials in $\mathbb P_3$." |
| 64–72 | Top arrow "add" grows. Copies of p and q fly right and merge into the teal p + q | caption "First add them, then take the derivative." |
| 72–80 | Right arrow "D" grows. An orange tangent slides along p + q while a glow dot traces its slope, drawing the teal (p + q)′ in the bottom-right panel | caption "The height of the new curve is the slope of the old one." |
| 80–90 | Left arrow "D". Tangents slide along p and q together and trace p′ (yellow) and q′ (blue) in the bottom-left panel | caption "Now take each derivative first." |
| 90–100 | **Centerpiece:** bottom arrow "add". Copies of p′ and q′ fly right and become a dashed teal curve that settles exactly on (p + q)′; orange stamps flash at three matching points | captions "Then add the two derivatives.", "Both routes land on the same curve." |
| 100–104 | Hold | caption "So $D(\mathbf p + \mathbf q) = D\mathbf p + D\mathbf q$." |
| 104–120 | Right column swaps to scaling: top-right shows c·p, bottom-right shows D(c·p) solid and c·Dp dashed. c springs 1 → −1 → ½ → 1 and the two bottom curves never separate | captions "Scaling works the same way.", "$D(c\,\mathbf p) = c\,D\mathbf p$ for every $c$, so $D$ is linear." |
| 120–130 | Square clears. A 2 × 2 matrix A; its off-diagonal entries swap across the diagonal into Aᵀ; then (A + B)ᵀ = Aᵀ + Bᵀ | captions "Transposing a matrix is linear too.", "It only moves entries, so sums and multiples come along." |
| 130–140 | Two panels. Left: t² − 2, t², t² + 1 as three parallel parabolas with parallel orange tangents at t = 1. Right: all three collapse into the one line 2t | captions "Different inputs can share one output under $D$.", "So $D$ is not one-to-one." |
| 140–148 | Dashed t³ appears in the right panel, ringed; no input arrives | captions "No polynomial in $\mathbb P_3$ has derivative $t^3$.", "So $D$ is not onto $\mathbb P_3$ either." |
| 148–156 | Takeaway card with origin pulse | end |
