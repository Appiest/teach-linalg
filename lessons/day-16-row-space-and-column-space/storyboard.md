# Day 16: Column space and row space

Day 5 drew a matrix as a machine that moves the plane, with $\mathbf e_1$ green, $\mathbf e_2$ red, a matrix's
first column green and its second red, the input $\mathbf x$ yellow and every output teal. Today keeps those
colors and gives the machine a $3\times 2$ matrix, so its outputs live in $\mathbb R^3$.

The matrix is $A = \begin{bmatrix}1&0\\0&1\\1&1\end{bmatrix}$ with columns $\mathbf a_1 = (1, 0, 1)$ and
$\mathbf a_2 = (0, 1, 1)$. Its column space is the plane $z = x + y$. The guide suggests
$\begin{bmatrix}1&2\\0&1\\2&3\end{bmatrix}$, but its plane is steep ($z = 2x - y$) and the image of even a small
input square runs off the top of the panel, so this lesson uses a gentler matrix with the same shape of story.
The guide's matrix appears in the first practice check instead.

Layout: the input plane $\mathbb R^2$ sits on the left at 0.55 scale. The right panel draws $\mathbb R^3$ through
an oblique view (`OrbitingView` in `engine/theme.py`) with a faint floor grid. The view's azimuth lives in a
`ValueTracker`, and everything in the right panel redraws from it, so the camera can orbit. At azimuth 60° the
plane faces the viewer; at about 120° (with 20° elevation) the view lies inside the plane and the plane collapses
to a line.

The third column $\mathbf a_3 = (-1, 1, 0) = -\mathbf a_1 + \mathbf a_2$ is pink. The test points
$\mathbf b = (1, -1, 0)$ and $\mathbf c = (1, 1, 0)$ are yellow, like any vector we ask a question about.

| t (s) | State | Trigger |
|---|---|---|
| 0–6 | Title card "Column space and row space", "Day 16" | start |
| 6–9 | Glowing origin on the left input plane; the input grid draws | after title |
| 9–15 | $A$ writes top left with its first column green and second red; the 3D axes, floor, $\mathbb R^2$, $\mathbb R^3$ tags and $\mathbf x \mapsto A\mathbf x$ appear | caption "This $3\times 2$ matrix sends vectors in $\mathbb R^2$ to $\mathbb R^3$." |
| 15–24 | $\mathbf e_1$ grows on the left; column 1 of $A$ flashes; the green arrow $\mathbf a_1$ grows in 3D. Same for $\mathbf e_2$ and red $\mathbf a_2$ | caption "Each basis vector lands on a column of $A$." |
| 24–31 | Yellow $\mathbf x = (1, 1)$ on the left; a copy of $\mathbf a_2$ slides tip to tail onto $\mathbf a_1$; teal $A\mathbf x$ grows | caption "Any input $\mathbf x$ lands at $x_1\mathbf a_1 + x_2\mathbf a_2$." |
| 31–42 | **Centerpiece:** a teal square of input grid lines draws; copies fly across and land as teal lines in 3D; a teal sheet fades in; $\mathbf x$ springs around and $A\mathbf x$ rides the sheet | caption "Send every input across and the outputs paint a plane." |
| 42–54 | Label $\operatorname{Col}A$ appears by the sheet; $\operatorname{Col}A = \operatorname{Span}\{\mathbf a_1, \mathbf a_2\} = \{A\mathbf x\}$ writes top right | captions "That tilted plane is the column space of $A$.", "It is the span of the columns, everything $A$ can output." |
| 54–66 | Yellow $\mathbf b = (1, -1, 0)$ appears; $[A\ \mathbf b]$ row reduces in place to a consistent system; the input springs to $(1, -1)$ and $A\mathbf x$ lands on $\mathbf b$; an orange ring marks it | captions "Is $\mathbf b = (1, -1, 0)$ an output? Row reduce $[A\ \mathbf b]$.", "No row says $0 = $ something else, so a solution exists.", "The input $(1, -1)$ lands on $\mathbf b$, so $\mathbf b$ is in $\operatorname{Col}A$." |
| 66–78 | Yellow $\mathbf c = (1, 1, 0)$; $[A\ \mathbf c]$ reduces to a last row $0\ 0 \mid -2$; a dashed orange line rises from $\mathbf c$ to the sheet | captions "Now try $\mathbf c = (1, 1, 0)$.", "The last row says $0 = -2$, so no input reaches $\mathbf c$." |
| 78–88 | The camera orbits until the sheet is edge on and collapses to a line; $\mathbf b$ sits on the line and $\mathbf c$ is off it; the camera orbits back | captions "Turn to see it edge on: the plane is perfectly flat.", "$\mathbf b$ sits on it, and $\mathbf c$ floats off it." |
| 88–96 | $A$ gains a pink third column; $\mathbf a_3 = (-1, 1, 0)$ grows inside the sheet | captions "Give $A$ a third column that already lies in the plane.", "The span is the same plane, so one column is redundant." |
| 96–108 | The input plane leaves; a copy of $A$ row reduces below it in two steps; orange frames mark pivot columns 1 and 2; column 3 of the reduced form flashes | captions "Row reduce $A$ to find its pivot columns.", "Columns 1 and 2 hold the pivots.", "Column 3 of the reduced form reads $-1$ and $1$." |
| 108–118 | $\mathbf a_3 = -\mathbf a_1 + \mathbf a_2$ writes; in 3D, $-\mathbf a_1$ then $\mathbf a_2$ tip to tail land on the tip of $\mathbf a_3$; orange ring | captions "Row operations keep that recipe, so it holds for $A$ too.", "So the pivot columns of $A$ are a basis for $\operatorname{Col}A$." |
| 118–130 | Gray arrows for the reduced columns $(1, 0, 0)$ and $(0, 1, 0)$ fly out of the reduced matrix; the camera turns edge on and they stick out of the plane; it turns back | captions "Take them from $A$ itself: reduced columns can leave the plane.", "Edge on, the reduced columns stick out of the plane." |
| 130–138 | $B$ with rows $(1, 0, 1)$ green and $(1, 1, 2)$ red replaces $A$; the red row arrow grows; $\operatorname{Row}B = \operatorname{Span}\{\mathbf r_1, \mathbf r_2\}$ replaces the Col A formula | captions "Now make two vectors in the plane the rows of $B$.", "Their span, the row space of $B$, is the same plane." |
| 138–150 | $R_2 \leftarrow R_2 - R_1$: the red row slides to $(0, 1, 1)$ inside the sheet while the entries crossfade; orange frames mark both rows | captions "A row operation slides a row but never leaves the plane.", "Each new row mixes old rows, and the step can be undone.", "So the nonzero rows of an echelon form are a basis." |
| 150–158 | Takeaway card | end |
