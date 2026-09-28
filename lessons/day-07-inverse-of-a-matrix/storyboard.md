# Day 7: The inverse of a matrix

The main matrix is A = [[2, 1], [1, 1]]. Its determinant is 1 and its inverse is [[1, −1], [−1, 2]], so every
landing spot is a small integer. Day 5's colors carry over: ê₁ and its column are green, ê₂ and its column are red.
The point x = (1, 1) is yellow, and A sends it to (3, 2), Day 1's v. Results and targets are teal, the inverse's
columns are pink, and orange marks stamps and warnings only. Days 5 and 6 used S = [[1, 1], [0, 1]] for the shear
and R = [[0, −1], [1, 0]] for the quarter turn, so the product section reuses them.

The grid is drawn live from one 2×2 matrix (`LiveTransform` in `engine/theme.py`). Each move left-multiplies it by
(1 − s)I + sE, so "playing A backwards" is literally the straight path from A back to I, and a rotation turns
through its angle instead of cutting across. The opening grid is styled exactly like the live grid (faint, wide
strokes) so the swap between them needs no crossfade; that styling also keeps the moving grids inside the 12 MB budget.

| t (s) | State | Trigger |
|---|---|---|
| 0–6 | Title card "The inverse of a matrix", "Day 7" | start |
| 6–9 | Glowing origin, grid draws outward | after title |
| 9–12 | A writes in the top-left panel with green and red columns over the empty grid | caption "Yesterday we chained moves. Today we undo one." (motivation) |
| 12–18 | ê₁, ê₂ and yellow x = (1, 1) grow | caption "Here is a matrix A and a point x." |
| 16–22 | Grid morphs I → A. ê₁ lands on (2, 1), ê₂ on (1, 1), x on (3, 2); an orange stamp marks Ax | caption "A moves every point of the plane." |
| 20–30 | **Centerpiece:** the grid plays backwards from A to I and x rides home to (1, 1). The panel grows A⁻¹ = [[1, −1], [−1, 2]] | captions "Can we play that motion backwards?", then, holding on x back home, "Undoing A would solve Ax = b in one step." (why it matters), "The matrix that undoes A is its inverse." |
| 30–40 | Pink arrows (1, −1) and (−1, 2) grow from A⁻¹'s columns. The grid morphs under A again and they land exactly on ê₁ and ê₂, marked by orange stamps. The grid returns home behind the next scrim | captions "The columns of the inverse are what A sends to ê₁ and ê₂." |
| 40–52 | Scrim. AA⁻¹ = I and A⁻¹A = I written out with numbers | captions "Undo after A, or A after undo: both give I.", then "We want a matrix whose product with A is I." (goal of the formula) over the two products |
| 52–70 | General formula [[a, b], [c, d]]⁻¹ = 1/(ad − bc)[[d, −b], [−c, a]]. On A: the diagonal entries swap places, the other two flip sign, then det = 2·1 − 1·1 = 1 fills the fraction | captions "For 2 × 2 matrices, a formula builds it directly.", "Swap the diagonal and flip the other two signs.", "Then divide by ad − bc, the determinant.", "On Day 25 the determinant turns out to measure area." (forward pointer) |
| 70–88 | Plane returns. Teal b = (4, 3) with a ring. The grid morphs I → A⁻¹ and b rides to (1, 2), which turns yellow as x. Panel: x = A⁻¹b = (1, 2). Grid morphs back so x lands on b | captions "To solve Ax = b, send b back through A⁻¹.", "Only one point comes back, so the solution is unique." |
| 88–112 | Panel S (shear), R (quarter turn). Grid shears then turns (RS). Wrong undo: S⁻¹ then R⁻¹; the grid ends skewed and x misses home (orange flash). Grid returns to RS. Right undo: R⁻¹ then S⁻¹; home. Panel (RS)⁻¹ = S⁻¹R⁻¹ | captions "Shear first, then turn: that product is RS.", "Undoing the shear first leaves the grid skewed.", "Undo the turn first, then the shear.", "Shoes come off before socks: (AB)⁻¹ = B⁻¹A⁻¹.", "Tomorrow this rule undoes a whole chain of row operations." (forward pointer) |
| 112–130 | Panel M = [[1, 2], [2, 4]], det = 4 − 4 = 0. Grid flattens onto the line through (1, 2). Three points (1, 0), (−1, 1), (3, −1) on the faint preimage line all land on (1, 2). Dashed paths fan back from (1, 2) to all three | captions "When ad − bc = 0, the plane flattens onto a line.", "Three different points land on (1, 2).", "Going back would need three answers, so no inverse exists.", "Next, row reduction finds inverses of any size." (what it unlocks) |
| 130–139 | Takeaway card with origin pulse | end |

The motivation beats added about 12 s, so the final render runs 151.1 s and every row after the opening lands later than listed.
