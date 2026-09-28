# Day 4: Matrix times vector

The columns reuse Day 1's vectors: a₁ = (3, 2) is yellow (Day 1's v) and a₂ = (−1, 2) is blue (Day 1's w). Each
weight in x wears its column's color, and every result is teal. The plane is drawn at 0.75 scale with its origin low
and left of center, so (5, 6) and (7, 2) fit beside the equation panel in the top-left corner.

| t (s) | State | Trigger |
|---|---|---|
| 0–6 | Title card "Matrix times vector", "Day 4" | start |
| 6–9 | Glowing origin, grid draws outward | after title |
| 9–15 | A = [[3, −1], [2, 2]] and x = (2, 1) write in the top-left panel as Ax | caption "Here is a matrix A and a vector x." |
| 15–22 | Column 1 of A lights up and flies out as the yellow arrow a₁, then column 2 as the blue arrow a₂ | caption "Read A as two columns, each one a vector." |
| 22–30 | x₁ = 2 flashes; a₁ springs to 2a₁ with a faint copy left behind. x₂ = 1 flashes on a₂ | caption "The entries of x are weights, one for each column." |
| 30–36 | **Centerpiece:** a₂ slides tip-to-tail onto 2a₁; teal Ax grows to (5, 6) and an orange stamp lands on its tip | caption "Scale each column, then add them tip to tail." |
| 36–44 | Panel extends to Ax = 2a₁ + 1a₂ = (5, 6) | caption "So Ax is a combination of the columns of A." |
| 44–52 | General formula Ax = x₁a₁ + ⋯ + xₙaₙ replaces the panel | caption "x needs exactly one entry for each column of A." |
| 52–72 | Plane dims. Center: 2(3, 2) + 1(−1, 2) = (2·3 + 1·(−1), 2·2 + 1·2) = (5, 6). Row 1 of A, all of x and the first entry glow together, then row 2 | captions "Write the sum out entry by entry.", "Each entry uses one row of A and all of x.", "That shortcut is the row rule, and it agrees." |
| 72–92 | Plane returns. Target b = (7, 2) appears as an orange ring. Sliders x₁, x₂ spring through (1, 1), (2, 0), (2, −1); the teal tip lands on b | captions "Now flip the question: which x lands on b?", "Solving Ax = b asks whether b is in the span." |
| 92–112 | Plane dims. System, vector equation and matrix equation stack; colored entries transform from one to the next. The augmented matrix row reduces to x₁ = 2, x₂ = −1 | captions "Here is the same problem written three ways.", "One augmented matrix solves all three.", "Row reduction confirms the weights 2 and −1." |
| 112–130 | Plane returns. a₂ springs to (6, 4), parallel to a₁. The span line draws through the origin; the teal tip slides along it and misses b. Panel shows [A b] ~ [[3, 6, 7], [0, 0, −8]] and the last row glows | captions "Parallel columns only span a line.", "Now b is off the line, so no x works.", "Row reduction agrees: the last row says 0 = −8." |
| 130–138 | Takeaway card with origin pulse | end |
