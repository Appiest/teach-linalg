# Day 40: The singular value decomposition

The video uses $A = \begin{bmatrix} 2 & -1 \\ 2 & 2 \end{bmatrix}$ with its columns green and red as on Day 5. Its SVD has
clean numbers: $A^TA = \begin{bmatrix} 8 & 2 \\ 2 & 5 \end{bmatrix}$ has eigenvalues $9$ and $4$, so $\sigma_1 = 3$ and
$\sigma_2 = 2$. The right singular vectors are $\mathbf v_1 = (2, 1)/\sqrt5$ (yellow) and $\mathbf v_2 = (-1, 2)/\sqrt5$ (blue),
and the left ones are $\mathbf u_1 = (1, 2)/\sqrt5$ and $\mathbf u_2 = (-2, 1)/\sqrt5$, in the same colors because each
$\mathbf v_i$ is carried onto $\sigma_i\mathbf u_i$. $V^T$ is a turn by $-26.6°$ and $U$ is a turn by $63.4°$, so neither
factor reflects. Singular values are orange, like Day 32's eigenvalues. The unit circle is teal with a faint fill. The plane
sits right of centre at 1.1 scene units per step, so the ellipse (extents $\pm\sqrt5$ across and $\pm\sqrt8$ up) fills the
height of the frame, and the factor panel lives in the top left.

The moving grid and circle are drawn from one `LiveTransform`, so $A$, its undo, and the three factors each play as one
continuous motion. Rotations turn through their angle, so the grid never shrinks on the way.

| t (s) | State | Trigger |
|---|---|---|
| 0–9 | Title card "The singular value decomposition", "Day 40"; glowing origin; grid draws | start |
| 9–22 | $A$ panel top left. Teal unit circle draws. The grid and circle move by $A$ into a tilted ellipse. A muted copy of the unit circle stays behind | captions "Here is a matrix $A$ and the unit circle." / "$A$ turns the circle into a tilted ellipse." |
| 22–42 | A gray unit input $\mathbf x$ sweeps around the circle while the teal $A\mathbf x$ traces the ellipse and a live readout of $\lVert A\mathbf x\rVert$ changes. It settles on the longest output: $\mathbf x$ becomes yellow $\mathbf v_1$, the output is $3\mathbf u_1$. Blue $\mathbf v_2$ and its output $2\mathbf u_2$ appear; a small orange right-angle mark sits between the outputs | captions "Which unit input gets stretched the most?" / "The longest output comes from the input $\mathbf v_1$." / "Its length $\sigma_1 = 3$ is the first \emph{singular value}." / "At right angles, $\mathbf v_2$ gets the shortest output, $\sigma_2 = 2$." / "The two outputs are perpendicular too." |
| 42–46 | Sweep items leave; the grid springs back to the square grid and the ellipse shrinks to the circle, with $\mathbf v_1$, $\mathbf v_2$ on it | caption "Undo $A$ and split it into three simpler moves." |
| 46–74 | **Centerpiece.** Factor panel $A = U\Sigma V^T$ replaces the $A$ panel, with $V^T$'s rows and $U$'s columns yellow and blue and $\Sigma$'s diagonal orange. An orange box sits on $V^T$: the grid turns, the circle looks unchanged, and $\mathbf v_1, \mathbf v_2$ land on the axes. Box moves to $\Sigma$: the circle stretches 3 across and 2 up into an upright ellipse. Box moves to $U$: the ellipse turns so its axes are $\sigma_1\mathbf u_1$ and $\sigma_2\mathbf u_2$, which get labels. A dashed outline of one step of $A$ draws over it and matches exactly | captions "$V^T$ turns $\mathbf v_1$ and $\mathbf v_2$ onto the axes." / "The circle looks the same, but its arrows moved." / "$\Sigma$ stretches the axes by $\sigma_1 = 3$ and $\sigma_2 = 2$." / "$U$ turns the axes onto $\mathbf u_1$ and $\mathbf u_2$." / "One step of $A$ draws exactly the same ellipse." / "Every matrix works this way: turn, stretch, turn." |
| 74–88 | Scrim. Board: $\lVert A\mathbf x\rVert^2 = \mathbf x^T(A^TA)\mathbf x$; $A^TA = \begin{bmatrix} 8 & 2 \\ 2 & 5\end{bmatrix}$ with $\lambda = 9, 4$; $\sigma_1 = \sqrt9 = 3$, $\sigma_2 = \sqrt4 = 2$; $\mathbf u_i = A\mathbf v_i/\sigma_i$ | captions "The stretches come from the symmetric matrix $A^TA$." / "Its eigenvalues are 9 and 4, with eigenvectors $\mathbf v_1$ and $\mathbf v_2$." / "The singular values are their square roots, 3 and 2." / "Each $\mathbf u_i$ is $A\mathbf v_i$ divided by $\sigma_i$." |
| 88–93 | Board: $A = \sigma_1\mathbf u_1\mathbf v_1^T + \sigma_2\mathbf u_2\mathbf v_2^T$ | caption "Written out, $A$ is a sum of rank-one layers." |
| 93–120 | A 90 × 135 picture (drawn by code) fills the right side. Left: bars of its first 30 singular values on a log scale, a $k$ readout and a storage count. $k$ steps 1, 2, 5, 20, each after its caption: the picture is rebuilt from the first $k$ layers, the kept bars turn teal, and the storage count updates | captions "A grayscale picture is a matrix of brightness values." / "Keep only the first $k$ layers to get a rank-$k$ copy." / "One layer gets only rough bands of light and dark." / "A second layer starts to find the sun." / "Five layers already show the sun and the hills." / "Twenty layers look almost exactly like the original." / "Rank 20 stores 4,520 numbers instead of 12,150." |
| 120–130 | Closing card: takeaway and one line for the whole course, with origin pulse | end |
