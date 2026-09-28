# Day 18: Rank and nullity

Day 16 ended with the $3\times 3$ matrix $A = \begin{bmatrix}1&0&-1\\0&1&1\\1&1&0\end{bmatrix}$, whose columns are
green, red and pink and whose column space is the tilted teal plane $z = x + y$. Day 17 showed that a matrix crushes a
whole subspace of inputs, its null space, onto the origin. Today opens on that same matrix acting on all of
$\mathbb R^3$ in Day 16's oblique view (`OrbitingView`, elevation 20°): a blue cube of inputs flattens onto the teal
plane, and the pink line $\operatorname{Nul}A = \operatorname{Span}\{(1, -1, 1)\}$ shrinks into the origin, which glows.

Colors for the tally, fixed for the whole lesson and the notes: a **pivot column** is teal (it survives into the
output, and teal is the output color), a **free column** is pink (Day 16's redundant third column was pink). Orange
frames mark pivot entries, as on Day 16.

The centerpiece matrix is new, with small integers and a zero row:
$$A = \begin{bmatrix}1&0&2&0&1\\1&1&1&0&3\\2&1&3&1&3\\3&1&5&1&4\end{bmatrix}
\sim \begin{bmatrix}1&0&2&0&1\\0&1&-1&0&2\\0&0&0&1&-1\\0&0&0&0&0\end{bmatrix}$$
Pivots sit in columns 1, 2 and 4, so rank 3 and nullity 2 (checked with sympy).

| t (s) | State | Trigger |
|---|---|---|
| 0–6 | Title card "Rank and nullity", "Day 18" | start |
| 6–8 | Glowing origin pulse | after title |
| 8–15 | Day 16's $A$ writes top left with green, red and pink columns (caption "Days 16 and 17 gave every matrix two subspaces."); 3D axes draw (caption "Today we ask how their sizes are related."); a blue lattice cube $[-1,1]^3$ draws; a pink line through $(1,-1,1)$ draws; the view swings from azimuth 35° to 60° | caption "Day 16's matrix has three columns, so it acts on $\mathbb R^3$." |
| 15–22 | The cube morphs from $\mathbf x$ to $A\mathbf x$ and lands flat; the teal sheet fades in with its $\operatorname{Col}A$ tag | captions "Watch a cube of inputs pass through $A$.", "Everything lands flat on the plane $\operatorname{Col}A$." |
| 22–28 | Replay the pink line alone: it shrinks into the origin, which flashes orange; $\operatorname{Nul}A$ tag | caption "One whole line of inputs lands on zero." |
| 28–40 | Counts write top right: $\operatorname{rank}A = \dim\operatorname{Col}A = 2$, then $\operatorname{nullity}A = \dim\operatorname{Nul}A = 1$, then $2 + 1 = 3$ | captions "Two dimensions survive, so $\operatorname{rank}A = 2$.", "One dimension is crushed, so $\operatorname{nullity}A = 1$.", "Together they make $3$, one for each column." |
| 40–47 | 3D scene clears; the $4\times 5$ matrix writes large at center | caption "Here is a bigger matrix with five columns." |
| 47–58 | Three row-reduction steps morph in place, each with its row operation label | goal caption "Row reduce until the pivots show, since they decide both counts." |
| 58–84 | **Centerpiece:** five empty cells sit under the five columns. A scan bar sweeps left to right. Column 1: orange frame on its pivot, column tints teal, its cell fills teal and a teal block drops into the rank bar. Column 2 same. Column 3: no pivot, tints pink, its cell fills pink and a pink block drops into the nullity bar, $x_3$ free. Column 4 teal, column 5 pink, $x_5$ free | captions "Sweep the columns: each one is a pivot or free.", "A pivot column adds one dimension to $\operatorname{Col}A$.", "A free column adds one free variable, one null direction." |
| 84–94 | The two bars slide together into one bar of five cells under a brace $n = 5$; $\operatorname{rank}A + \operatorname{nullity}A = n$ writes with $3 + 2 = 5$ | caption "Rank plus nullity always equals the number of columns." |
| 94–108 | Bars leave; orange row frames box the three nonzero rows, each holding one pivot; $\dim\operatorname{Row}A = \dim\operatorname{Col}A = 3$ writes | captions "Each pivot also sits in its own nonzero row.", "So the row space and column space share one dimension.", "Rows live in $\mathbb R^5$, columns in $\mathbb R^4$, yet counts match." |
| 108–122 | Two small matrices appear side by side with their tallies: a $3\times 3$ with three pivots (3 + 0) and a $2\times 4$ with two pivots (2 + 2) | captions "The same tally works for any shape.", "Two rows allow two pivots, so two columns must be free." |
| 122–132 | A nine-cell bar under "$7\times 9$": two cells fill pink, the other seven fill teal; $\operatorname{rank}A = 9 - 2 = 7$ | caption "A $7\times 9$ matrix with nullity 2 must have rank 7." |
| after the $6\times 9$ cross | Hold on the crossed-out bar | caption "Tomorrow this count ties together the tests for an inverse." (points to Day 19) |
| 135–144 | Takeaway card (the final render runs 143.9 s; the three motivation captions added 7 s, so rows after 8 s sit up to 7 s later than listed) | end |
