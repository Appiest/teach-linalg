# Day 36: Orthogonal projection

Day 35 introduced dot products, lengths, $W^\perp$ and orthogonal sets. Day 17 met the projection
$P = \tfrac12\begin{bmatrix}1&1\\1&1\end{bmatrix}$, which slides every point along $(1, -1)$ onto the diagonal. Today opens on that
same diagonal as the line $L$ and ends with the closest-point property in $\mathbb R^3$.

Colors for the whole lesson and the notes: $\mathbf y$ yellow, the subspace ($L$ or $W$) and $\hat{\mathbf y}$ teal (teal is the
output color, and Day 17 and Day 18 drew column spaces teal), the error $\mathbf z = \mathbf y - \hat{\mathbf y}$ pink (Day 17's
pink was the direction $P$ crushes), the basis vectors $\mathbf u_1$ green and $\mathbf u_2$ red, a trial point $\mathbf v$ blue,
and the right-angle mark orange.

Numbers (checked by hand):

- Line: $\mathbf u = (1, 1)$, $\mathbf y = (1, 5)$, $\mathbf y\cdot\mathbf u = 6$, $\mathbf u\cdot\mathbf u = 2$, $\hat{\mathbf y} = (3, 3)$,
  $\mathbf z = (-2, 2)$, and $P\mathbf y = (3, 3)$.
- Plane: $\mathbf u_1 = (1, 1, 0)$, $\mathbf u_2 = (-1, 1, 1)$, $\mathbf y = (2, 2, 3)$, weights $4/2$ and $3/3$,
  $\hat{\mathbf y} = (1, 3, 1)$, $\mathbf z = (1, -1, 2)$, distance $\sqrt6 \approx 2.45$.
- Trial point $\mathbf v = 0.5\,\mathbf u_1 + 1.5\,\mathbf u_2$: $11.25 = 6 + 5.25$.

| t (s) | State | Trigger |
|---|---|---|
| 0–6 | Title card "Orthogonal projection", "Day 36" | start |
| 6–10 | Origin pulse; grid draws with its origin low left | after title |
| 10–15 | Teal line $L$ draws; green $\mathbf u = (1,1)$ and yellow $\mathbf y = (1,5)$ grow | caption "Here is a vector $\mathbf y$ and the line $L$ through $\mathbf u$." |
| 15–22 | Hold on $L$, $\mathbf u$ and $\mathbf y$; $L$ flashes orange | captions "Yesterday the dot product told us when vectors are perpendicular." / "Today we find the point of $L$ closest to $\mathbf y$." / "Day 38 needs this when $A\mathbf x = \mathbf b$ has no solution." |
| 22–26 | Dashed drop from the tip of $\mathbf y$ to $L$; a teal dot pops at its foot | caption "Drop a perpendicular from the tip of $\mathbf y$ onto $L$." |
| 26–30 | Teal $\hat{\mathbf y}$ grows to the foot | caption "Its foot is the projection $\hat{\mathbf y}$, a multiple of $\mathbf u$." |
| 30–36 | Pink $\mathbf z$ replaces the drop; orange right-angle mark draws and flashes | caption "The leftover $\mathbf z = \mathbf y - \hat{\mathbf y}$ meets $L$ at a right angle." |
| 36–49 | Panel on the right: the weight formula, then $= \tfrac62\mathbf u = (3,3)$, then $\mathbf z\cdot\mathbf u = -2 + 2 = 0$; the plate grows with each row | three captions: the weight, the numbers, the check |
| 49–55 | Check row swaps for Day 17's $P\mathbf y = (3,3)$ | caption "Day 17's matrix $P$ was this same projection onto $L$." |
| 55–56 | Everything fades, caption included | end of the line section |
| 56–61 | Oblique 3D axes; the teal plane $W$ fades in; yellow $\mathbf y$ grows | caption "Now project $\mathbf y$ onto a plane $W$ in $\mathbb R^3$." |
| 61–65 | Dashed drop to $W$, teal $\hat{\mathbf y}$ grows | caption "Drop a perpendicular from $\mathbf y$ straight down to $W$." |
| 65–74 | **Centerpiece:** pink $\mathbf z$ with an orange glow and right-angle mark; the camera swings from azimuth 30° to 46° and back so the right angle holds from every side | caption "The error $\mathbf z$ stands at a right angle to all of $W$." |
| 74–76 | Hold on the plane, $\mathbf y$, $\hat{\mathbf y}$ and $\mathbf z$ | caption "We want a formula for $\hat{\mathbf y}$, not just a picture." |
| 76–80 | Panel lists $\mathbf u_1$, $\mathbf u_2$, $\mathbf y$; dashed green and red basis lines and the basis arrows appear in $W$ | caption "Give $W$ a basis whose vectors are perpendicular." |
| 80–87 | The two-term formula writes; dashed drops from $\mathbf y$ to each basis line; shadows $2\mathbf u_1$ and $\mathbf u_2$ grow; the numbers row lands on $(1,3,1)$ | caption "Project $\mathbf y$ onto each basis line separately." |
| 87–92 | The red shadow slides tip to tail onto $2\mathbf u_1$ and ends at $\hat{\mathbf y}$, which flashes | caption "Add the two shadows and you land exactly on $\hat{\mathbf y}$." |
| 92–95 | Green and red basis arrows flash orange | caption "Day 37 builds a perpendicular basis from any basis." |
| 95–100 | Two dot-product checks write under the panel | caption "Check: $\mathbf z$ is perpendicular to both $\mathbf u_1$ and $\mathbf u_2$." |
| 100–105 | Checks and numbers swap for $\mathbf y = \hat{\mathbf y} + \mathbf z$, $\hat{\mathbf y}\in W$, $\mathbf z\in W^\perp$, circled in orange | caption "Every $\mathbf y$ splits in exactly one way like this." |
| 105–116 | Blue point $\mathbf v$ in $W$ with a blue segment to $\mathbf y$ and a live $\|\mathbf y - \mathbf v\|$ readout; $\mathbf v$ springs to two other spots | captions "Is $\hat{\mathbf y}$ really the closest point…", "Slide another point $\mathbf v$ around $W$…" |
| 116–122 | Dashed teal leg from $\hat{\mathbf y}$ to $\mathbf v$ and a right-angle mark close a right triangle; Pythagoras writes with $11.25 = 6 + 5.25$ | caption "The path through $\hat{\mathbf y}$ makes a right triangle." |
| 122–130 | $\mathbf v$ springs onto $\hat{\mathbf y}$; readout settles at $2.45$; flash | captions "The distance is smallest exactly when $\mathbf v = \hat{\mathbf y}$.", "So $\hat{\mathbf y}$ is the best approximation…" |
| 130–141 | Takeaway card with origin pulse | end |
