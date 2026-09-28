# Day 33: Diagonalizing a linear transformation

The video reuses Day 22's matrix $A = \begin{bmatrix} 1 & 2 \\ 1 & 0 \end{bmatrix}$, whose columns are green (where
$\mathbf e_1$ lands) and red (where $\mathbf e_2$ lands). On Day 22 the basis $\{(2, 1), (-1, 2)\}$ made it triangular.
Its eigenvectors keep Day 28's eigen-colors: yellow $\mathbf v_1 = (2, 1)$ with $\lambda = 2$ and blue
$\mathbf v_2 = (-1, 1)$ with $\lambda = -1$. They form the basis $\mathcal B$, with
$P = \begin{bmatrix} 2 & -1 \\ 1 & 1 \end{bmatrix}$, $P^{-1} = \tfrac13\begin{bmatrix} 1 & 1 \\ -1 & 2 \end{bmatrix}$ and
$D = \begin{bmatrix} 2 & 0 \\ 0 & -1 \end{bmatrix}$. Entries of a $\mathcal B$-coordinate vector are yellow and blue.
The tracked vector is $\mathbf x = \mathbf v_1 + \mathbf v_2 = (1, 2)$, and $A\mathbf x = (5, 1) = 2\mathbf v_1 - \mathbf v_2$
in teal.

The centerpiece splits the frame into two copies of the same plane. The left copy carries the standard square grid
and the right copy carries the purple-gray eigen-grid of $\mathcal B$. Each side keeps a faint copy of its grid in
place while a bright copy moves along $(1 - s)I + sA$, so every point slides straight to its image. On the left the
moved lines land at new angles. On the right every moved line lands on an old grid line: the $\mathbf v_1$ direction
doubles, and the $\mathbf v_2$ direction shrinks through the origin and comes out flipped.

| t (s) | State | Trigger |
|---|---|---|
| 0–7 | Title card "Diagonalizing a linear transformation", "Day 33"; glowing origin | start |
| 7–19 | Left half: faint square grid, bright copy, green $\mathbf e_1$, red $\mathbf e_2$, and $A$ in a top plate. Right half: purple-gray eigen-grid with yellow and blue eigen-axes, yellow $\mathbf v_1$, blue $\mathbf v_2$, and $\mathcal B = \{\mathbf v_1, \mathbf v_2\}$ in a top plate | captions "Here is Day 22's matrix $A$ on the standard grid." / "Its eigenvectors make a basis $\mathcal B$ with its own grid." |
| 19–24 | Yellow $\mathbf x = (1, 2)$ grows on both sides. On the right a blue step from the tip of $\mathbf v_1$ walks to it. Readouts: $\mathbf x = (1, 2)$ on the left, $[\mathbf x]_{\mathcal B} = (1, 1)$ on the right | caption "Track one vector $\mathbf x$ in both coordinate systems." |
| 24–40 | **Centerpiece.** $A$ acts on both halves at once. Left: the bright grid slants off the faint one; $\mathbf e_1 \to (1, 1)$, $\mathbf e_2 \to (2, 0)$. Right: moved lines land on old lines; $\mathbf v_1$ doubles and $\mathbf v_2$ flips. A teal copy of $\mathbf x$ rides to $A\mathbf x$ on both sides. Readouts complete: $(1, 2) \mapsto (5, 1)$ and $(1, 1) \mapsto (2, -1)$; step dots count two yellow steps and one backward blue step | captions "Now let $A$ act on both pictures at once." / "On the standard grid, every cell slants and turns." / "On the eigen-grid, lines slide onto lines and cells only stretch." / "In $\mathcal B$-coordinates, $A$ doubles the first entry and flips the second." |
| 40–52 | Read off $[T]_{\mathcal B}$: column $(2, 0)$ appears by $A\mathbf v_1$ and column $(0, -1)$ by $A\mathbf v_2$; both fly into the right plate, which becomes $[T]_{\mathcal B}$. The two zeros turn orange with a flash | captions "Column $j$ of $[T]_{\mathcal B}$ is $[A\mathbf v_j]_{\mathcal B}$, as on Day 21." / "Eigenvectors only stretch, so every entry off the diagonal is 0." |
| 52–63 | Scrim. Commuting square: $\mathbf x \xrightarrow{A} A\mathbf x$ on top, $[\mathbf x]_{\mathcal B} \xrightarrow{D} [A\mathbf x]_{\mathcal B}$ below, $P$ up the left, $P^{-1}$ down the right. The long way glows orange edge by edge, the bottom edge turns teal, then $P^{-1}AP = D$ checks out with numbers | captions "Up by $P$, across by $A$, down by $P^{-1}$: the same map as $D$." / "So an eigenvector basis turns $A$ into the diagonal matrix $D$." |
| 63–77 | Three small planes of the same map in three bases: standard ($A$), Day 22's basis $\mathcal C = \{(2, 1), (-1, 2)\}$ ($\begin{bmatrix} 2 & 1 \\ 0 & -1 \end{bmatrix}$), and $\mathcal B$ ($D$). All three grids move with $A$ together. "tr = 1, det = −2, λ = 2, −1" appears under all three; an orange outline lands on $D$ | captions "Every basis gives its own matrix for the same map." / "These matrices are all similar, so they share trace and determinant." / "Only the eigenbasis makes the matrix diagonal." |
| 77–94 | Powers. One large eigen-grid. $\mathbf x_0 = \tfrac14\mathbf v_1 + \mathbf v_2$; each step hops the teal dot to $\mathbf x_{k+1}$, leaving a labelled ghost and a dashed segment, and the zigzag crosses the $\mathbf v_1$ line. Side plate lists $\mathbf x_0$ to $\mathbf x_4$ in $\mathcal B$ (yellow coefficient doubles, blue sign flips), then $A^k = PD^kP^{-1}$. The yellow line through $\mathbf v_1$ draws last | captions "Powers of $A$ are where the eigenbasis pays off." / "Each step doubles the $\mathbf v_1$ part and flips the $\mathbf v_2$ part." / "So $A^k\mathbf x_0 = \tfrac14\,2^k\,\mathbf v_1 + (-1)^k\,\mathbf v_2$, no matrix products." / "In the long run the arrow lines up with $\mathbf v_1$." |
| 94–101 | Takeaway card with origin pulse | end |
