# Day 37: Gram–Schmidt

The video stays in one oblique view of $\mathbb R^3$, the orbiting view from Days 16 and 18. The input basis is
$\mathbf x_1 = (1, 1, 0)$ in yellow, $\mathbf x_2 = (1, 0, 1)$ in blue and $\mathbf x_3 = (0, 1, 1)$ in pink. Each
$\mathbf v_k$ keeps the color of the $\mathbf x_k$ it came from, because it is the same arrow after straightening.
Shadows (projections) are purple-gray arrows lying along the earlier vectors, the drop from a tip to its shadow is a
dashed line in the arrow's own color, and right angles are small orange corners at the origin. The formula panel
sits top right and uses the same colors, with the shadow coefficients in purple-gray.

The numbers: $\mathbf v_2 = \mathbf x_2 - \tfrac12\mathbf v_1 = (\tfrac12, -\tfrac12, 1)$ and
$\mathbf v_3 = \mathbf x_3 - \tfrac12\mathbf v_1 - \tfrac13\mathbf v_2 = (-\tfrac23, \tfrac23, \tfrac23)$. Normalizing gives
$\mathbf u_1 = \tfrac1{\sqrt2}(1, 1, 0)$, $\mathbf u_2 = \tfrac1{\sqrt6}(1, -1, 2)$ and $\mathbf u_3 = \tfrac1{\sqrt3}(-1, 1, 1)$,
and $R = Q^TA$ has diagonal $\sqrt2$, $3/\sqrt6$, $2/\sqrt3$, the lengths of the $\mathbf v$'s.

| t (s) | State | Trigger |
|---|---|---|
| 0–7 | Title card "Gram–Schmidt", "Day 37"; glowing origin | start |
| 7–13 | Axes and floor draw; $\mathbf x_1$, $\mathbf x_2$, $\mathbf x_3$ grow one by one with labels | caption "These three arrows form a basis for $\mathbb R^3$." |
| 13–22 | Camera orbits 14° to the working view | captions "But no two of them meet at a right angle." / "Gram–Schmidt straightens them, one vector at a time." |
| 22–25 | Label $\mathbf x_1$ becomes $\mathbf v_1$; a faint yellow line through $\mathbf v_1$ draws | caption "Keep the first one as it is: $\mathbf v_1 = \mathbf x_1$." |
| 25–31 | Dashed blue drop from $\mathbf x_2$'s tip to the line; purple-gray shadow $\tfrac12\mathbf v_1$ grows. Panel writes $\mathbf v_2 = \mathbf x_2 - \frac{\mathbf x_2\cdot\mathbf v_1}{\mathbf v_1\cdot\mathbf v_1}\mathbf v_1$ and the weight $= \tfrac12$ | captions "$\mathbf x_2$ casts a shadow on the line through $\mathbf v_1$." / "That shadow is the part of $\mathbf x_2$ that leans along $\mathbf v_1$." |
| 31–38 | **Centerpiece, first half.** $\mathbf x_2$'s tip springs back by the shadow while the shadow shrinks into the origin and the drop line slides down onto the new arrow. An orange corner marks $\mathbf v_1 \perp \mathbf v_2$; label becomes $\mathbf v_2$; panel shows the column arithmetic | caption "Subtract it, and $\mathbf x_2$ swings up to a right angle." |
| 38–48 | Teal sheet $\operatorname{Span}\{\mathbf v_1, \mathbf v_2\}$ replaces the line. Dashed pink drop from $\mathbf x_3$ to the sheet; shadows $\tfrac12\mathbf v_1$ and $\tfrac13\mathbf v_2$ grow with dashed edges completing their sum. Panel writes the two-term formula and its numbers | captions "$\mathbf v_1$ and $\mathbf v_2$ span a plane." / "$\mathbf x_3$ casts a shadow on each of them." |
| 48–56 | **Centerpiece, second half.** Both shadows shrink as $\mathbf x_3$ springs off the plane to $\mathbf v_3$; two orange corners mark it perpendicular to both; panel shows $(-\tfrac23, \tfrac23, \tfrac23)$ | caption "Subtract both shadows, and $\mathbf x_3$ stands straight up." |
| 56–64 | Sheet leaves; three dot products $= 0$ appear; camera swings 40° and back so the right angles hold from another side | caption "Now every pair has dot product zero." |
| 64–77 | Panel $\mathbf u_k = \mathbf v_k/\lVert\mathbf v_k\rVert$; arrows spring to unit length; labels become $\mathbf u_k$; faint teal unit cube on $\mathbf u_1, \mathbf u_2, \mathbf u_3$; values listed; slow orbit | captions "Divide each one by its length to make it a unit vector." / "They sit like the corner of a unit cube: an orthonormal basis." |
| 77–86 | Stage clears. $A$ with yellow, blue and pink columns and $Q = [\mathbf u_1\ \mathbf u_2\ \mathbf u_3]$ at the top; the three weight equations write in, each $\mathbf x_k$ using $\mathbf u_1$ to $\mathbf u_k$ | captions "Stack the $\mathbf x$'s into $A$ and the $\mathbf u$'s into $Q$." / "Each $\mathbf x_k$ uses only $\mathbf u_1$ through $\mathbf u_k$." |
| 86–91 | The six weights fly into $R$; the three zeros below the diagonal pop in orange | caption "Those weights fill an upper triangular $R$, so $A = QR$." |
| 91–96 | The symbols crossfade to the numbers of $R = Q^TA$ | caption "Since $Q^TQ = I$, you can compute $R = Q^TA$." |
| 96–103 | Takeaway card with origin pulse | end |
