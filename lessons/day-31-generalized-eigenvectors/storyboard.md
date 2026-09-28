# Day 31: Generalized eigenvectors

The whole video uses Day 5's shear $S = \begin{bmatrix} 1 & 1 \\ 0 & 1 \end{bmatrix}$, with its columns green (where
$\mathbf e_1$ lands) and red (where $\mathbf e_2$ lands). The plane is centred at the middle of the frame with 1.3 scene
units per grid step. A square patch of the grid, $-2 \le x, y \le 2$, carries the motion: it is the image of that
square under the current matrix, so it shears into a parallelogram under $S$, squashes onto a segment of the
eigenline under $S - I$, and shrinks to the origin under $(S - I)^2$. The eigenline (the $x$-axis) is yellow, as the
first eigen-direction was on Day 28. The chain's top vector $\mathbf v_2 = (1, 2)$ is blue, $S\mathbf v_2$ is teal,
and the push $(S - I)\mathbf v_2$ is pink, the same pink Day 28 used for the gap $(A - \lambda I)\mathbf x$. When the
push slides to the origin it turns yellow and becomes $\mathbf v_1 = (2, 0)$. Orange is only for tip marks and the
ring at the origin.

| t (s) | State | Trigger |
|---|---|---|
| 0–9 | Title card "Generalized eigenvectors", "Day 31"; glowing origin; grid draws outward | start |
| 9–14 | $S$ panel fades in top left, green and red columns. The plane dims and the bright square patch fades in | caption "Here is the shear $S$ from Day 5." |
| 14–24 | Twelve purple-gray arrows fan out from the origin with faint dashed lines. The patch shears slowly to $S$; every arrow tips off its line except the two horizontal ones | captions "Draw twelve directions, then let $S$ act." / "Every arrow tips over except the horizontal pair." |
| 24–30 | The $x$-axis lights up yellow, the horizontal arrows turn yellow with orange tips, and $\lambda = 1$ lands on the line. The fan fades and the patch springs back to $I$ | caption "So $S$ has just one line of eigenvectors, for $\lambda = 1$." |
| 30–50 | Scrim. $\det(S - \lambda I) = (1 - \lambda)^2$ with the exponent glowing; "algebraic multiplicity 2". Then $S - I = \begin{bmatrix} 0 & 1 \\ 0 & 0 \end{bmatrix}$, $\operatorname{Nul}(S - I) = \operatorname{Span}\{\mathbf e_1\}$, "geometric multiplicity 1". The two counts sit side by side, $1 < 2$, and the word defective appears | captions "The characteristic polynomial counts $\lambda = 1$ twice." / "But $S - I$ has rank 1, so its null space is one line." / "One eigen-direction short of two, $S$ is called \emph{defective}." |
| 50–58 | Scrim lifts. Blue $\mathbf v_2 = (1, 2)$ grows, with its dashed line | caption "Take $\mathbf v_2 = (1, 2)$, which sits off the eigenline." |
| 58–64 | Patch shears to $S$; a teal copy rides to $S\mathbf v_2 = (3, 2)$ | caption "The shear carries $\mathbf v_2$ to $S\mathbf v_2 = (3, 2)$." |
| 64–70 | Pink arrow grows from the tip of $\mathbf v_2$ to the tip of $S\mathbf v_2$, labelled $(S - I)\mathbf v_2$ | caption "The push between them is $(S - I)\mathbf v_2 = S\mathbf v_2 - \mathbf v_2$." |
| 70–78 | **Centerpiece, part 1.** The pink push slides down to the origin, lands on the eigenline and turns yellow as $\mathbf v_1 = (2, 0)$; an orange mark lands on its tip. Top right, the chain label starts: $\mathbf v_2 \to \mathbf v_1$ | caption "Slid to the origin, the push lies on the eigenline." |
| 78–84 | Teal and pink leave; patch springs back to $I$ | caption "So $\mathbf v_1 = (S - I)\mathbf v_2$ is an eigenvector of $S$." |
| 84–92 | **Centerpiece, part 2.** The patch moves to $S - I$ and squashes flat onto the eigenline; the blue $\mathbf v_2$ rides down onto $\mathbf v_1$ | caption "Apply $S - I$ to the patch, and it squashes onto the eigenline." |
| 92–100 | The patch moves by $S - I$ again and shrinks to the origin; $\mathbf v_1$ shrinks with it; orange ring at the origin; the chain label finishes $\mathbf v_2 \to \mathbf v_1 \to \mathbf 0$ | caption "A second push sends the whole line to $\mathbf 0$." |
| 100–112 | Scrim. $(S - I)\mathbf v_2 \ne \mathbf 0$ but $(S - I)^2\mathbf v_2 = \mathbf 0$; then the general rule $(A - \lambda I)^k\mathbf v = \mathbf 0$ | captions "$\mathbf v_2$ needs two pushes, so it is a \emph{generalized eigenvector}." / "In general, $(A - \lambda I)^k\mathbf v = \mathbf 0$ for some $k$." |
| 112–122 | The chain rewrites as $A\mathbf v_1 = \lambda\mathbf v_1$ and $A\mathbf v_2 = \lambda\mathbf v_2 + \mathbf v_1$ | caption "Read the chain as two equations about $A$." |
| 122–134 | $J = \begin{bmatrix} \lambda & 1 \\ 0 & \lambda \end{bmatrix}$ with its first column yellow and second blue; the entries fly in from the two equations; the 1 glows | captions "In the basis $\mathbf v_1, \mathbf v_2$, they become the columns of $J$." / "The 1 above the diagonal records the push onto $\mathbf v_1$." |
| 134–142 | A $3 \times 3$ block matrix $\begin{bmatrix} 1 & 0 & 0 \\ 0 & -2 & 1 \\ 0 & 0 & -2 \end{bmatrix}$ with its two blocks outlined | caption "Stacking such blocks along the diagonal gives the \emph{Jordan form}." |
| 142–150 | Takeaway card with origin pulse | end |
