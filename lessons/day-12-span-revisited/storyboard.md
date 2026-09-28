# Day 12: Span as the smallest subspace

Picks up from Day 2's picture in space: $\mathbf u = (2, -1, 1)$ in yellow and $\mathbf v = (1, 2, 1)$ in blue span
a teal plane through the origin. Day 2's pink $\mathbf b = (4, 3, 3)$ returns as the third vector $\mathbf w$, and
it stays pink. Multiples of $\mathbf u$ and $\mathbf v$ are drawn as faint lines in their own colours, and the span
is teal throughout. Orange marks only pivots, gaps and flashes.

| t (s) | State | Trigger |
|---|---|---|
| 0–6 | Title card "Span as the smallest subspace", "Day 12" | start |
| 6–10 | Glowing origin; 3D axes draw while the camera tilts into space; slow ambient turn begins | after title |
| 10–20 | $\mathbf u$ and $\mathbf v$ grow with tags; the teal sheet sweeps out from the origin | caption "On Day 2, $\mathbf u$ and $\mathbf v$ spanned this plane." then "Day 11 showed that every span is a subspace." |
| 20–27 | The sheet fades; only $\mathbf u$ and $\mathbf v$ remain | caption "Now take any subspace $H$ that holds $\mathbf u$ and $\mathbf v$." |
| 27–33 | Yellow line through $\mathbf u$ and blue line through $\mathbf v$ draw; panel line 1 "$c\mathbf u$ and $d\mathbf v$ are in $H$" | caption "Closed under scaling, $H$ holds every $c\mathbf u$ and $d\mathbf v$." |
| 33–40 | Sheet sweeps back out between the lines; panel line 2 "$c\mathbf u + d\mathbf v$ is in $H$" | caption "Closed under addition, it holds every sum $c\mathbf u + d\mathbf v$." |
| 40–48 | Panel line 3 "$\operatorname{Span}\{\mathbf u, \mathbf v\} \subseteq H$" in glow | captions "So every such $H$ contains the whole span." / "The span is the smallest subspace holding $\mathbf u$ and $\mathbf v$." |
| 48–54 | Panel fades | caption "$\{\mathbf u, \mathbf v\}$ is a spanning set, a recipe for this plane." |
| 54–64 | Pink $\mathbf w = (4, 3, 3)$ grows; blue $2\mathbf v$ springs tip to tail from $\mathbf u$ and lands on its tip; orange stamp | captions "Add Day 2's $(4, 3, 3)$ as a third vector $\mathbf w$." / "It lies in the plane, because $\mathbf w = \mathbf u + 2\mathbf v$." |
| 64–74 | Pinned formula $c_1\mathbf u + c_2\mathbf v + c_3\mathbf w = (c_1 + c_3)\mathbf u + (c_2 + 2c_3)\mathbf v$; the sheet flashes once and stays the same size | captions "Any combination using $\mathbf w$ folds back into $\mathbf u$ and $\mathbf v$." / "So this $\mathbf w$ is redundant, and the span stays put." |
| 74–82 | **Centerpiece begins:** $\mathbf w$'s last entry springs to $-1$; an orange dashed gap opens to the plane; camera swings nearly edge-on | caption "Now change its last entry to $-1$." |
| 82–96 | Copies of the teal sheet slide out along $\mathbf w$ in both directions, a stack of parallel planes | captions "Adding $c_3\mathbf w$ slides the whole plane along $\mathbf w$." / "The slid planes stack up and fill all of space." |
| 96–100 | Stack glows once | caption "One new direction grows the span from a plane to $\mathbb R^3$." |
| 100–104 | Space clears, camera flattens | after |
| 104–116 | Matrix $[\,\mathbf u\ \mathbf v\ \mathbf w\,]$ with coloured columns; echelon form fades in beside it; two orange pivot rings; the zero row is outlined | captions "Row reduction tells the two cases apart." / "With $\mathbf w = (4, 3, 3)$, the third row becomes all zeros." |
| 116–124 | Second row: the matrix with $-1$; echelon form with three pivot rings | caption "With $\mathbf w = (4, 3, -1)$, every row gets a pivot." |
| 124–132 | Matrices clear; theorem card "columns of $A$ span $\mathbb R^m$ $\iff$ pivot in every row" | caption "The columns span $\mathbb R^m$ exactly when every row has a pivot." |
| 132–140 | $[\,\mathbf u\ \mathbf v\,]$ reduces to a $3\times 2$ echelon form; its empty third row is outlined | captions "Two vectors give at most two pivots, one per column." / "So two vectors can never span all of $\mathbb R^3$." |
| 140–156 | $1 + t$, $t + t^2$, $1 + t^2$ in yellow, blue, pink; their coefficients fly into columns of a matrix with rows labelled $1, t, t^2$; echelon form with three pivot rings | captions "Polynomials in $\mathbb P_2$ work the same way." / "List the coefficients of $1$, $t$ and $t^2$ as columns." / "Every row has a pivot, so these three span $\mathbb P_2$." |
| 156–164 | Takeaway card with origin pulse | end |

The final render runs 150.9 s. The rows above are the plan, and the later beats land about 10 s earlier than listed.
