# Day 15: Coordinates and dimension

The plane section picks up Day 14's idea of a skewed grid. The basis vectors wear the basis colors from Day 1:
b₁ = (2, 1) is green and b₂ = (−1, 2) is red, the point x = (3, 4) is yellow, and the extra vector w is blue. The
basis grid is drawn in muted purple-gray so it reads as scaffolding under the arrows. The centerpiece reuses Day 10's
split screen (graph on the left, coefficient space with axes 1, t, t² on the right), with p(t) = 2 − t + 3t² in
yellow, q(t) = 1 + 4t − t² in blue and their sum in teal. A horizontal arrow between the formulas and the columns is
the coordinate map, and it turns around when a column is translated back into a polynomial.

| t (s) | State | Trigger |
|---|---|---|
| 0–6 | Title card "Coordinates and dimension", "Day 15" | start |
| 6–9 | Glowing origin, grid draws outward | after title |
| 9–17 | Green b₁ and red b₂ grow; the plane dims and the purple-gray basis grid fades in | captions "A basis gives every vector in the plane one address." / "Here $\mathbf b_1$ and $\mathbf b_2$ make a basis $\mathcal B$." |
| 17–26 | Yellow x = (3, 4) grows. Two green copies of b₁ spring tip to tail, then a red b₂ lands on x's tip | caption "Reach $\mathbf x$ with 2 steps of $\mathbf b_1$ and 1 of $\mathbf b_2$." |
| 26–31 | The column [x]_B = (2, 1) appears in the right panel with a green 2 and a red 1 | caption "Those weights form the coordinate vector $[\mathbf x]_{\mathcal B}$." |
| 31–38 | P_B [x]_B = x appears; its green and red columns flash with the arrows | caption "The matrix $P_{\mathcal B}$ turns coordinates back into $\mathbf x$." |
| 38–46 | The augmented matrix [b₁ b₂ \| x] morphs into its reduced form; the last column 2, 1 glows | caption "To find the coordinates, row reduce $[\,\mathbf b_1\ \mathbf b_2 \mid \mathbf x\,]$." |
| 46–50 | Plane clears; graph axes draw on the left and coefficient axes on the right | caption "Polynomials get coordinates too, from the basis $1, t, t^2$." |
| 50–55 | p's formula writes, its curve sweeps in | caption "Here is a polynomial in $\mathbb P_2$." |
| 55–63 | **Centerpiece, part 1:** the coordinate-map arrow grows left to right; the coefficients 2, −1, 3 lift off the formula and drop into a yellow column; the yellow arrow grows to (2, −1, 3) | captions "Its coordinates are its three coefficients, stacked in a column." / "That column is also an arrow in $\mathbb R^3$." |
| 63–71 | **Centerpiece, part 2:** a blue column (1, 4, −1) appears; the map arrow turns around; its entries fly left into q's formula and the blue curve sweeps in; the blue arrow grows | caption "Every column of three numbers turns back into one polynomial." |
| 71–80 | Teal sum curve sweeps in; the blue arrow slides tip to tail and the teal arrow grows to (3, 3, 2); the column sum completes | caption "Adding polynomials adds their columns and their arrows too." |
| 80–90 | The formulas collapse into ℙ₂, the columns into ℝ³, and the map arrow becomes a double arrow | captions "The map is one-to-one, onto $\mathbb R^3$, and linear." / "A map like that is called an isomorphism." |
| 90–97 | Plane returns with b₁, b₂ and the basis grid | caption "How many vectors can a basis of the plane hold?" |
| 97–106 | Blue w = (3, −1) grows; a green b₁ and a reversed red b₂ walk to its tip | captions "A third vector $\mathbf w$ already has an address on the grid." / "So $\mathbf w = \mathbf b_1 - \mathbf b_2$, and the three are dependent." |
| 106–112 | w and b₂ fade; the grid collapses to the one purple-gray line through b₁ | caption "One vector alone spans only a line, not the plane." |
| 112–118 | A new basis c₁ = (1, 1), c₂ = (−1, 1) grows with its own grid | caption "Every basis of the plane has exactly two vectors." |
| 118–126 | Plane clears; a three-row table of spaces, bases and dimensions fills in one row at a time | captions "That shared count is the dimension of the space." / "$\mathbb P_2$ has dimension 3 because $1, t, t^2$ is a basis." |
| 126–146 | Coefficient axes for ℝ³; the origin, a line, a plane, then a lattice filling space, each with its key-value row on the right | captions "The origin alone has dimension 0." / "A line through the origin has dimension 1." / "A plane through the origin has dimension 2." / "Only $\mathbb R^3$ itself has dimension 3." |
| 146–154 | Takeaway card with origin pulse | end |
