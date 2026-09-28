# Day 35: Dot products and orthogonality

The video brings back Day 1's vectors: yellow $\mathbf v = (3, 2)$ and blue $\mathbf w = (-1, 2)$. Their dot product is
$1$, so they are almost perpendicular, and their tips sit at the same height, so $\mathbf v - \mathbf w = (4, 0)$ and the
distance between them is exactly 4. Walking guides are green (first entry) and red (second entry) as on Day 1.

The centerpiece keeps $\mathbf v$ fixed with a faint yellow line through it and spins $\mathbf w$ (length $\sqrt5$) around
the origin. A dashed drop line runs from the tip of $\mathbf w$ to the line of $\mathbf v$, and the shadow from the origin
to the foot is a thick bar: teal while it points along $\mathbf v$, pink once it points backward. A small orange arc marks
$\theta$ and becomes a right-angle mark at $90^\circ$. The readout $\mathbf v\cdot\mathbf w$ follows live.

The last third reuses the perpendicular direction $\mathbf u = (-2, 3)$ in blue: the line $W^\perp$, the row of
$A = [\,3\ \ 2\,]$, and the orthogonal basis $\{\mathbf v, \mathbf u\}$ with teal $\mathbf y = (5, -1) = \mathbf v - \mathbf u$.

| t (s) | State | Trigger |
|---|---|---|
| 0–7 | Title card "Dot products and orthogonality", "Day 35"; glowing origin; grid draws | start |
| 7–12 | Yellow $\mathbf v = (3, 2)$ and blue $\mathbf w = (-1, 2)$ grow with names | caption "Here are Day 1's vectors…" |
| 12–24 | Top-left plate: $[3;2]\cdot[-1;2]$. Each matching pair of entries flashes orange and its product drops in; "= 1" lands | captions "The dot product multiplies matching entries and adds them." / "The result $\mathbf v\cdot\mathbf w = 1$ is a number…" |
| 24–33 | Green "3" and red "2" walking guides draw under $\mathbf v$; plate becomes $\mathbf v\cdot\mathbf v = 13$, then $\|\mathbf v\| = \sqrt{13}$ | captions "Dot $\mathbf v$ with itself…" / "By Pythagoras…" |
| 33–42 | Teal arrow from the tip of $\mathbf w$ to the tip of $\mathbf v$; a copy springs to the origin as $(4, 0)$; plate reads $\operatorname{dist} = 4$ | captions "The distance between the tips…" / "Moved to the origin…" |
| 42–72 | **Centerpiece.** Faint line through $\mathbf v$, drop line, shadow bar, angle arc and live readout. $\mathbf w$ swings to $\theta = 0$ (value 8.06), eases to $60^\circ$ (4.03), lands at $90^\circ$ (shadow gone, right-angle mark, readout 0.00 in orange), then sweeps to $180^\circ$ (pink shadow, −8.06). The rule $\|\mathbf v\|\|\mathbf w\|\cos\theta$ joins the plate; $\mathbf w$ returns to $90^\circ$ | one caption per stop, then "The rule is…" / "Two vectors with $\mathbf v\cdot\mathbf w = 0$ are orthogonal." |
| 72–92 | Shadow leaves. Gray $-\mathbf w$ appears opposite $\mathbf w$; blue and gray dashed segments join the tip of $\mathbf v$ to both, with live lengths. $\mathbf w$ swings to $40^\circ$ (lengths differ), then back to $90^\circ$ (both 4.24). The plate expands $\|\mathbf v \mp \mathbf w\|^2$; then $18 = 13 + 5$ | captions "Compare how far $\mathbf v$ is from…" / "The two distances agree only at a right angle." / "Expanding both…" / "At a right angle this is Pythagoras…" |
| 92–108 | Blue line $W^\perp$ through $\mathbf u = (-2, 3)$ crosses the yellow line $W$ with a right-angle mark. Plate: $A = [\,3\ \ 2\,]$, $A\mathbf x = \mathbf v\cdot\mathbf x$, then $\operatorname{Nul}A = (\operatorname{Row}A)^\perp$ | captions "Every vector orthogonal to $W$ lies on one line, $W^\perp$." / "Put $\mathbf v$ in the row…" / "So…" |
| 108–126 | Lines fade. Blue $\mathbf u$ stays; teal $\mathbf y = (5, -1)$ grows. Plate computes $c_1 = 13/13 = 1$, $c_2 = -13/13 = -1$; a blue $-\mathbf u$ springs from the tip of $\mathbf v$ to the tip of $\mathbf y$ | captions "$\{\mathbf v, \mathbf u\}$ is an orthogonal basis…" / "Each weight is one ratio of dot products." / "So $\mathbf y = \mathbf v - \mathbf u$…" |
| 126–134 | Dashed unit circle; $\mathbf v$ and $\mathbf u$ shrink by $\sqrt{13}$ onto it | caption "Divide each by its length and the set is orthonormal." |
| 134–142 | Takeaway card with origin pulse | end |
