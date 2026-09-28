# Day 19: The invertible matrix theorem

The lesson opens on Day 7's matrices. $A = \begin{bmatrix}2&1\\1&1\end{bmatrix}$ keeps its green and red columns, and
$M = \begin{bmatrix}1&2\\2&4\end{bmatrix}$ is Day 7's flattening matrix. The pink test vector $\mathbf x = (2, -1)$ is
chosen so that $A\mathbf x = (3, 1)$ lands in the teal ring $\mathbf b = (3, 1)$ while $M\mathbf x = \mathbf 0$. Under
$M$ the grid falls onto the line through $(1, 2)$ and the ring at $\mathbf b$ is left off it. Orange marks only the
crushed point, pivots and the travelling light.

The centerpiece is a web of the 18 statements (Lay's (a) to (r)) on a scrim. The left block holds the statements that
say nothing is crushed (e, f, d, q, r from top to bottom), the right block the ones that say every target is reached
(h, i, g, n, o). The center column stacks the basis statement (m), the undo group (l, a, then j and k side by side) and
the pivot group (b, c, p). That order puts every "restates" link between neighbours, so the only long arrows are the
reasoning links of Lay's proof. A node is lit when its plate turns teal and its text turns teal, and it is dark when
its text drops to faint gray.

The matrices fed into the web are fresh: $B = \begin{bmatrix}2&1&0\\1&3&1\\0&1&2\end{bmatrix}$ (three pivots) and
$C = \begin{bmatrix}1&2&-1\\2&4&0\\3&6&1\end{bmatrix}$ (column 2 is twice column 1).

| t (s) | State | Trigger |
|---|---|---|
| 0–6 | Title card "The invertible matrix theorem", "Day 19" | start |
| 6–9 | Glowing origin, grid draws | after title |
| 9–16 | Panel lists six words from Days 12 to 18 (independent columns, columns span, $n$ pivots, $\operatorname{Nul}A = \{\mathbf 0\}$, rank $n$, $A^{-1}$ exists); each word pulses teal in turn | captions "Days 12 to 18 gave square matrices many new words.", "Do these all say the same thing about a square matrix?" |
| 16–19 | Panel swaps to $A$ with green and red columns; $\hat\imath$ and $\hat\jmath$ grow | caption "Day 7's matrix $A$ moves every point of the plane." |
| 19–24 | Pink $\mathbf x = (2, -1)$ grows; teal ring at $\mathbf b = (3, 1)$ | caption "Follow the pink $\mathbf x$ and the ring at $\mathbf b$." |
| 24–31 | Grid springs $I \to A$; $\mathbf x$ lands in the ring, which flashes | captions "$A$ sends $\mathbf x$ onto $\mathbf b$, not onto $\mathbf 0$.", "The grid still covers the plane, so every target is hit." |
| 31–39 | Grid returns home; panel swaps to $M$; grid collapses onto the line through $(1, 2)$; pink shrinks to nothing and the origin flashes orange | caption "Now try $M$, whose columns point along one line.", "$M$ crushes $\mathbf x$ all the way to $\mathbf 0$." |
| 39–44 | The ring at $\mathbf b$ is circled in orange; a dashed orange drop shows it sits off the line | caption "Everything lands on one line, so $\mathbf b$ is never reached." |
| 44–58 | Panel grows two rank bars: $A$ with two teal cells, $M$ with one teal cell and one empty dashed cell; readouts rank and nullity | captions "Two input directions go in, and each survives or is crushed.", "Rank plus nullity always equals $2$ for a $2\times 2$ matrix.", "So a square matrix that crushes nothing reaches everything." |
| 58–64 | Scrim. The 18 statement nodes appear block by block, left and right blocks with their names below | captions "For a square $n\times n$ matrix, Lay lists eighteen statements.", "Some say nothing is crushed, and others say every target is hit." |
| 64–100 | Arrows of the proof draw in stages: a→j, a→k, a⇔l; j→d; d→c→b; b→a; k→g; g→c; the neighbour links inside each block; o→p→r | one caption per stage (see scene.py) |
| 100–104 | Whole web settles | caption "So the eighteen are all true or all false together." |
| 104–122 | **Centerpiece, light.** A plate opens in the center; $B$ row reduces in two steps; orange boxes mark three pivots; $B$ shrinks into "n pivot positions", which lights; light travels along the arrows level by level until every node is teal | captions "So we can check one cheap statement and trust the rest.", "Row reduce $B$ only far enough to count its pivots.", "$B$ has three pivots. Watch that one fact travel.", "The light reaches every statement, so $B$ is invertible." |
| 122–142 | Web resets. $C$ opens in the center; columns 1 and 2 flash; $\mathbf c_2 = 2\mathbf c_1$ writes; $C$ shrinks into "columns are independent", which goes dark with an orange ring; darkness travels back along the arrows until every node is faint | captions "Here is $C$, whose second column is twice its first.", "Independence fails, and the failure spreads to every statement.", "So $C$ is singular, and no row reduction was needed." |
| 142–151 | A dashed preview node $\det A \ne 0$ fades in at the top right | captions "On Day 26, $\det A \neq 0$ joins the list.", "Day 29 uses this list to hunt for eigenvalues." while "$A$ is invertible" pulses orange |
| 151–160 | Takeaway card | end |
