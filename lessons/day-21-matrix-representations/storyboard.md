# Day 21: The matrix of a linear transformation

Day 5 showed that a matrix's columns are where $\mathbf e_1$ and $\mathbf e_2$ land, and Day 15 turned polynomials
into coordinate columns with the basis $1, t, t^2$. Day 20 showed that $d/dt$ is linear. Today joins the three:
track where each basis vector lands, write the landing spot in coordinates, and stack those columns into a matrix.

The plane section reuses Day 5's map $T(\mathbf e_1) = (2, 1)$, $T(\mathbf e_2) = (-1, 1)$ with the blue moving
grid, green $\mathbf e_1$ and red $\mathbf e_2$. In the polynomial section the basis $1, t, t^2$ wears green, red
and blue (the weight colors of Day 15's widget), and column $j$ of every matrix keeps the color of basis vector $j$.
The test polynomial $\mathbf p$ is yellow and its derivative is teal.

| t (s) | State | Trigger |
|---|---|---|
| 0–6 | Title card "The matrix of a linear transformation", "Day 21" | start |
| 6–9 | Glowing origin, grid draws outward | after title |
| 9–20 | Green e₁ and red e₂ grow; the plane dims and the blue moving grid springs to T. Landing columns (2, 1) and (−1, 1) appear at the tips | captions "A linear map $T$ moves the whole plane." / "It is pinned down by where $\mathbf e_1$ and $\mathbf e_2$ land." |
| 20–27 | Panel "A = [? ?]" in the top-left; each landing column flies into its slot and glows | caption "Stack the landing spots as columns to get the standard matrix." |
| 27–38 | Walk: one green step and two red steps on the moved grid; the teal arrow T(x) = (0, 3) grows; the panel extends to A(1, 2) = (0, 3) | captions "$\mathbf x = \mathbf e_1 + 2\mathbf e_2$ lands on $T(\mathbf e_1) + 2\,T(\mathbf e_2)$." / "That sum is exactly $A\mathbf x$, so $A$ does everything $T$ does." |
| 38–42 | Plane clears | caption "Polynomials are not arrows, but they still have a basis." |
| 42–48 | Header $T = d/dt$ and $\mathcal B = \{1, t, t^2\}$ write at the top; two small graph windows, two gates ($d/dt$ and $[\cdot]_{\mathcal B}$) and an empty 3×3 frame with three faint column slots appear | caption "Build the matrix of $\tfrac{d}{dt}$ on $\mathbb P_2$ one column at a time." |
| 48–62 | **Centerpiece, column 1:** green 1 flies from the header into the input window; its flat curve slides through the d/dt gate and flattens onto the axis as 0; "T(1) = 0" logs below; zeros drop through the coordinate gate into a column, which flies into slot 1 | captions "A constant has slope 0, so $T(1) = 0$." / "Its coordinates are all zero, and that column goes in slot 1." |
| 62–72 | **Column 2:** red t becomes 1; the 1 lands in the top entry; the column flies into slot 2 | caption "The derivative of $t$ is $1$, with coordinates $(1, 0, 0)$." |
| 72–82 | **Column 3:** blue t² becomes 2t; the 2 lands in the middle entry; the column flies into slot 3; the finished matrix glows | caption "The derivative of $t^2$ is $2t$, with coordinates $(0, 2, 0)$." |
| 82–88 | Column 1 flashes | caption "Column 1 is all zeros because $T$ sends $1$ to $0$." |
| 88–94 | Pipeline clears; the matrix shrinks onto the bottom edge of a square diagram | caption "Now send $\mathbf p(t) = 3 + 5t - 2t^2$ along two routes." |
| 94–104 | Down, then across: p's coefficients drop into [p]_B = (3, 5, −2); each matrix row flashes and the teal entries 5, −4, 0 appear | caption "Down, then across: take coordinates, then multiply by $[T]_{\mathcal B}$." |
| 104–112 | Across, then down: p′(t) = 5 − 4t writes; its coefficients drop down onto the same teal column, which flashes with an orange ring | captions "Across, then down: differentiate first, then take coordinates." / "Both routes land on the same column." |
| 112–117 | Hold | caption "So $[T(\mathbf p)]_{\mathcal B} = [T]_{\mathcal B}[\mathbf p]_{\mathcal B}$ for every $\mathbf p$." |
| 117–128 | Square clears; the matrix returns large with column labels 1, t, t² and row labels. The bottom row fades, the frame shrinks to 2×3, and the name becomes $[T]_{\mathcal C\leftarrow\mathcal B}$ | captions "Every derivative here lies in $\mathbb P_1$, with basis $\mathcal C = \{1, t\}$." / "Columns follow the input basis and rows follow the output basis." |
| 128–136 | The general recipe and the standard matrix appear stacked | caption "With standard bases on $\mathbb R^n$, the recipe gives the standard matrix." |
| 136–144 | Takeaway card with origin pulse | end |
