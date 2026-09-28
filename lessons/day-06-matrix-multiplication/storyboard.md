# Day 6: Matrix multiplication is composition

Colors carry over from Days 1 to 5. The basis arrows are green î and red ĵ, and every column of a transformation
matrix wears the color of the basis arrow it records. The moving point x = (1, 1) is yellow, like Day 1's main
vector, and the transformed grid is blue, like the `TransformExplorer` widget from Day 5. The shear
S = [[1, 1], [0, 1]] is yesterday's shear, and R = [[0, −1], [1, 0]] is the quarter turn.

Every grid motion is driven by a tracker whose value is the fraction of the step done: a shear by t·1, then a
rotation by t·90°. Rotating by angle rather than interpolating matrix entries keeps the grid from shrinking
halfway through the turn.

The times below are the plan. The rendered video runs 137 seconds, so later rows land up to 20 seconds earlier.

| t (s) | State | Trigger |
|---|---|---|
| 0–6 | Title card "Matrix multiplication is composition", "Day 6" | start |
| 6–9 | Glowing origin, grid draws outward | after title |
| 9–16 | î, ĵ and the yellow x = (1, 1) grow. Panel top-left writes S | caption "Start with yesterday's shear $S$." |
| 16–22 | Blue grid shears; ĵ tilts to (1, 1); x slides to (2, 1). A faint yellow hop arc labelled S joins the two spots | caption "The shear moves $\mathbf x$ to $S\mathbf x$." |
| 22–30 | Panel adds R to the left of S. The grid turns a quarter turn; x lands on (−1, 2). Second hop arc labelled R | caption "Then rotate everything a quarter turn with $R$." |
| 30–37 | One long teal arc draws straight from x to its final spot, labelled RS | caption "Two moves in a row act like one transformation." |
| 37–46 | Green and red landing spots (0, 1) and (−1, 1) fly into the columns of a new matrix RS = [[0, −1], [1, 1]] | caption "Its columns are where î and ĵ finally land." |
| 46–55 | R(Sx) = (RS)x writes under the panel; an arrow under RSx points right to left, S glows, then R | caption "Read right to left: $S$ touches $\mathbf x$ first." |
| 55–75 | Plane dims. RS = R[s₁ s₂] = [Rs₁ Rs₂] = [[0, −1], [1, 1]]. Column 1 of S glows green and R·s₁ drops into column 1, then column 2 in red | captions "Each column of $RS$ is $R$ applied to a column of $S$.", "That is the column rule for any product." |
| 75–80 | General rule AB = [Ab₁ ⋯ Abₚ] replaces the example | same caption |
| 80–102 | A = [[1, 2], [−3, 4]] times B = [[2, 0, −1], [5, 1, 3]]. Sizes 2×2 and 2×3 write underneath; the inner 2s glow and the outer ones drop to "2×3". Row 2 of A and column 3 of B box in orange; (−3)(−1) + 4·3 = 15 appears and flies into the empty (2, 3) slot; the other entries fade in | captions "The inner sizes must match. The outer sizes give the answer.", "One entry is a row of $A$ times a column of $B$.", "Every entry of $AB$ works the same way." |
| 102–134 | **Centerpiece.** Two panels side by side, each with its own grid, î, ĵ and x. Left, "shear, then rotate"; right, "rotate, then shear". Step 1 plays in both at once (shear on the left, rotation on the right), then step 2. The yellow tips end at (−1, 2) and (0, 1). An orange stamp lands on each, and RS and SR write under their panels from the landing spots | captions "Now do the same two moves in the other order.", "First moves happen together, then second moves.", "They end in different places, so $RS \neq SR$." |
| 134–150 | Plane dims. B = [[2, 0, −1], [5, 1, 3]]; each row copies down into a column of Bᵀ. Then (AB)ᵀ = BᵀAᵀ with sizes 3×2 and 2×2 underneath | captions "The transpose turns each row into a column.", "Transposing a product reverses the order." |
| 150–158 | Takeaway card with origin pulse | end |
