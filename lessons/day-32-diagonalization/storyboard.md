# Day 32: Diagonalization

The video keeps Day 28's matrix $A = \begin{bmatrix} 3 & -2 \\ 1 & 0 \end{bmatrix}$ with its green and red columns and
its two eigen-lines in their Day 28 colors: yellow through $\mathbf v_1 = (2, 1)$ with $\lambda = 2$, and blue through
$\mathbf v_2 = (1, 1)$ with $\lambda = 1$. So $P = \begin{bmatrix} 2 & 1 \\ 1 & 1 \end{bmatrix}$ has a yellow first column
and a blue second column, $D = \begin{bmatrix} 2 & 0 \\ 0 & 1 \end{bmatrix}$ has orange diagonal entries, and
$P^{-1} = \begin{bmatrix} 1 & -1 \\ -1 & 2 \end{bmatrix}$ has integer entries because $\det P = 1$. The ordinary input is
the purple-gray $\mathbf u = (0, 1)$, and the orange ring marks $A\mathbf u = (-2, 0)$, the red column of $A$. The plane sits a
little right of and below centre, 1.4 scene units per step, so the thin eigen-grid cells stay readable and $\mathbf u$'s whole path
$(0, 1) \to (-1, 2) \to (-2, 2) \to (-2, 0)$ stays in frame and clear of the factor panel in the top right.

The moving grid is the purple-gray **eigen-grid**, the lines $a\mathbf v_1 + t\mathbf v_2$ and $t\mathbf v_1 + b\mathbf v_2$.
It is drawn as the image of the integer grid under a live matrix that starts at $P$, and each move left-multiplies it
along the straight path $(1 - s)I + sM$, so each of $P^{-1}$, $D$ and $P$ plays as one continuous motion. None of those
paths passes through a singular matrix.

| t (s) | State | Trigger |
|---|---|---|
| 0–9 | Title card "Diagonalization", "Day 32"; glowing origin; grid draws outward | start |
| 9–25 | $A$ panel top left in Day 28's colors. Yellow and blue eigen-lines draw, then $\mathbf v_1$ and $\mathbf v_2$ grow along them with labels, and the picture holds while today's question is posed. The plane dims and the purple-gray eigen-grid fades in over it, with one cell shaded | captions "Day 28's matrix $A$ keeps two lines through the origin." / "Yesterday's shear had one such line, but $A$ has two." / "Can two eigenvectors make $A$ as simple as a diagonal matrix?" / "Use its eigenvectors $\mathbf v_1$ and $\mathbf v_2$ as new axes." |
| 25–37 | The eigen-grid moves by $A$: every yellow step doubles and the shaded cell stretches along yellow; blue steps stay put. It springs back | captions "Let $A$ act on this eigen-grid." / "Every yellow step doubles and every blue step stays put." / "On this grid $A$ only stretches each axis." |
| 37–74 | **Centerpiece.** $A$ panel leaves; factor panel $A = PDP^{-1}$ lands top right and holds while its purpose is named. $\mathbf u$ grows, and the ring for $A\mathbf u$ lands with its label. An orange box sits on $P^{-1}$: the eigen-grid straightens onto the ordinary grid, $\mathbf v_1 \to \mathbf e_1$, $\mathbf v_2 \to \mathbf e_2$, and $\mathbf u$ rides to $(-1, 2)$ with a coordinate tag. Box moves to $D$: the grid stretches 2 across, 1 up, and $\mathbf u$ rides to $(-2, 2)$. Box moves to $P$: the grid swings back to the stretched eigen-grid, and $\mathbf u$ lands in the ring, which pulses | captions "This factorization will make powers of $A$ easy to compute." / "Take a vector $\mathbf u$ that $A$ turns, and mark $A\mathbf u$." / "Now do $A$ in three moves, starting from the right." / "$P^{-1}$ turns the eigen-grid into the ordinary grid." / "Now $\mathbf u$ sits at its eigen-coordinates $(-1, 2)$." / "$D$ stretches along the axes by 2 and by 1." / "$P$ turns the ordinary grid back into the eigen-grid." / "The three moves land exactly on $A\mathbf u$." |
| 74–90 | Scrim. $AP$ written column by column: $[A\mathbf v_1\ A\mathbf v_2] = [2\mathbf v_1\ 1\mathbf v_2] = [\mathbf v_1\ \mathbf v_2]\,D = PD$, with eigenvectors yellow and blue and eigenvalues orange. Then $A = PDP^{-1}$ lands large | captions "Here is why: look at $AP$ one column at a time." / "Each column is an eigenvector times its eigenvalue." / "$P$ has independent columns, so $P^{-1}$ exists." |
| 90–106 | Board: the definition of diagonalizable and the theorem. Two small planes: $A$ with its two eigen-lines and eigen-grid, and the shear $S$ from Day 31 with its single eigen-line while a test arrow gets knocked off its line. Then the distinct-eigenvalue test | captions "$A$ is \emph{diagonalizable} when $A = PDP^{-1}$ with $D$ diagonal." / "That works exactly when $A$ has $n$ independent eigenvectors." / "The shear from Day 31 has only one eigen-line." / "Distinct eigenvalues always give enough eigenvectors." |
| 106–125 | Board: $A^{10} = A\,A\,A\,A\,A\,A\,A\,A\,A\,A$ written out, then it fades and $A^2 = (PDP^{-1})(PDP^{-1})$; the middle $P^{-1}P$ glows and becomes $I$; then $PD^2P^{-1}$ and $A^k = PD^kP^{-1}$ with $D^k$ written out. Then $A^{10} = P\begin{bmatrix} 1024 & 0 \\ 0 & 1\end{bmatrix}P^{-1} = \begin{bmatrix} 2047 & -2046 \\ 1023 & -1022 \end{bmatrix}$ | captions "Computing $A^{10}$ directly takes nine matrix products." / "Squaring $A$ puts $P^{-1}P = I$ in the middle." / "So $A^k = PD^kP^{-1}$, and only $D$ takes the power." / "$A^{10}$ now takes two products instead of nine." / "Day 33 uses these powers to predict where $A^k\mathbf x$ heads." |
| 125–133 | Takeaway card with origin pulse | end |
