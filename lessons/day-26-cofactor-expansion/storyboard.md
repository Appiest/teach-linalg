# Day 26: Computing determinants

The video opens on the plane with Day 25's picture, then moves to matrices under a scrim for most of the lesson, and
comes back to the plane once, for the row operations. The worked 3×3 matrix is fresh, not Lay's:
A = [[2, 2, 1], [1, 0, 1], [0, −2, −1]], with det A = 4. Across row 1 its terms are 4, +2 and −2. Down column 2
the middle entry is 0, so only two minors are needed, and the term −(−2)·1 = +2 shows the sign coming from the
position times the sign of the entry.

Colors: the active entry is yellow, the entries of its minor are blue, every term is teal, and the checkerboard
signs are small orange marks while they are in use. The parallelogram of the columns is yellow while
det > 0 and pink once the orientation flips, like the notes widgets.

| t (s) | State | Trigger |
|---|---|---|
| 0–8 | Title card "Computing determinants", "Day 26"; origin pulse; grid draws outward | start |
| 8–18 | The unit square springs into the parallelogram of M = [[2, 1], [1, 2]] (green column (2, 1), red column (1, 2)). The panel shows M and det M = 2·2 − 1·1 = 3 | captions "On Day 25, det measured how a matrix scales area.", "For 2 by 2, the formula ad − bc gives it." |
| 18–22 | Scrim covers the plane. A writes in on the left | caption "Bigger matrices need a recipe, built from 2 by 2 pieces." |
| 22–38 | Row 2 and column 3 of A dim. The four entries left fly out into A₂₃ = [[2, 2], [0, −2]] on the right. det A₂₃ = −4 writes beside it, then C₂₃ = (−1)^{2+3}(−4) = 4 | captions "Delete row 2 and column 3, and a 2 by 2 matrix remains.", "Its determinant is called a minor.", "The cofactor C₂₃ gives the minor a sign." |
| 38–44 | The dimmed row and column return. A + − + checkerboard ripples in over the entries of A | caption "The sign depends only on the position, like a checkerboard." |
| 44–72 | **Centerpiece.** Row 1 is expanded entry by entry. For each entry: its row and column dim, the entry turns yellow, the four entries of its minor turn blue, and its sign glows. The sign and entry fly out to start a new line on the right, the minor's entries fly into a small determinant, its two diagonals are drawn in orange, the cross product 0·(−1) − 1·(−2) writes beside it and collapses to its value, and the teal term appears. Each term flies down into a running sum det A = 4 + 2 − 2 = 4 | captions "Expand along row 1: each entry times its cofactor.", "Cover its row and column, and a 2 by 2 minor remains.", "Position (1, 2) takes a minus sign from the checkerboard.", "The last entry adds its own term the same way.", "The three terms add up to det A = 4." |
| 72–90 | The three lines fade and the sum moves down. Column 2 lights up (signs −, +, −). Its top entry gives +2; the 0 in the middle gives 0 with no minor; the bottom entry −2 at a minus position gives −(−2)·1 = +2. A second sum det A = 2 + 0 + 2 = 4 lands under the first and both 4s glow | captions "Any row or column gives the same number.", "A zero entry makes its whole term zero.", "A minus position times the entry −2 gives plus 2.", "Pick the line with the most zeros to save work." |
| 90–104 | A clears. U = [[3, 1, 4], [0, 2, 5], [0, 0, −1]] appears with a dashed outline around its zeros. Expanding down column 1 keeps only 3 times the minor [[2, 5], [0, −1]], which is triangular again, so det U = 3·2·(−1) = −6 and the diagonal glows | captions "In a triangular matrix, every entry below the diagonal is 0.", "Down column 1, only the top entry survives.", "So det U is the product of the diagonal entries." |
| 104–128 | The scrim lifts back to M's parallelogram and a live det counter. Three row operations play on the panel and the plane at once: R₂ ← R₂ − R₁ shears the parallelogram and the counter holds at 3; R₁ ↔ R₂ flattens it through a segment and flips it pink while the counter passes 0 to −3; R₁ ← 2R₁ stretches it sideways to −6. Each rule is added to the panel | captions "Row operations change det in three predictable ways.", "Adding a multiple of another row shears the area.", "The area never changes, so det stays 3.", "Swapping two rows flips the picture over, so det turns negative.", "Scaling a row by 2 doubles the area and det." |
| 128–146 | Scrim. det B = [[0, 1, 2], [1, 2, 1], [2, 3, 4]]. The rows swap past each other and a minus sign appears in front; two replacements crossfade only the entries that change; the diagonal of the triangular result glows and det B = −(1·1·4) = −4 writes | captions "So row reduce to a triangular matrix, tracking every change.", "Swapping rows 1 and 2 puts a minus sign in front.", "Replacements leave the determinant alone.", "Multiply the diagonal and keep the sign: det B = −4." |
| 146–158 | A comes back. Every entry flies across the diagonal into Aᵀ. det Aᵀ = det A = 4 writes under them. Then the pair is replaced by M, N and MN with det 3, 2 and 6 | captions "Flipping A over its diagonal gives its transpose.", "Rows of Aᵀ are columns of A, so det Aᵀ = det A.", "Areas scale one after the other, so det MN = det M det N." |
| 158–166 | Takeaway card with origin pulse | end |

Figures for the notes:

- `FigCheckerboard`: A with row 2 and column 3 dimmed and the sign checkerboard overlaid, beside A₂₃ and
  C₂₃ = (−1)^{2+3} det A₂₃ = 4.
- `FigExpansion`: the finished row-1 expansion, with A, its three lines and the sum.
- `FigRowOperations`: four small planes in a row: M, then after each row operation, each with its matrix and
  determinant, and arrows labelled with the operation.

The poster is the centerpiece mid-way: row 1 and column 2 dimmed, the minor blue, the first line finished.

The final render runs 163.6 s, so the later rows land a few seconds earlier than listed.
