# Day 3: Systems of equations and row reduction

Running example (Lay §1.1, p. 3): $x_1 - 2x_2 = -1$ (yellow line) and $-x_1 + 3x_2 = 3$ (blue line), crossing at
$(3, 2)$, which is Day 1's $\vec v$. Row 1 of every matrix is yellow and row 2 is blue, so each row is tied to its
line. The solution set is teal (a point, a line, or nothing); pivots and small marks are glow orange.

| t (s) | State | Trigger |
|---|---|---|
| 0–9 | Title card "Systems of equations and row reduction", "Day 3"; origin pulse; grid draws | start |
| 9–15 | The two equations write in, top left, tinted yellow and blue | caption "A linear system is equations that share the same unknowns." |
| 15–21 | Yellow line draws, then blue line draws | caption "Every point on a line satisfies that line's equation." |
| 21–26 | Teal dot springs in at (3, 2) with its coordinates | caption "A solution satisfies both, so it sits where they cross." |
| 26–33 | Blue line springs parallel ($-x_1 + 2x_2 = 3$), its equation morphs, dot fades | caption "Parallel lines never meet, so there is no solution." |
| 33–40 | Blue line slides onto the yellow one ($-x_1 + 2x_2 = 1$); a thick teal line draws over both | caption "The same line twice gives infinitely many solutions." |
| 40–46 | Teal line fades, blue line springs back, dot returns | caption "Lines that cross give exactly one solution." |
| 46–56 | Bar and brackets appear; each equation's numbers fly into its matrix row; rows flash for the size | captions "Keeping only the numbers gives the augmented matrix." / "It has 2 rows and 3 columns, so it is 2 × 3." |
| 56–66 | Equations fade, matrix springs to the corner; card lists the three operations and their undo, undo column flashes | captions "Three row operations change a matrix." / "Each one can be undone by an operation of the same kind." |
| 66–72 | Interchange: rows swap along an arc and back; lines unchanged | caption "Swapping two rows only changes the order of the equations." |
| 72–80 | Scaling: row 2 becomes $[-2\ 6 \mid 6]$, a flash runs along the unmoved blue line, then halves back | caption "Scaling a row changes its numbers but not its line." |
| 80–92 | **Centerpiece.** $R_2 \leftarrow R_2 + R_1$: row 1 flashes, row 2 morphs to $[0\ 1 \mid 2]$ while the blue line pivots about the teal dot to horizontal; the dot flashes | captions "A replacement adds a multiple of one row to another." / "The blue line turns, but the crossing point never moves." |
| 92–99 | $R_1 \leftarrow R_1 + 2R_2$: row 1 morphs to $[1\ 0 \mid 3]$ while the yellow line pivots to vertical | caption "Add two copies of row 2 to row 1." |
| 99–106 | Rows fly out as $x_1 = 3$ and $x_2 = 2$ labels on the two lines | caption "Now each row reads off one unknown: $x_1 = 3$, $x_2 = 2$." |
| 106–120 | Parallel system returns; $R_2 \leftarrow R_2 + R_1$ sends the blue line accelerating off screen as row 2 becomes $[0\ 0 \mid 2]$; glow ring on that row | captions "Try the same move on the parallel lines." / "The row $[0\ 0 \mid 2]$ says $0 = 2$, so nothing solves it." |
| 120–128 | Plane fades; a 3×5 augmented matrix with $x_1..x_4$ column names steps through two replacements | caption "Bigger systems use the same moves, one column at a time." |
| 128–132 | Glow staircase draws under the leading entries | caption "In echelon form, each leading entry sits right of the one above." |
| 132–137 | $R_1 \leftarrow R_1 - 3R_2$ gives reduced form; pivots boxed in glow | caption "In reduced form, each pivot is 1 and alone in its column." |
| 137–146 | "free" tags over columns 2 and 4; general solution writes in beside the matrix | captions "Columns without a pivot belong to free variables." / "Choose any free values and the other unknowns follow." |
| 146–151 | Takeaway card with origin pulse | end |
