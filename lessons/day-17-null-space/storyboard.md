# Day 17: Null space

Day 16 collected every output of a matrix into $\operatorname{Col}A$ and drew it teal. Today runs the question
backward and asks which inputs land on $\mathbf 0$. The colors carry over: outputs and $\operatorname{Col}$ stay
teal, a vector we ask a question about is yellow, and the null space gets pink, which no earlier lesson has given a
fixed job. Orange marks only the spots where things land.

The centerpiece matrix is the projection $P = \tfrac12\begin{bmatrix}1&1\\1&1\end{bmatrix}$ onto the diagonal
$x_2 = x_1$. It sends $\mathbf x$ to $\tfrac{x_1 + x_2}{2}(1, 1)$, so every point slides along the direction
$(1, -1)$ until it hits the diagonal. Its null space is the anti-diagonal $\operatorname{Span}\{(1, -1)\}$.

The plane fills the frame (origin at $(0.9, -0.25)$, 0.85 units per grid step). A lattice of integer dots covers
it, and every dot's position comes from one `ValueTracker` $s$: at $s$ the dot sits at $(1 - s)\mathbf x + sP\mathbf x$.
Running $s$ from 0 to 1 plays the projection, and running it back rewinds it, so every collapse is continuous.

The last section needs a matrix with more than one free variable, so it switches to
$A = \begin{bmatrix}1&-2&0&3\\2&-4&1&4\end{bmatrix}$ (a fresh example, not Lay's). One row operation reduces it to
$\begin{bmatrix}1&-2&0&3\\0&0&1&-2\end{bmatrix}$, so $x_2, x_4$ are free and
$\operatorname{Nul}A = \operatorname{Span}\{(2, 1, 0, 0), (-3, 0, 2, 1)\}$. The first basis vector is yellow and the
second blue.

| t (s) | State | Trigger |
|---|---|---|
| 0–6 | Title card "Null space", "Day 17" | start |
| 6–9 | Glowing origin; grid draws outward | after title |
| 9–17 | $P$ writes in a panel top left; the lattice of gray dots ripples out from the origin | captions "Yesterday we collected every output of a matrix.", "Today we ask which inputs land on $\mathbf 0$." |
| 17–25 | $s$ springs 0 → 1: every dot slides along $(1, -1)$ onto the diagonal; the teal line $\operatorname{Col}P$ draws | caption "This $P$ projects the plane onto the diagonal." |
| 25–30 | $s$ rewinds to 0; the anti-diagonal dots turn pink and a pink line draws through them | caption "Now follow the dots on this pink line." |
| 30–40 | **Centerpiece:** $s$ springs 0 → 1 again; the pink line shrinks into the origin with its dots; an orange flash and ring at the origin | caption "The whole pink line collapses onto the origin." |
| 40–48 | $s$ rewinds; gray dots dim; the label $\operatorname{Nul}P = \operatorname{Span}\{(1, -1)\}$ appears by the line; the definition writes in the panel | captions "That line is the \emph{null space} of $P$.", "It holds every input that $P$ sends to $\mathbf 0$." |
| 48–58 | Pink arrow $(1, -1)$ grows; the panel shows $P(1, -1) = (0, 0)$; a yellow arrow $(2, 1)$ slides to $(1.5, 1.5)$ and the panel shows it | captions "To test one vector, just multiply by $P$.", "$(2, 1)$ lands at $(1.5, 1.5)$, so it is not in $\operatorname{Nul}P$." |
| 58–76 | Scrim; the three subspace checks write one per caption, each with a teal tick | captions "The null space of any matrix is a subspace.", "It contains $\mathbf 0$, because $A\mathbf 0 = \mathbf 0$.", "Sums stay in, because $A(\mathbf u + \mathbf v) = A\mathbf u + A\mathbf v$.", "Multiples stay in, because $A(c\mathbf u) = cA\mathbf u$." |
| 76–86 | Scrim lifts; an orange ring marks $\mathbf b = (2, 2)$ on the teal line; the dots with $x_1 + x_2 = 4$ turn yellow and a yellow line draws | caption "Now ask which inputs land on $\mathbf b = (2, 2)$." |
| 86–92 | $s$ springs 0 → 1: yellow dots stack on $\mathbf b$, pink dots on $\mathbf 0$; flash at $\mathbf b$; rewind | caption "Every yellow dot lands on $\mathbf b$." |
| 92–104 | Yellow arrow $\mathbf p = (2, 2)$; a copy of the pink line slides along $\mathbf p$ onto the yellow line; a point $\mathbf p + t(1, -1)$ rides the yellow line with a dashed pink arrow from $\mathbf p$ | captions "The solutions are the null space, shifted by $\mathbf p$.", "Each solution is $\mathbf p$ plus a vector in $\operatorname{Nul}P$." |
| 104–110 | $\{\mathbf x : P\mathbf x = \mathbf b\} = \mathbf p + \operatorname{Nul}P$ in the panel; ring at the origin, which the yellow line misses | caption "The shifted line misses $\mathbf 0$, so it is not a subspace." |
| 110–120 | Scrim; $A$ writes; $R_2 \leftarrow R_2 - 2R_1$ morphs it to reduced form | captions "Bigger matrices need row reduction to find $\operatorname{Nul}A$.", "Row reduce $A$. The zero column of $[A\ \mathbf 0]$ never changes." |
| 120–128 | Orange frames on pivot columns 1 and 3; the free columns 2 and 4 get tags $x_2$, $x_4$; the two solved equations write | captions "Columns 2 and 4 have no pivot, so $x_2$ and $x_4$ are free.", "Solve for $x_1$ and $x_3$ in terms of the free ones." |
| 128–140 | $\mathbf x$ writes as a column and the solved right sides fly into it glyph by glyph; then it splits into $x_2\mathbf u + x_4\mathbf v$ with $\mathbf u$ yellow and $\mathbf v$ blue | captions "Write $\mathbf x$ with only the free variables left.", "Split by free variable: one vector for each." |
| 140–150 | Orange frames on rows 2 and 4 of $\mathbf u$ and $\mathbf v$, which read $1, 0$ and $0, 1$ | captions "Rows 2 and 4 of $\mathbf x$ are just $x_2$ and $x_4$.", "So only zero weights give $\mathbf 0$, and $\{\mathbf u, \mathbf v\}$ is a basis." |
| 146–156 | Tags $\operatorname{Nul}A \subseteq \mathbb R^4$ and $\operatorname{Col}A \subseteq \mathbb R^2$ | caption "$A$ has 4 columns, so $\operatorname{Nul}A$ lives in $\mathbb R^4$." |
| 142–151 | Takeaway card (the final render runs 151.5 s, so every row above sits a few seconds earlier than planned) | end |
