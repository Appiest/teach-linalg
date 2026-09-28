# Day 29: Finding eigenvalues

Day 28 ended with $A - 2I$ squashing the plane flat for $A = \begin{bmatrix} 3 & -2 \\ 1 & 0 \end{bmatrix}$, and
with the promise that today finds eigenvalues of matrices that are not triangular. The video opens on that same
picture, with the same plane, colors and yellow line, and then asks for a test that needs no guessing.

After the recap the lesson switches to a new matrix $A = \begin{bmatrix} 1 & 2 \\ 2 & 1 \end{bmatrix}$ with columns
green and red. Its characteristic polynomial $\lambda^2 - 2\lambda - 3 = (\lambda - 3)(\lambda + 1)$ has well
separated roots, so between them the plane opens wide again, which Lay's Day 28 matrix (roots 1 and 2) cannot show.
Its eigen-directions keep Day 28's colors: yellow is $\mathbf v_1 = (1, 1)$ with $\lambda = 3$, and blue is
$\mathbf v_2 = (1, -1)$ with $\lambda = -1$. Because $(A - \lambda I)\mathbf v_1 = (3 - \lambda)\mathbf v_1$, the
yellow arrow shrinks along its own line and vanishes exactly at $\lambda = 3$, and the blue arrow does the same at
$\lambda = -1$. The image of the unit square under $A - \lambda I$ is filled teal when its signed area is positive
and pink when it is negative; that signed area is the value of the curve on the right. Orange is only for $\lambda$,
the moving dot and small marks.

Centerpiece layout: left, a 12 by 12 plane (0.53 units per step) showing the grid moved by $A - \lambda I$; right,
the graph of $p(\lambda) = \det(A - \lambda I)$ for $\lambda \in [-2.5, 4.5]$, whose horizontal axis is the number
line $\lambda$ slides along.

| t (s) | State | Trigger |
|---|---|---|
| 0–8 | Title card "Finding eigenvalues", "Day 29"; glowing origin; grid draws outward | start |
| 8–18 | Motivation. Day 28's $A$ in the top-left corner, yellow line $\lambda = 2$ and blue line $\lambda = 1$ with labels; the picture holds while the question is posed | captions "Yesterday's $A$ kept two lines, with $\lambda = 2$ and $\lambda = 1$." / "We could check each $\lambda$, but only after guessing it." / "Today we find every eigenvalue directly, with no guessing." |
| 18–30 | The grid moves from $I$ to $A - 2I$, squashes flat, and the yellow line shrinks into an orange ring at the origin. $\det(A - 2I) = 0$ lands in the corner panel and holds under the goal caption | captions "Then $A - 2I$ squashed the whole plane flat." / "A flat plane has area scale $\det(A - 2I) = 0$." / goal "The goal is an equation whose only unknown is $\lambda$." |
| 30–41 | Scrim. The chain builds line by line: $\lambda$ is an eigenvalue $\iff$ $(A - \lambda I)\mathbf x = \mathbf 0$ has a nonzero solution $\iff$ $A - \lambda I$ is not invertible $\iff$ $\det(A - \lambda I) = 0$. The last line glows | captions, one per line, then "This equation has only $\lambda$ in it, so nothing is guessed." |
| 41–58 | New $A = \begin{bmatrix} 1 & 2 \\ 2 & 1 \end{bmatrix}$; $A - \lambda I$ appears with glowing diagonal. $\det(A - \lambda I) = (1 - \lambda)^2 - 4 = \lambda^2 - 2\lambda - 3 = (\lambda - 3)(\lambda + 1)$ builds step by step; the polynomial is named | captions "Here is a new matrix, and we want its eigenvalues." / "Subtract $\lambda$ from each diagonal entry." / "Expand the $2 \times 2$ determinant as on Day 26." / "This is the \emph{characteristic polynomial} of $A$." / "Its roots are $3$ and $-1$." |
| 58–90 | **Centerpiece.** Scrim lifts onto the two panels; the polynomial moves above the graph. $\lambda$ starts at $-2$. It slides to $-1$: the grid squashes onto a line, the blue arrow shrinks into the origin, the blue line lights up with an orange ring, and the dot on the curve touches the axis where a blue mark lands. $\lambda$ sweeps on to $1$: the square flips pink and the curve dips below the axis. At $3$ the grid squashes again, the yellow line lights and a yellow mark lands on the axis. $\lambda$ springs to $4$ and the plane opens | captions "Slide $\lambda$ and watch what $A - \lambda I$ does to the plane." / "At $\lambda = -1$ the plane squashes flat." / "At that same moment the curve touches zero." / "In between, the square flips and its area turns negative." / "At $\lambda = 3$ the plane squashes flat again." / "Every other $\lambda$ leaves a real parallelogram." |
| 90–101 | The graph fades; a panel shows $[\,A - 3I \mid \mathbf 0\,] \sim \begin{bmatrix} 1 & -1 & 0 \\ 0 & 0 & 0 \end{bmatrix}$, so $\mathbf x = x_2(1, 1)$ in yellow, and $A + I$ gives $\mathbf x = x_2(1, -1)$ in blue | captions "The line that lands on $\mathbf 0$ holds the eigenvectors." / "Row reduce $A - \lambda I$ for each root to find them." |
| 101–117 | Scrim. $M = \begin{bmatrix} 4 & 0 & 0 \\ -3 & 1 & 2 \\ 2 & 0 & 3 \end{bmatrix}$ (a fresh matrix in the style of Lay §5.2 #11), then $M - \lambda I$. Row 1 is boxed and its two zeros turn gray. Expansion along row 1 gives $(4 - \lambda)\det\begin{bmatrix} 1 - \lambda & 2 \\ 0 & 3 - \lambda \end{bmatrix} = (4 - \lambda)(1 - \lambda)(3 - \lambda)$, and the roots $4, 1, 3$ drop out | captions "A $3 \times 3$ matrix gives a polynomial of degree 3." / "Row 1 has two zeros, so only one term survives." / "The minor is triangular, so its determinant is its diagonal." / "Leave it factored and read off the three roots." |
| 117–130 | Triangular $B$ with diagonal $2, 2, 4$; $\det(B - \lambda I) = (2 - \lambda)^2(4 - \lambda)$. Its graph touches the axis at $2$ without crossing and crosses at $4$. A mark at $2$ reads "multiplicity 2", and the graph holds under the forward pointer | captions "Here the factor $2 - \lambda$ appears twice." / "So $\lambda = 2$ has \emph{algebraic multiplicity} 2." / "Day 31 asks whether a double root gives two eigenvectors." |
| 130–139 | Takeaway card with origin pulse | end |
