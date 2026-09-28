# Day 23: Kernel

Day 17 found $\operatorname{Nul}A$, the inputs a matrix sends to $\mathbf 0$, and drew it pink. Day 20 made the
derivative a linear map and used the evaluation map $T(\mathbf p) = (\mathbf p(0), \mathbf p(1))$ in its practice.
Today asks Day 17's question of any linear map, so the kernel keeps Day 17's pink. The first input $\mathbf u$ is
yellow, the second input $\mathbf v$ is blue, outputs are teal, and orange marks only landing spots and pins.

The centerpiece uses $T : \mathbb P_2 \to \mathbb R^2$, $T(\mathbf p) = (\mathbf p(0), \mathbf p(1))$. A large graph
panel on the left holds the inputs, with two dashed pins at $t = 0$ (green, the first output entry) and $t = 1$
(red, the second). The codomain $\mathbb R^2$ is a small plane on the right. $T$ reads a curve's heights at the two
pins, and those heights fly across as the two coordinates of the output. $\mathbf u = t^2$ and $\mathbf v = t$
both pass through $(0, 0)$ and $(1, 1)$, so both land on $\mathbf b = (0, 1)$. Their difference $t^2 - t$ passes
through both pins at height 0, so it lands on $\mathbf 0$. Every curve $\mathbf u + c(t^2 - t)$ stays pinned and
lands on $\mathbf b$; $c = -1$ gives $\mathbf v$ itself.

A third pin at $t = -1$ then reads $t^2 - t$ as 2, and the kernel of the three-pin map shrinks to $\{\mathbf 0\}$.

| t (s) | State | Trigger |
|---|---|---|
| 0–8 | Title card "Kernel", "Day 23"; glowing origin; grid draws outward | start |
| 8–18 | Day 17's $P$ in a top-left panel; pink line $\operatorname{Nul}P$ with pink dots; the dots and line collapse into the origin, orange flash | captions "On Day 17, this $P$ sent a whole pink line to $\mathbf 0$.", "That line was $\operatorname{Nul}P$." |
| 18–30 | Scrim. Definition card: $\ker T = \{\mathbf u \in V : T(\mathbf u) = \mathbf 0\}$; then "for $T(\mathbf x) = A\mathbf x$, $\ker T = \operatorname{Nul}A$" | captions "Any linear map $T : V \to W$ can ask the same question.", "Its \emph{kernel} is everything $T$ sends to $\mathbf 0$.", "The kernel is a set of inputs, so it lives in $V$." |
| 30–46 | Two graph panels joined by an arrow $D$. Four pink constants draw on the left; copies slide right and flatten onto the teal zero polynomial; orange flash along it | captions "Try the derivative $D$ on $\mathbb P_3$.", "Every constant flattens to the zero polynomial.", "So $\ker D$ is the constants, $\operatorname{Span}\{1\}$.", "That is why every antiderivative carries a $+\,C$." |
| 46–62 | Scrim. "$\ker T$ is a subspace of $V$" and three lines, one per caption, each ending on an orange-marked $\mathbf 0$ | captions "The kernel is always a subspace.", "It holds $\mathbf 0$, since $T(\mathbf 0) = \mathbf 0$.", "Sums of kernel vectors stay in the kernel.", "Multiples stay in too, by linearity." |
| 62–70 | Graph panel with the green and red pins, the $\mathbb R^2$ plane, arrow $T$, header $T(\mathbf p) = (\mathbf p(0), \mathbf p(1))$ | caption "Now let $T$ read a curve's height at two pins." |
| 70–80 | Yellow $\mathbf u = t^2$ draws; its pin dots fly to the axes of $\mathbb R^2$; the teal arrow to $\mathbf b = (0, 1)$ grows | caption "$\mathbf u = t^2$ lands on $\mathbf b = (0, 1)$." |
| 80–90 | Blue $\mathbf v = t$ draws through the same pin dots; a second teal arrow grows onto $\mathbf b$; orange ring | captions "$\mathbf v = t$ is a different input with the same output.", "So this $T$ is not one-to-one." |
| 90–102 | **Centerpiece.** Copies of $\mathbf u$ and $\mathbf v$ fade into pink $t^2 - t$; its pin dots sit at height 0; a pink dot lands on the origin with an orange flash; readout $T(\mathbf u - \mathbf v) = \mathbf b - \mathbf b = \mathbf 0$ | captions "Subtract them: $\mathbf u - \mathbf v = t^2 - t$.", "Both pins read 0, so $\mathbf u - \mathbf v$ is in $\ker T$.", "Linearity forces it: $T(\mathbf u - \mathbf v) = \mathbf b - \mathbf b = \mathbf 0$." |
| 102–112 | $c(t^2 - t)$ springs through several values leaving pink ghosts, all through the two zero pins; the output stays on $\mathbf 0$ | caption "Every multiple of $t^2 - t$ lands on $\mathbf 0$ too.", "So $\ker T = \operatorname{Span}\{t^2 - t\}$." |
| 112–124 | Pink ghosts fade. $\mathbf u + c(t^2 - t)$ springs through $c = 1, -1, -\tfrac12$, leaving yellow ghosts pinned at the same two points; at $c = -1$ it lies on $\mathbf v$; the teal arrow never moves | captions "Add any kernel vector to $\mathbf u$.", "Every curve stays pinned, so every output is $\mathbf b$." |
| 124–138 | Scrim. Theorem card: one-to-one exactly when $\ker T = \{\mathbf 0\}$, with the two reasons revealed one at a time | captions "Two inputs with one output differ by a kernel vector.", "A nonzero kernel vector gives two inputs one output.", "So $T$ is one-to-one exactly when $\ker T = \{\mathbf 0\}$." |
| 138–152 | Graph panel with pink $t^2 - t$. A third pin at $t = -1$ reads 2 (orange dashed height); header becomes three entries; $c$ shrinks to 0 and the curve flattens onto the axis as the reading drops to 0 | captions "Add a third pin at $t = -1$.", "There $t^2 - t$ reads 2, not 0.", "A nonzero quadratic can't be zero at three places.", "So this new $T$ has $\ker T = \{\mathbf 0\}$ and is one-to-one." |
| 152–160 | Takeaway card with origin pulse (the final render runs 157 s, so late rows land a few seconds earlier) | end |
