# Day 9: LU decomposition

Colors keep their course meanings. The unknown x is yellow, the halfway vector y is blue, and the right-hand
side b is teal, as in Day 4. Multipliers are pink everywhere they appear, both in the operation labels and in the
lower triangle of L. Pivot boxes are orange, as in Day 3.

The opening picture uses a 2 × 2 matrix whose two factors are shears: A = [[1, 1], [2, 3]], U = [[1, 1], [0, 1]],
L = [[1, 0], [2, 1]], with x = (1, 1), y = (2, 1), b = (2, 5). The centerpiece and the solve use the fresh 3 × 3
problem from the guide: A = [[2, 1, −1], [4, 5, 0], [−2, 8, 5]], L = [[1, 0, 0], [2, 1, 0], [−1, 3, 1]],
U = [[2, 1, −1], [0, 3, 2], [0, 0, −2]], with b = (−1, −1, 0), then b = (0, 5, 13).

| t (s) | State | Trigger |
|---|---|---|
| 0–7 | Title card "LU decomposition", "Day 9" | start |
| 7–10 | Glowing origin, grid draws outward | after title |
| 10–15 | Panel top-left writes A = LU for the 2 × 2 example, with L and U named under their factors; yellow x = (1, 1) grows | caption "Here a matrix $A$ is written as a product $LU$." |
| 15–20 | U flashes in the panel; the grid shears sideways under U and x slides to the blue y = (2, 1) | caption "Multiplying by $U$ first shears the grid sideways." |
| 20–27 | L flashes; the grid shears vertically under L and y climbs to teal b = (2, 5) | caption "Then $L$ shears it vertically and lands on $\mathbf b$." |
| 27–36 | Reverse: the panel adds Ly = b and the L shear undoes (b back to y); the line becomes Ux = y and the U shear undoes (y back to x) | caption "To solve $A\mathbf x = \mathbf b$, undo $L$ first, then $U$." |
| 36–38 | Plane fades out | — |
| 38–42 | 3 × 3 A on the right, labelled A. L on the left with 1s on the diagonal, 0s above and empty slots below | caption "Elimination builds $L$ and $U$ at the same time." |
| 42–56 | **Centerpiece, step 1.** Pivot column (2, 4, −2) boxed in orange. "÷ 2" appears and the column crossfades to (1, 2, −1) in the gap, multipliers pink. The pink 2 and −1 arc into column 1 of L as the slots fade. The label R₂ ← R₂ − 2R₁, R₃ ← R₃ − (−1)R₁ appears and A morphs to A₁ = [[2, 1, −1], [0, 3, 2], [0, 9, 4]] | captions "Divide the pivot column by its pivot.", "Those numbers drop into column 1 of $L$.", "The same multipliers clear the entries below the pivot." |
| 56–64 | **Step 2.** Pivot column (3, 9) boxed; ÷ 3 gives (1, 3); pink 3 drops into L; the matrix morphs to U under R₃ ← R₃ − 3R₂ | caption "Repeat one column over, using the current matrix." |
| 64–67 | Last pivot −2 boxed; nothing sits below it | caption "The last pivot has nothing below it, so we are done." |
| 67–75 | Label A crossfades to U. A dashed staircase wraps U's zeros, then L's zeros | captions "$U$ is an echelon form, all zeros below the diagonal.", "$L$ has 1s on its diagonal and zeros above." |
| 75–86 | L and U slide right and A fades in on the left, so the row reads A = LU. Row 2 of L and rows 1–2 of U get orange boxes, which copy into a teal box on row 2 of A | captions "Multiplying $LU$ adds the multiples back and rebuilds $A$.", "Row 2 of $A$ is 2 copies of row 1 of $U$ plus row 2." |
| 86–92 | Beneath, E₂E₁A = U crossfades to A = (E₂E₁)⁻¹U = LU | caption "Elimination is $E_2E_1A = U$, so $L$ is $(E_2E_1)^{-1}$." |
| 92–106 | L shrinks to the top as Ly = b with b = (−1, −1, 0); U waits below. Row by row from the top, a box lights the row, its arithmetic appears at right, and y₁, y₂, y₃ crossfade to −1, 1, −4 | captions "First solve $L\mathbf y = \mathbf b$ from the top row down.", "Each row adds one new unknown, so plug in and go." |
| 106–121 | The solved y copies down as the right side of Ux = y. From the bottom row up, x₃, x₂, x₁ become 2, −1, 1 with their arithmetic | captions "Then solve $U\mathbf x = \mathbf y$ from the bottom row up.", "Work upward, plugging in what is already known.", "So $\mathbf x = (1, -1, 2)$ solves $A\mathbf x = \mathbf b$." |
| 121–129 | Work lines fade. b crossfades to (0, 5, 13), then y to (0, 5, −2), then x to (0, 1, 1) | caption "A new $\mathbf b$ reuses $L$ and $U$, with no elimination." |
| 129–144 | Cost chart for n = 1000: right-hand sides 0 to 100 across, billions of flops up. The purple-gray line "row reduce each time" sweeps up to an orange dot at ≈ 67; the teal line "LU once" stays flat to ≈ 0.87 | captions "For $n = 1000$, row reducing costs $\tfrac23 n^3$ flops each time.", "LU pays $\tfrac23 n^3$ once, then about $2n^2$ per $\mathbf b$.", "At 100 right-hand sides, LU does 77 times less work." |
| 144–151.5 | Takeaway card with origin pulse | end |
