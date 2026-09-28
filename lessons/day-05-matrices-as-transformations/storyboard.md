# Day 5: Matrices are transformations

Day 4 ended with $A\mathbf x$ as one new vector and the rules $A(\mathbf u + \mathbf v) = A\mathbf u + A\mathbf v$ and
$A(c\mathbf u) = cA\mathbf u$. Today the same product moves every point at once. The static grid stays underneath,
dimmed, while a blue copy of the grid moves; this matches the web widget `TransformExplorer`. $\mathbf e_1$ is
green and $\mathbf e_2$ is red, and a matrix's first column is green and its second red, so each landing spot and
the column it becomes share a color. The input vector $\mathbf x$ is yellow and outputs are teal. The plane is
drawn at 1.15 scale with its origin just right of center and low, which leaves the top-left corner for the panel.

Every grid state comes from four entry trackers (`MatrixTracker` in `engine/theme.py`), so the moving grid,
the basis arrows and any vector riding on the grid are all functions of the current matrix.

The times below are the plan; the gallery and slide rows run about 3 seconds later than listed after the Day 20 pointer.

| t (s) | State | Trigger |
|---|---|---|
| 0–6 | Title card "Matrices are transformations", "Day 5" | start |
| 6–9 | Glowing origin, grid draws outward | after title |
| 9–17 | Panel A = [[1, 1], [0, 1]] writes; yellow x = (1, 2) grows; panel extends to Ax = (3, 2); orange ring marks (3, 2) | captions "Yesterday a matrix $A$ met one vector $\mathbf x$.", "Their product $A\mathbf x$ was one new vector." (link to Day 4) |
| 17–23 | Static grid dims; the blue moving grid fades in on top; green e₁ and red e₂ grow | caption "Today we ask what $A$ does to every point at once." (today's question) |
| 23–30 | **Centerpiece, part 1:** entries spring from I to A. The grid shears, x rides along and lands in the ring, which flashes | caption "The grid shears, and $\mathbf x$ rides along to $A\mathbf x$." |
| 30–40 | Landing labels (1, 0) and (1, 1) appear at the green and red tips, then fly into the columns of A, which glow | captions "$\mathbf e_1$ stays put and $\mathbf e_2$ lands on $(1, 1)$.", "Those landing spots are exactly the columns of $A$." |
| 40–50 | Orange dots mark equal steps along one sheared line; a flash at the origin | captions "Grid lines stay straight, parallel and evenly spaced.", "The origin never moves." |
| 50–58 | Grid springs back to I; x and its ring leave; panel shows A with four muted question marks | caption "Next we find a quarter turn's matrix from its landing spots." (goal before the procedure) |
| 58–64 | **Centerpiece, part 2:** the grid rotates 90° counterclockwise (angle-driven, so it turns rather than shrinking) | caption "A quarter turn sends $\mathbf e_1$ up and $\mathbf e_2$ left." |
| 64–72 | Landing labels (0, 1) and (−1, 0) appear, then fly into the columns, replacing the question marks | caption "Write each landing spot in as a column." |
| 72–80 | Hold on the finished rotation matrix | caption "Two columns are enough to move every point." |
| 80–88 | Grid turns back. Panel clears. Yellow x = (2, 1) with its walk: green, green, red steps tip to tail | caption "Every vector is a walk of $\mathbf e_1$ and $\mathbf e_2$ steps." |
| 88–96 | Entries spring to [[2, −1], [1, 1]]. The steps become T(e₁), T(e₁), T(e₂) and the walk ends at (3, 3) | caption "Move the steps, and the walk moves with them." |
| 96–108 | Panel: T(x) = 2T(e₁) + 1T(e₂) = 2(2, 1) + 1(−1, 1) = (3, 3), then the general rule and the two linearity rules | captions "So $T(\mathbf x) = x_1T(\mathbf e_1) + x_2T(\mathbf e_2)$ for every $\mathbf x$.", "That works because $T$ keeps sums and multiples." |
| 108–111 | Hold on the panel with the two linearity rules | caption "On Day 20 these two rules become the definition of linear." (forward pointer) |
| 108–114 | Grid resets; walk leaves; yellow unit square appears | caption "Here is a small gallery of other moves." |
| 114–120 | Stretch [[2, 0], [0, 1]]; the matrix entries crossfade | caption "A stretch doubles $\mathbf e_1$ and leaves $\mathbf e_2$ alone." |
| 120–127 | Back to I, then reflection [[−1, 0], [0, 1]]; the square turns pink as it flips | caption "A reflection flips $\mathbf e_1$ over to the left." |
| 127–135 | Back to I, then projection [[1, 0], [0, 0]]; the whole grid collapses onto the x₁-axis | caption "A projection sends $\mathbf e_2$ to the origin." |
| 135–146 | Back to I. The grid slides by (1, 1); the origin mark rides away and an orange ring stays at the true origin | captions "Sliding the plane by $(1, 1)$ moves the origin.", "Since $A\mathbf 0 = \mathbf 0$, no matrix can do that." |
| 146–149 | Hold on the slid grid and the ringed true origin | caption "Tomorrow, two moves in a row become one matrix." (what today unlocks) |
| 149–157 | Takeaway card with origin pulse | end |
