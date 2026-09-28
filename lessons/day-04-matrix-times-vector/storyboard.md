# Day 4: Matrix times vector

The columns reuse Day 1's vectors: a₁ = (3, 2) is yellow (Day 1's v) and a₂ = (−1, 2) is blue (Day 1's w). Each
weight in x wears its column's color, and every result is teal. The plane is drawn at 0.75 scale with its origin low
and left of center, so (5, 6) and (7, 2) fit beside the equation panel in the top-left corner.

| t (s) | State | Trigger |
|---|---|---|
| 0–6 | Title card "Matrix times vector", "Day 4" | start |
| 6–9 | Glowing origin, grid draws outward | after title |
| 9–13 | The vector equation x₁(3, 2) + x₂(−1, 2) = **b** writes in the top-left panel | caption "Day 2 asked which weights combine these vectors into b." |
| 13–18 | The columns slide together into A, x₁ and x₂ stack into x, the plus sign fades: Ax = b | caption "Today we write that question as one short equation." |
| 18–24 | A = [[3, −1], [2, 2]] and x = (2, 1) write in the top-left panel as Ax | caption "Here is a matrix A and a vector x." |
| 24–31 | Column 1 of A lights up and flies out as the yellow arrow a₁, then column 2 as the blue arrow a₂ | caption "Read A as two columns, each one a vector." |
| 31–39 | x₁ = 2 flashes; a₁ springs to 2a₁ with a faint copy left behind. x₂ = 1 flashes on a₂ | caption "The entries of x are weights, one for each column." |
| 39–45 | **Centerpiece:** a₂ slides tip-to-tail onto 2a₁; teal Ax grows to (5, 6) and an orange stamp lands on its tip | caption "Scale each column, then add them tip to tail." |
| 45–53 | Panel extends to Ax = 2a₁ + 1a₂ = (5, 6) | caption "So Ax is a combination of the columns of A." |
| 53–61 | General formula Ax = x₁a₁ + ⋯ + xₙaₙ replaces the panel | caption "x needs exactly one entry for each column of A." |
| 61–63 | General formula glows | caption "Next we want a faster way to compute Ax by hand." |
| 63–83 | Plane dims. Center: 2(3, 2) + 1(−1, 2) = (2·3 + 1·(−1), 2·2 + 1·2) = (5, 6). Row 1 of A, all of x and the first entry glow together, then row 2 | captions "Write the sum out entry by entry.", "Each entry uses one row of A and all of x.", "That shortcut is the row rule, and it agrees." |
| 83–102 | Plane returns. Target b = (7, 2) appears as an orange ring. Sliders x₁, x₂ spring through (1, 1), (2, 0), (2, −1); the teal tip lands on b | captions "Now flip the question: which x lands on b?", "Solving Ax = b asks whether b is in the span." |
| 102–122 | Plane dims. System, vector equation and matrix equation stack; colored entries transform from one to the next. The augmented matrix row reduces to x₁ = 2, x₂ = −1 | captions "Here is the same problem written three ways.", "One augmented matrix solves all three.", "Row reduction confirms the weights 2 and −1." |
| 122–140 | Plane returns. a₂ springs to (6, 4), parallel to a₁. The span line draws through the origin; the teal tip slides along it and misses b. Panel shows [A b] ~ [[3, 6, 7], [0, 0, −8]] and the last row glows | captions "Parallel columns only span a line.", "Now b is off the line, so no x works.", "Row reduction agrees: the last row says 0 = −8." |
| 140–144 | Reduction panel and target fade; a₂ springs back to (−1, 2); x runs to (1, 1) then (2, 1) and the teal Ax follows | caption "Tomorrow, A becomes a rule that moves every x to Ax." |
| 144–149 | Takeaway card with origin pulse | end |
