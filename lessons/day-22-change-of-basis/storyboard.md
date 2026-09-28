# Day 22: Change of basis

The plane picks up Day 15's basis $\mathcal B$: green $\mathbf b_1 = (2, 1)$, red $\mathbf b_2 = (-1, 2)$, the
purple-gray grid, and yellow $\mathbf x = (3, 4)$ with $[\mathbf x]_{\mathcal B} = (2, 1)$. The second basis
$\mathcal C$ is pink $\mathbf c_1 = (1, 0)$ and blue $\mathbf c_2 = (-1, 1)$, drawn with a faint pink grid over the
purple-gray one. In $\mathcal C$, $\mathbf x = 7\mathbf c_1 + 4\mathbf c_2$. Entries of a $\mathcal B$-coordinate
vector are green and red; entries of a $\mathcal C$-coordinate vector are pink and blue. Columns of
$P_{\mathcal C \leftarrow \mathcal B}$ are green (from $\mathbf b_1$) and red (from $\mathbf b_2$).
$P_{\mathcal C \leftarrow \mathcal B} = \begin{bmatrix} 3 & 1 \\ 1 & 2 \end{bmatrix}$ and its inverse is
$\tfrac15\begin{bmatrix} 2 & -1 \\ -1 & 3 \end{bmatrix}$. The similarity section uses
$A = \begin{bmatrix} 1 & 2 \\ 1 & 0 \end{bmatrix}$, which doubles $\mathbf b_1$ and sends $\mathbf b_2$ to
$\mathbf b_1 - \mathbf b_2$, so $[T]_{\mathcal B} = \begin{bmatrix} 2 & 1 \\ 0 & -1 \end{bmatrix}$; images are teal.
A dark side panel on the right holds the math while the plane fills the left two thirds.

| t (s) | State | Trigger |
|---|---|---|
| 0–9 | Title card "Change of basis", "Day 22"; glowing origin; grid draws outward | start |
| 9–19 | Plane dims; green b₁, red b₂ and the purple-gray grid appear; yellow x grows; two green steps and one red step walk to its tip; $[\mathbf x]_{\mathcal B} = (2, 1)$ lands in the side panel | captions "Yesterday a matrix depended on the basis we picked." (while the B grid draws) / "Day 15 gave $\mathbf x$ an address in the basis $\mathcal B$." / "Two steps of $\mathbf b_1$ and one of $\mathbf b_2$ reach $\mathbf x$." |
| 19–28 | Pink c₁ and blue c₂ grow; the pink grid draws over the purple-gray one | captions "A second basis $\mathcal C$ lays another grid over the same plane." / "Today we translate an address from one basis to another." |
| 28–45 | **Centerpiece.** The walks fade and x shrinks to the origin. A tracker grows x back out; the B walk (2s·b₁, s·b₂) and the C walk (7s·c₁, 4s·c₂) stretch with it, and both address columns count up together from 0 to (2, 1) and (7, 4). x's tip gets an orange ring | captions "Grow $\mathbf x$ and read both addresses as it grows." / "In $\mathcal C$ it takes 7 steps of $\mathbf c_1$ and 4 of $\mathbf c_2$." / "The arrow stays put while each grid names it differently." |
| 45–66 | Walks fade; both address columns glow. b₁ is walked on the C grid (3 pink steps, 1 blue), then $\mathbf b_1 = 3\mathbf c_1 + \mathbf c_2$; its C column flies into column 1 of P. Same for b₂ = c₁ + 2c₂ into column 2 | captions "We want one matrix that turns $[\mathbf x]_{\mathcal B}$ into $[\mathbf x]_{\mathcal C}$." / "To translate, write each $\mathcal B$ vector in $\mathcal C$ coordinates." / "Those columns build the matrix $P_{\mathcal C \leftarrow \mathcal B}$." |
| 66–76 | $P\,[\mathbf x]_{\mathcal B} = 2\,(\text{col }1) + 1\,(\text{col }2) = [\mathbf x]_{\mathcal C}$ fills in; (7, 4) matches the C column above | caption "Since $\mathbf x = 2\mathbf b_1 + \mathbf b_2$, the same weights combine the columns." |
| 76–88 | Panel clears to two columns (2, 1) and (7, 4) joined by a top arrow $P_{\mathcal C\leftarrow\mathcal B}$ and a bottom arrow $P_{\mathcal B\leftarrow\mathcal C} = P^{-1}$; an orange dot runs over and back | captions "Read the subscript right to left, from $\mathcal B$ into $\mathcal C$." / "Its inverse translates back from $\mathcal C$ to $\mathcal B$." |
| 88–103 | Scrim. $[\,\mathbf c_1\ \mathbf c_2 \mid \mathbf b_1\ \mathbf b_2\,]$ with colored column names above; one row step $R_1 + R_2$ morphs it to $[\,I \mid P\,]$; the right block glows | captions "With real vectors, row reduce $[\,\mathbf c_1\ \mathbf c_2 \mid \mathbf b_1\ \mathbf b_2\,]$." / "One row reduction finds both columns of $P$ at once." / "The basis you translate into goes on the left." |
| 103–120 | Scrim lifts. C grid and x leave. The side panel shows A. b₁ springs to teal T(b₁) = 2b₁; b₂ swings to teal T(b₂) = (3, −1), walked as one green step and one backward red step; columns (2, 0) and (1, −1) drop into $[T]_{\mathcal B}$ | captions "Change of basis also rewrites the matrix of a map." / "$T$ doubles $\mathbf b_1$ and sends $\mathbf b_2$ to $\mathbf b_1 - \mathbf b_2$." / "In $\mathcal B$ coordinates, $T$ has a simpler matrix." |
| 120–138 | Scrim. The commuting square: $[\mathbf x]_{\mathcal B}$ up by P to x, across by A, down by $P^{-1}$ to $[T\mathbf x]_{\mathcal B}$; bottom edge $[T]_{\mathcal B}$. An orange dot runs the long way; the formula $[T]_{\mathcal B} = P^{-1}AP$ lights up right to left; the numbers check out below | captions "Go to standard coordinates, apply $A$, then come back." / "So $[T]_{\mathcal B} = P^{-1}AP$, and the two matrices are similar." / "Day 32 picks a basis that makes this matrix diagonal." |
| 138–143 | Takeaway card with origin pulse | end |
