# Day 27: Determinant properties and Cramer's rule

Day 25 read $\det[\,\mathbf a_1\ \mathbf a_2\,]$ as the signed area of the parallelogram of the columns, and Day 26
computed determinants and listed the row-operation rules. Today explains why those rules hold and what follows.
Colors keep their meaning: the fixed first column $\mathbf a_1$ is green, the moving second column $\mathbf x$ is
yellow (a second choice $\mathbf v$ is blue and the sum $\mathbf u + \mathbf v$ teal). A parallelogram is yellow when
its orientation is positive and pink when it flips. Heights are orange marks. In the centerpiece the unit square is
yellow, its image under $B$ stays yellow, and its image under $AB$ is teal. Cramer's rule reuses Day 15's basis:
green $\mathbf a_1 = (2, 1)$, red $\mathbf a_2 = (-1, 2)$ and yellow $\mathbf b = (3, 4) = 2\mathbf a_1 + \mathbf a_2$.
The parallelepiped has green, red and pink edges and a teal body.

Matrices: $B = \begin{bmatrix} 1 & 1 \\ 0 & 2 \end{bmatrix}$ ($\det 2$),
$A = \begin{bmatrix} 2 & 1 \\ -1 & 1 \end{bmatrix}$ ($\det 3$), $AB = \begin{bmatrix} 2 & 4 \\ -1 & 1 \end{bmatrix}$
($\det 6$). Their images are wide and flat, so the centerpiece fills the left of the frame at a large scale. Cramer: $A = \begin{bmatrix} 2 & -1 \\ 1 & 2 \end{bmatrix}$, $\mathbf b = (3, 4)$, $\det A = 5$,
$\det A_1(\mathbf b) = 10$, $\det A_2(\mathbf b) = 5$, $\mathbf x = (2, 1)$. Box: columns $(3,0,0)$, $(0,2,0)$,
$(0,0,2)$, sheared to $(3,0,0)$, $(1,2,0)$, $(1,1,2)$, volume 12 throughout.

| t (s) | State | Trigger |
|---|---|---|
| 0–9 | Title card "Determinant properties and Cramer's rule", "Day 27"; glowing origin; grid draws outward | start |
| 9–22 | Green $\mathbf a_1 = (3, 0)$ and yellow $\mathbf x = (1, 1)$ grow; their parallelogram fills yellow; the panel reads $\det[\mathbf a_1\ \mathbf x] = 3$; the readout pulses orange on the forward pointer | captions "Day 26 listed the determinant's rules without saying why." / "The determinant is the signed area of the columns' parallelogram." / "Today we find the two properties behind every rule." / "Day 29's search for eigenvalues is built on these rules." |
| 22–26 | An orange dashed height drops from x's tip to the base; the panel reads $= 3h$ | caption "With $\mathbf a_1$ fixed as the base, only the height of $\mathbf x$ matters." |
| 26–30 | x springs to 2x; height and readout double to 6; x springs back | caption "Doubling $\mathbf x$ doubles the height, so the determinant doubles." |
| 30–42 | x leaves; yellow u = (1, 1) and blue v = (−2, 2) with their parallelograms; height bars 1 and 2 stand at the right; the blue bar lifts onto the yellow one; teal u + v and its parallelogram arrive with a teal bar of height 3 beside the stack; panel $9 = 3 + 6$ | captions "Now take two choices, $\mathbf u$ and $\mathbf v$." / "Their heights stack, so their determinants add." |
| 42–50 | x returns and dips below the base; the fill turns pink and the readout goes negative | caption "Below the base the height is negative, and so is the area." |
| 50–56 | Panel shows the two linearity rules | caption "So det is linear in each column while the others stay fixed." |
| 56–60 | An orange arc turns from $\mathbf a_1$ to $\mathbf x$; the panel's columns swap into $\det[\mathbf x\ \mathbf a_1] = -3$; the arc reverses and the fill turns pink | caption "Swap the two columns and the sign flips." |
| 60–68 | x slides onto a1; the parallelogram flattens; panel $\det[\mathbf a\ \mathbf a] = -\det[\mathbf a\ \mathbf a] = 0$ | caption "Equal columns give zero: the swap changes nothing, yet flips the sign." |
| 68–82 | x returns to (1, 1); a dashed track parallel to a1 appears; x slides along it to (4, 1) and (−2, 1); height and readout stay at 3; panel shows the one-line proof | captions "Adding a multiple of $\mathbf a_1$ slides $\mathbf x$ parallel to the base." / "The height never changes, so the determinant stays the same." / "Rows obey the same rules, because $\det A^T = \det A$." |
| 82–86 | Stage clears. New large plane with a blue moving grid. Yellow unit square, panel counter "area 1.0" | caption "Here is why $\det(AB) = \det A \det B$." |
| 86–92 | B plays on the grid; the square becomes a yellow parallelogram; counter climbs to 2; $\det B = 2$ appears | caption "First $B$ stretches the square into area $\det B = 2$." |
| 92–98 | **Centerpiece.** A dashed outline keeps B's shape; A plays; the parallelogram turns teal and the counter climbs to 6; $\det A = 3$ appears | caption "Then $A$ multiplies every area by $\det A = 3$, this one too." |
| 98–111 | The grid springs back to the plain grid; AB plays in one step and lands exactly on the teal outline, which flashes; panel $\det(AB) = \det A\,\det B$, $6 = 3 \cdot 2$ | captions "The single map $AB$ lands on the very same shape." / "Areas multiply, so the determinants multiply." / "Day 30 uses this rule to show similar matrices share eigenvalues." |
| 111–118 | Stage clears. Green a₁, red a₂, yellow b on a new plane; panel shows $A\mathbf x = \mathbf b$ with $\det A = 5$; parallelogram of a₁ and a₂ fills yellow | caption "Cramer's rule aims to give each unknown as a ratio of determinants." |
| 118–130 | The first column stretches to 2a₁ (area 10) and then shears along a₂ until its tip reaches b; the area stays 10; b slides into column 1 to form $A_1(\mathbf b)$, and $x_1 = 10/5 = 2$ | captions "Since $\mathbf b = 2\mathbf a_1 + \mathbf a_2$, stretch $\mathbf a_1$ by 2." / "Adding $\mathbf a_2$ is a shear, so the area stays 10." / "So $\det A_1(\mathbf b) = x_1 \det A$, which gives $x_1$." |
| 130–141 | $A_2(\mathbf b)$ and $x_2 = 5/5 = 1$; the general rule $x_i = \det A_i(\mathbf b)/\det A$ | caption "Put $\mathbf b$ in column $i$ and divide by $\det A$." |
| 141–153 | Scrim. $A^{-1} = \frac{1}{\det A}\operatorname{adj}A$; the 2×2 cofactor matrix flips across its diagonal into $\operatorname{adj}A$, which is Day 7's formula | captions "Solving for each column of $A^{-1}$ gives the adjugate formula." / "The adjugate is the matrix of cofactors, transposed." |
| 153–172 | Scrim lifts onto a 3D floor. A 3 × 2 × 2 box grows from green, red and pink edges; the panel shows its diagonal matrix and volume 12; the top face slides, then the side face slides, while the view orbits; matrix morphs column by column, volume stays 12 | captions "Three columns in $\mathbb R^3$ build a box called a parallelepiped." / "Column replacement slides a face without changing the volume." / "So its volume is $\lvert\det A\rvert$, here still 12." / "Day 29 solves $\det(A - \lambda I) = 0$ to find eigenvalues." |
| 172–177 | Takeaway card with origin pulse | end |

The final render runs 176.8 s.
