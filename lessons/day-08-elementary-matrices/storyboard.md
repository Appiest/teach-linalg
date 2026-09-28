# Day 8: Elementary matrices and computing inverses

One grid carries the whole video. The plane is drawn at 1.25 scale with its origin right of center, so the
matrix panel sits on a plate in the top-left corner. A blue sheet of grid lines (the image of the square from −4 to 4, kept finite so the video stays small) shows the plane after the current matrix, and
green and red arrows show where î and ĵ land. Those arrows are the columns of the current matrix, so the
matching columns of every matrix on screen are green and red. Every change to the grid is a sum of entry
trackers animated with `spring`, so one continuous grid morphs from step to step.

The worked matrix is A = [[2, 1], [1, 1]] (fresh, not from Lay). Its reduction uses all three kinds of row
operation: R₁ ↔ R₂, R₂ ← R₂ − 2R₁, R₂ ← −R₂, R₁ ← R₁ − R₂, and A⁻¹ = [[1, −1], [−1, 2]].

| t (s) | State | Trigger |
|---|---|---|
| 0–8 | Title card "Elementary matrices and computing inverses", "Day 8"; origin pulse; grid draws outward | start |
| 8–13 | Blue grid fades in over the plane with î and ĵ on the basis | caption "Row operations from Day 3 can be written as matrices." |
| 13–21 | Panel "I = [[1, 0], [0, 1]]" writes in the top-left. The label R₂ ← R₂ − 2R₁ appears under it, row 2 glows, the bottom-left entry crossfades 0 → −2, and I becomes E | captions "Start with I and do one row operation to it.", "The result is an elementary matrix, E." |
| 21–33 | Plane dims under a scrim. E [[a, b], [c, d]] = [[a, b], [c − 2a, d − 2b]] writes in the center. Row 2 of E and row 2 of the answer are boxed in orange together | captions "Multiplying by E does that row operation to any matrix.", "Row 2 of E says: −2 times row 1, plus row 2." |
| 33–42 | Scrim lifts. The grid shears: î springs to (1, −2) while ĵ stays. Then it springs back, and E⁻¹ with R₂ ← R₂ + 2R₁ appears under E | captions "As a move of the plane, E is a shear.", "Adding 2 times row 1 back undoes it." |
| 42–51 | Panel morphs to the swap R₁ ↔ R₂. The grid flips across y = x (î and ĵ trade places), then flips back; E⁻¹ = E | caption "A swap reflects the plane, and swapping again undoes it." |
| 51–60 | Panel morphs to R₁ ← 2R₁. The grid stretches sideways, then shrinks back; E⁻¹ has ½ | caption "Scaling by 2 stretches it, and scaling by ½ undoes it." |
| 60–68 | Panel clears. The grid springs from square to A: î lands on (2, 1) and ĵ on (1, 1). [A \| I] writes in the panel, A's columns in green and red | captions "Here is A and the grid it makes.", "Row reduce A to I, doing each step to I as well." |
| 68–100 | **Centerpiece.** Four steps. Each step: the operation label and E_k appear under the left block, the augmented matrix crossfades only the changed entries, and at the same moment the grid moves by E_k (reflect, shear, flip, shear). Under the right block a running product E₁ → E₂E₁ → E₃E₂E₁ → E₄E₃E₂E₁ updates | one caption per step: "Swap the rows: the grid reflects.", "Subtract 2 times row 1: the grid shears down.", "Scale row 2 by −1: the grid flips over.", "Subtract row 2 from row 1: the grid is square again." |
| 100–106 | The right block turns teal and pulses orange, and the label under it becomes A⁻¹ | caption "The left half is I, so the right half is A⁻¹." |
| 106–118 | Scrim. E₄E₃E₂E₁A = I, then E₄E₃E₂E₁ = A⁻¹, then E₄E₃E₂E₁I = A⁻¹ stack, each derived from the one above | captions "Four steps turned A into I.", "So their product is A⁻¹.", "The right half applied that product to I." |
| 118–132 | Scrim lifts, grid square. The grid runs the steps backwards: E₄⁻¹, E₃⁻¹, E₂⁻¹, E₁⁻¹, and A = E₁⁻¹E₂⁻¹E₃⁻¹E₄⁻¹ builds from the right one factor per move, ending on A's grid | captions "Run the steps backwards to build A.", "So A is a product of elementary matrices." |
| 132–146 | New matrix B = [[1, 2], [1, 2]]. The grid springs from square to a single line y = x. [B \| I] reduces by R₂ ← R₂ − R₁ to a zero row, which turns orange; the grid line tips down to the x-axis | captions "This B flattens the plane onto a line.", "A zero row appears, so B has no inverse." |
| 134–142 | Takeaway card with origin pulse | end |

Figures for the notes: `FigShear` (E = [[1, 0], [−2, 1]] shearing the grid with I and E side by side),
`FigThreeKinds` (three small grids, one per kind, each with E and E⁻¹), `FigInverseSteps` ([A | I] through the
four steps to [I | A⁻¹], each step labelled with its E_k). The poster is the centerpiece mid-way: A's grid with
î and ĵ, and the panel [A | I] ∼ [I | A⁻¹].

The final render runs 141.6 s. Every grid move lasts 1 s, so the later rows of the table land a few seconds earlier than listed.
